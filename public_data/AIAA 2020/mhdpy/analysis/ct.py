# -*- coding: utf-8 -*-

"""
Utilities for dealing with 'cuttimes', or time intervals related to certain test cases
most of these functions generatre or work with a DataArray of cuttimes (da_ct)
the da_ct is a series of slice object that are indexed by the experimental parameters of interest during those windows of time (e.g. total flow, seed rate, etc.)
"""

import pandas as pd
import xarray as xr

from .xr import gen_seldicts, drop_single_coords

# utilities to Generating indexed cuttimes (da_ct) and alter other data arrays based on da_ct 

def gen_da_ct_data(cuttimes, dim_dict):    
    """
    index cuttimes based on the mean of data within the time range
    """

    #for each cuttime get a combination of coordinates
    #combos may be obsolete with separate 'set_measnum' function
    combos = []
    for sl in cuttimes:
        combo = []
        for dim in dim_dict:
            data = dim_dict[dim]['data']
            val = data.sel(time=sl).mean('time').item()
            
            if 'round_value' in dim_dict[dim]:
                val = round(val, dim_dict[dim]['round_value'])
            
            # d[dim].append(val)
            combo.append(val)
        combos.append(combo)
    
    dims = list(dim_dict.keys())
    combos = [tuple(combo) for combo in combos]

    #generated multindexed dataarray    
    coords = {}
    for i in range(len(dims)):
        dim = dims[i]
        coords[dim] = ('ct', list((c[i] for c in combos)))

    
    da_ct = xr.DataArray(cuttimes,
        coords=coords,
        dims = ('ct')
        )

    # add attributes to each coordinate from the datasets
    for coord in da_ct.coords:
        da_ct.coords[coord].attrs = dict()
        if coord in dim_dict:
            data = dim_dict[coord]['data'] 
            if 'long_name' in data.attrs:
                da_ct.coords[coord].attrs['long_name'] = data.attrs['long_name']
            if 'units' in data.attrs:
                da_ct.coords[coord].attrs['units'] = data.attrs['units']
    
    return da_ct

def _checkIfDuplicates(listOfElems):
    ''' Check if given list contains any duplicates '''    
    for elem in listOfElems:
        if listOfElems.count(elem) > 1:
            return True
    return False


def assign_tc_general(da, da_ct, timeindex='time'):
    """
    assigns the general coords in da_ct to da
    Can handle a stacked da_ct, but assumes that there is only one stacked dimension
    """

    if type(da) == xr.core.dataarray.DataArray:
        isdataarray = True
        if da.name == None:
            print("Recieved datarray with no name, giving dummy name")
            da.name = "dummy_name"
    else:
        isdataarray=False

    seldicts = gen_seldicts(da_ct)

    firstdim = da_ct.dims[0]
    firstindex = da_ct.indexes[firstdim]

    if type(firstindex) == pd.core.indexes.multi.MultiIndex:
        """This is a multiindexed dataarray, so restack at the end"""
        stacked = True
    else:
        stacked = False
    
    das = []
    for seldict in seldicts:
        sl = da_ct.sel(seldict).item()

        d = {timeindex: sl}

        da_sel = da.sel(d).dropna(timeindex, 'all')

        for dim in seldict:
            coord = seldict[dim]
            da_sel = da_sel.assign_coords(temp=coord).rename({'temp': dim}).expand_dims(dim)

        das.append(da_sel)

    #Changed this to be merge vs concatentate. Concatenate was giving assertion errors.
    #Believe this is actually accurate as each dataarray has totally different coordinates (time and assigned coordinates)
    ds = xr.merge(das)

    for cd in da_ct.unstack().coords:
        #note that running unstack on a unstacked datarray should do nothing
        attrs = da_ct.coords[cd].attrs
        ds.coords[cd].attrs = attrs

    if stacked:
        ds = ds.stack({firstdim: firstindex.names}).dropna(firstdim, 'all')
        ds.coords[firstdim].attrs = da_ct.coords[firstdim].attrs

    if isdataarray:
        #If a datarray was passed in, convert back (merge would have converted to dataset)
        ds = ds[list(ds.data_vars)[0]]

    return ds

def assign_measnum(da_ct):
    combos = []
    for i in da_ct.coords['ct']:
        da= da_ct.sel(ct=i.item())
        combos.append(tuple(da.coords[c].item() for c in da.coords))

    dims = list(da.coords)
    unique_combos = set(combos)
    if len(unique_combos) < len(combos):
        print('duplicated coordinate combinations. adding measnum')
        dims.append('mnum')
        for c_u in unique_combos:
            j=0
            for i in range(len(combos)):
                if combos[i] == c_u:
                    combos[i] = tuple((*combos[i],j))
                    j=j+1

    coords = {}
    for i in range(len(dims)):
        dim = dims[i]
        coords[dim] = ('ct', list((c[i] for c in combos)))
        
    da_ct_new = da_ct.assign_coords(coords)

    for coord in da_ct.coords:
        da_ct_new.coords[coord].attrs = da_ct.coords[coord].attrs

    return da_ct_new

def set_index_da_ct(da):
    """Stacks all coordinates into one multindex and automatically generates a long_name"""

    coordnames = list(da.coords)
    da_stacked = da.set_index(ct=coordnames)

    if len(coordnames) == 1:
        #only one coordinate just rename ct to the coordinate name
        da_unstacked = da_stacked.rename(ct=coordnames[0])
    else:
        #generate multindex
        long_name_string = 'Test Case ('
        for coord in da.coords:
            if 'long_name' in da.coords[coord].attrs:
                long_name_string = long_name_string + da.coords[coord].attrs['long_name'] + ', '
            else:
                long_name_string = long_name_string + coord + ', '
                
        #remove last comma and close parentheses
        long_name_string = long_name_string[0:-2] + ')' 

        da_stacked.coords['ct'].attrs = dict(long_name=long_name_string)  

        da_unstacked = da_stacked.unstack()  

    for coord in da.coords:
        da_unstacked.coords[coord].attrs = da.coords[coord].attrs

    return da_unstacked, da_stacked

def gen_timeinfo(da_ct):
    """create a dataset with info about the time slices"""
    start = da_ct.copy()
    start.name = 'start timestamp'
    start.attrs = dict(units = 'ns')
    end = da_ct.copy()
    end.name = 'end timestamp'
    end.attrs = dict(units = 'ns')
    timestr = da_ct.copy()
    timestr.name = 'time window string'
    
    seldicts = gen_seldicts(da_ct)
    for seldict in seldicts:
        start.loc[seldict] = da_ct.loc[seldict].item().start 
        end.loc[seldict] = da_ct.loc[seldict].item().stop
        timestr.loc[seldict] = str(da_ct.loc[seldict].item().start) + ' - ' +  str(da_ct.loc[seldict].item().stop)

    timeinfo = xr.merge([timestr,start,end])
    # temp = []
    # for stat in flows.coords['stat']:
    #     temp.append(da_ct.assign_coords(stat = stat).expand_dims('stat'))
    # da_ct = xr.concat(temp, 'stat')
    
    return timeinfo


def reduce_da_ct(da_ct, timewindows):
    """
    Pass in a unstacked da_ct and a timewindow or list of timewindows.
    Will remove all coordinates that are outside of those timewindows, 
    
    returns: da_ct_cut and da_ct_cut_stack
    """

    #If single timewindow passed in convert to list
    if type(timewindows) == slice:
        timewindows = [timewindows]

    da_ct_cut = da_ct.copy(deep=True).where(False)

    seldicts = gen_seldicts(da_ct)

    for seldict in seldicts:
        ct = da_ct.sel(seldict).item()
        for timewindow in timewindows:
            if (ct.start > timewindow.start) and (ct.stop < timewindow.stop):
                da_ct_cut.loc[seldict] = ct

    da_ct_cut, da_ct_cut_stack = reset_da_ct(da_ct_cut)
        
    return da_ct_cut, da_ct_cut_stack

def reset_da_ct(da_ct, keep_attrs = False, drop_single = True):
    """
    Perform this after downselecting coordinates in da_ct
    drops any dimensions with all nans, reset the measurement numbers if any, and reset the index

    returns: da_ct and da_ct_stack
    """
    for dim in da_ct.dims:
        da_ct = da_ct.dropna(dim,'all')

    attr_dict = {coordname: da_ct.coords[coordname].attrs for coordname in da_ct.coords}

    if drop_single:
        da_ct = drop_single_coords(da_ct)
    
    da_ct = da_ct.stack(ct=[...]).dropna('ct','all').reset_index('ct')

    if 'mnum' in da_ct.coords:
        da_ct = assign_measnum(da_ct.drop('mnum'))

    # import pdb; pdb.set_trace()

    da_ct, da_ct_stack = set_index_da_ct(da_ct)

    if keep_attrs:
        for coord in attr_dict:
            if coord in da_ct.coords:
                da_ct.coords[coord].attrs = attr_dict[coord]

    return da_ct, da_ct_stack

def get_region(da_ct, buffer = None):
    """
    gets the minimum and maximum times in da_ct
    returns slice(min, max)
    Specifying buffer (from 0.0 to 1.0) will add a fraction of the time window as a buffer to the edges
    """
    seldicts = gen_seldicts(da_ct)

    times = []

    for seldict in seldicts:
        ct = da_ct.sel(seldict).item()
        times.append(ct.start)
        times.append(ct.stop)

    mintime = min(times)
    maxtime = max(times)

    if buffer is not None:
        bufftime = (maxtime - mintime)*buffer
        mintime = mintime - bufftime
        maxtime = maxtime + bufftime 

    region = slice(mintime, maxtime)

    return region


def sort_ct_list(ct):
    """Sorts a list of slices by the start time of the slices (use before making da_ct)"""
    starts = [sl.start for sl in ct]

    s = pd.Series(ct, index = starts)

    ct = list(s.sort_index().values)
    
    return ct