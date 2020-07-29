# -*- coding: utf-8 -*-
# TODO: improve readability of function and variable names
"""
Functions and utilities for handling xarray objects
"""
# stdlib imports
import csv
import re

# third party imports
import xarray as xr
import numpy as np
import pandas as pd
import itertools

from ._tools import find_nearest

# Utilities to generally alter coordinates
def regex_coords(
        da,
        dim,
        regex_dict
):
    """
    TODO: improve documentation
    takes coordinates made of strings and and splits into new dimensions based on regex_dict
    i.e. coordinates would be test3_power5_run2 and one could extract the numbers into 3 dimensions (test#, power#, run#)

    Parameters
    ----------
    da : xr.DataArray
    dim
    regex_dict : dict

    Returns
    -------
    da : xr.DataArray
    """
    das = []
    for coord in da.coords[dim].values:
        name = da.name
        da_sel = da.sel({dim: coord}).drop(dim)

        for new_dim in regex_dict:
            regex = regex_dict[new_dim]
            m = re.search(regex, coord)
            da_sel = da_sel.assign_coords(temp=m.groups()[0]).\
                expand_dims('temp').rename({'temp': new_dim})
        da_sel.name = name
        das.append(da_sel)

    ds = xr.merge(das)
    da = ds[name]

    return da


def drop_single_coords(da):
    """
    drops all dimensions if there is only a single coordinate

    Parameters
    ----------
    da : xr.DataArray

    Returns
    -------
    da : xr.DataArray
    """
    # import pdb; pdb.set_trace()
    for coord in da.coords:
        if coord in da.dims:
            if len(da.coords[coord].values) == 1:
                print('Found only one value for coords '+ coord +' Dropping')
                da = da.isel({coord: 0}).drop(coord)
        else:
            print('Coordinate  '+ coord +' had no corresponding dimension, dropping')
            da = da.drop(coord)
            
    return da


def str2num_coords(
        da,
        dims=None,
        numtype='float'
):
    """
    convert the indexes of a data array to floats. cannot figure out how to not
    affect the original array so this does not return a value.
    TODO: implement da.copy() to avoid affecting the original array

    Parameters
    ----------
    da : xr.DataArray
    dims : Union[iterable, None]
        dims to iterate over, if none convert all indexes
    numtype : str
        TODO: is there a reason this is a string instead of an actual dtype?
    """

    if dims is None:
        dims = da.dims

    for dim in dims:
        cds = da.coords[dim].values
        if numtype == 'float':
            cds = [float(cd) for cd in cds]
        elif numtype == 'int':
            cds = [int(cd) for cd in cds]

        da.coords[dim] = cds

    return da


# General
def gen_seldicts(
        da,
        dims=None,
        check_empty=True,
        unstack=True
):
    """
    TODO: improve documentation
    generates a list of dictionaries to be passed into dataarray selection
    functions.

    Parameters
    ----------
    da : xr.DataArray
        datarray to generate selection dicts for
    dims
        dimensions to generate seldicts over, if None then use all dimensions
    check_empty : bool
        only generate seldicts that give values that are not all nan
    unstack : if 
    Returns
    -------
    seldicts : List[Dict]
    """
    if unstack:
        #unstacks in case of multiindex. using unstacked seldict on stacked multindex da seems to work
        da = da.unstack() 

    if dims is None:
        dims = list(da.dims)

    idxs = {dim: da.indexes[dim] for dim in dims}

    seldicts = [dict(zip(idxs, x)) for x in itertools.product(*idxs.values())]

    seldicts_red = []
    if check_empty:
        # checks to see if the seldict produces all nans and only appends the
        # seldict to the list if that is not true
        for i, seldict in enumerate(seldicts):
            sel = da.sel(seldict).values

            t = (sel != sel)  # test for nan

            if type(t) == np.ndarray:
                t = t.all()

            if not t:
                seldicts_red.append(seldict)

        seldicts = seldicts_red

    return seldicts

def removelatex(string):
    """
    Remove the latex $ symbols from a unit string

    Parameters
    ----------
    string : str
        String containing latex math mode $ delimiters

    Returns
    -------
    string : str
        Input string with $ delimiters removed
    """
    if '$' in string:
        string = string.replace('$', '')
    if '\\' in string:
        string = string.replace('\\', '')
    return string


def writeunitsrowcsv(
        ds,
        path
):
    """
    Writes the units in a dataset to the first row of a csv file

    Parameters
    ----------
    ds : xr.DataArray
        DataArray of data to append
    path : str
        Path of .csv to append data into
    """

    df = pd.read_csv(path)
    coords = df.columns[0:1]
    data_vars = df.columns[1:]
    
    coordunits = []
    coordnames = []
    for c in coords:
        if 'units' in ds.coords[c].attrs:
            coordunits.append(removelatex(ds.coords[c].units))
        else:
            coordunits.append(np.nan)
            
        if 'long_name' in ds.coords[c].attrs:
            coordnames.append(ds.coords[c].long_name)
        else:
            coordnames.append(ds.coords[c].name)

    varunits = []
    varnames = []
    for v in data_vars:
        if 'units' in ds[v].attrs:
            varunits.append(removelatex(ds[v].units))
        else:
            varunits.append(np.nan)
        
        if 'long_name' in ds[v].attrs:
            varnames.append(ds[v].long_name)
        else:
            varnames.append(ds[v].name)

    unitsrow = [*coordunits, *varunits]
    namerow = [*coordnames, *varnames]

    with open(path, "r") as infile:
        reader = list(csv.reader(infile))
        reader.insert(1, namerow)
        reader.insert(2, unitsrow)

    with open(path, "w", newline='') as outfile:
        writer = csv.writer(outfile)
        for i, line in enumerate(reader):
            if i != 0:  # get rid of short name
                writer.writerow(line)


from scipy import optimize

def fit_da(da_data, fit_fn, fitdim, xs, p0, bounds, p_labels):
    """
    Fits 1D cross sections along fitdim in da_data with fit function fit_fn. The
    other coordinates are iterated through using gen_seldicts. This program uses
    scipy.optimize.curve_fit directly, see fit_da_lmfit for using lmfit models.
    """
    da_data = da_data.dropna(fitdim,'all')
    fits = da_data.copy(deep = True).where(False).interp({fitdim: xs})
    # xs = da_data.coords[fitdim]

    da_p = da_data.mean(fitdim).where(False).copy()
    ds_p = xr.Dataset({p : da_p for p in p_labels}).copy(deep=True)
    ds_p_cov = ds_p.copy(deep=True)
    seldicts = gen_seldicts(ds_p)

    for seldict in seldicts:
        da = da_data.sel(seldict).dropna(fitdim,'all')

        if len(da.coords[fitdim]) > 1:
            xs_data = da.coords[fitdim]
            popt, pcov = optimize.curve_fit(fit_fn,xs_data,da.data, p0 = p0, bounds = bounds) #had to make initial nK guess large for correct high seed fit...
            perr = np.sqrt(np.diag(pcov))
            for i in range(len(p_labels)):
                var = list(ds_p.data_vars)[i]
                ds_p[var].loc[seldict] = popt[i]
                ds_p_cov[var].loc[seldict] = perr[i]

            fits.loc[seldict] = fit_fn(xs, *popt)
            
    return fits, ds_p, ds_p_cov

def fit_da_lmfit(da_data, model, params, fitdim, xs_eval):
    """
    Fits 1D cross sections along fitdim in da_data with a lmfit model and
    initial parameters 'params'. The other coordinates are iterated through
    using gen_seldicts. The final output fits are evaluated at x coordinates
    xs_eval. To interact with scipy.optimize directly see 'fit_da' 
    """
    
    da_data = da_data.dropna(fitdim,'all')
    
    fits = da_data.copy(deep = True).where(False).interp({fitdim: xs_eval})
    fits.name = 'fits'
    da_p = da_data.mean(fitdim).where(False).copy()
    ds_p = xr.Dataset({par : da_p for par in params}).copy(deep=True)
    ds_p_stderr = ds_p.copy(deep=True)
    
    seldicts = gen_seldicts(ds_p)

    for seldict in seldicts:
        da = da_data.sel(seldict).dropna(fitdim,'all')

        if len(da.coords[fitdim]) > 1:
            xs_data = da.coords[fitdim]
            out = model.fit(da.data, params, x=xs_data)

            for par in out.params:
                ds_p[par].loc[seldict] = out.params[par].value
                ds_p_stderr[par].loc[seldict] = out.params[par].stderr

            fits.loc[seldict] = out.eval(x=xs_eval)
            
    return fits, ds_p, ds_p_stderr


def coordstr_1D(da_ct):
    """
    Note: outdated, you should stack your coordinates into a multindex instead. 
    This generates a one-dimensonal datarray of strings (da_ct_str) for each test case like "tf9.5sr0.01". 
    This way one can plot multidimensonal test cases easily along one dimension
    """
    das = []
    seldicts = gen_seldicts(da_ct)

    for seldict in seldicts:
        ct = da_ct.sel(seldict).item()
        coordstr = ''
        for dim in seldict:
            coordstr = coordstr + dim + str(seldict[dim]) + '_'
        coordstr = coordstr[0:-1]    
        das.append(xr.DataArray([ct], coords = {'coordstr': [coordstr]}, dims = ['coordstr']))
    da_ct_str = xr.concat(das,'coordstr')
    
    return da_ct_str


def fix_coord_grid(da, coord, grid_values, keep_attrs=False):

    da_out = da.copy(deep=True)
    
    print('Fixing coord ' + coord + ' to grid values ' + str(grid_values))
    print('             ---Old Coords---')
    print(da.coords[coord].values)
        
    coords_actual = da.coords[coord].values
    coords_grid = [grid_values[find_nearest(grid_values, crd)] for crd in coords_actual]

    print('             ---New Coords---')
    print(coords_grid)

    
    #not sure if this is a perfect condition
    if len(da_out.indexes) == 0:
        #assign to values to remain compatible with da_ct before setting index (cannot do this with a multindex)
        da_out.coords[coord].values = coords_grid
    else:
        #This works for da with actual dims and coords
        da_out = da_out.assign_coords({coord:coords_grid})

    if keep_attrs:
        da_out.coords[coord].attrs = da.coords[coord].attrs

    return da_out


from scipy.stats import binned_statistic

def fix_coord_grid_bins(da, bin_dim, bins, round_value=None, keep_attrs=False):
    raw_coords = da.coords[bin_dim].values
    bin_means, bin_edges, binnumber = binned_statistic(raw_coords, raw_coords, 'mean', bins)
    bin_means = bin_means[~np.isnan(bin_means)]

    if round_value is not None:
        bin_means = [round(val, round_value) for val in bin_means]

    da = fix_coord_grid(da, bin_dim,  bin_means, keep_attrs)
    return da

def calc_stats(ds,  stat_dim='time'):
    """
    Calculates over a given dimension (stat_dim) and returns a dataset with a new statistic dimension (mean, std, etc.)
    Currrently skew is not included, messes with units. 
    """
    mean = ds.mean(stat_dim,keep_attrs = True).assign_coords(stat = 'mean')
    std = ds.std(stat_dim,keep_attrs = True).assign_coords(stat = 'std')

#     #skew messes with units...may want to separate
#     skew = ds.apply(stats.skew,nan_policy = 'omit',keep_attrs = True).assign_coords(stat = 'skew').assign_coords(case=case).expand_dims('case')
    
    ds = xr.concat([mean,std], dim = 'stat')
    
    return ds

def bin_da(da, bin_dim, bins, reset_coords_midpoint=True, min_points=None, dropna = False):
    """
    Custom utility function for binning dataarray along a coordinate and returning the mean and standard devaition.
    groups coodinates along 'bin_dim' into 'bins'.
    'bins' is passed directly into groupby_bins, i.e. can be a int for fixed number of bins
    If reset_coords_midpoint is True, the coords will be reset to the midpoint of the bin interval and attribues restored
    if min_points is specified, bins that include less than min_points will be dropped. 

    returns: da_mean, da_std
    """
    da_gb = da.groupby_bins(bin_dim, bins)

    da_mean = da_gb.apply(calc_bins_mean, bin_dim = bin_dim, min_points=min_points)
    if reset_coords_midpoint:
        da_mean = reset_bins(da_mean, bin_dim)
        da_mean.coords[bin_dim].attrs = da.coords[bin_dim].attrs
        if dropna: da_mean = da_mean.dropna(bin_dim,'all')

    da_std = da_gb.apply(calc_bins_std, bin_dim = bin_dim, min_points=min_points)
    if reset_coords_midpoint:
        da_std = reset_bins(da_std, bin_dim)
        da_std.coords[bin_dim].attrs = da.coords[bin_dim].attrs
        if dropna: da_std = da_std.dropna(bin_dim,'all')

    return da_mean, da_std

def reset_bins(da, bin_dim):
    """resets binned coordinates to midpoint and resets dim name. bin_dim is original dimension name"""
    bin_dim_name = bin_dim + '_bins'
    da = da.rename({bin_dim_name: bin_dim})
    da.coords[bin_dim] = [interval.mid for interval in da.coords[bin_dim].values]
    return da
    

def calc_bins_mean(da, bin_dim, min_points = None):
    if min_points is None:
        return da.mean(bin_dim, keep_attrs=True)
    else:
        l = len(da.coords[bin_dim])
        if l > min_points:
            return da.mean(bin_dim, keep_attrs=True)
        else:
            return da.where(False).isel({bin_dim:0}).drop(bin_dim)
    
def calc_bins_std(da, bin_dim,  min_points = None):
    if min_points is None:
        return da.std(bin_dim, keep_attrs=True)
    else:
        l = len(da.coords[bin_dim])
        if l > min_points:
            return da.std(bin_dim, keep_attrs=True)
        else:
            return da.where(False).isel({bin_dim:0}).drop(bin_dim)