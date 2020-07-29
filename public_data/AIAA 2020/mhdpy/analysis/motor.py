# -*- coding: utf-8 -*-

"""
Functions for handling motorized stage position data
In particular, these utilities are used to assign a motor position to another time-based measurement by finding the position that the motor was at nearest to that time. 

"""

import xarray as xr

def assign_direc(da, da_motor, timeindex='time', deriv_min=1e-3):
    """
    adds a 'direction' dimension based on the derivative of the motor position vs time

    Parameters
    ----------
    da: DataArray with a time index
    da_motor: DataArray of motor position with respect to time
    timeindex: name of time index
    deriv_min: minimum absolute value of derivative to be considered, there are often false values that are very small in the wrong direciton
    
    Returns
    -------
    DataArray
    """
    timearray = da.coords[timeindex].values

    motorderiv = da_motor.diff('time')

    # small cutoff for derivative
    motorderiv_cut = motorderiv.where(abs(motorderiv) > deriv_min).dropna('time') 

    slopes = motorderiv_cut.sel({'time': timearray}, method='nearest')

    # for now set the motor time index to the dataarrays time index, probably
    # should interpolate instead, but because the mp is found by the 'nearest'
    # method this may actually be more accurate. Should basically interpolate
    # above as well if this is the case.
    slopes = slopes.assign_coords(time=timearray)

    direcs = []

    for slope in slopes.values:
        if slope > 0:
            direcs.append('U')
        elif slope < 0:
            direcs.append('D')

    direcs = xr.DataArray(direcs,
                          coords={'time': slopes.coords['time']},
                          dims=['time'])

    da = da.assign_coords(direc=(timeindex, direcs))
    da = da.set_index(t=[timeindex, 'direc'])
    if timeindex in da.coords:
        #new data format encounters error with no 'time' dim. Maybe new xarray version.
        da = da.rename({timeindex: 't'})
    da = da.unstack('t')

    return da


def assign_mp(da, da_motor, timeindex='time'):
    """
    converts the time index of da to motor position.
    Note that this should be applied last as there are often duplicate values
    in the motor position, which will cause issues when trying to assign test
    cases or motor direction. 

    Parameters
    ----------
    da: DataArray with a time index
    da_motor: DataArray of motor position with respect to time
    timeindex: name of time index
    
    Returns
    -------
    DataArray
    """
    timearray = da.coords[timeindex].values

    #assumes motor has 'time' time index
    #use ffill instead of interpolation because motor is at previous position while waitng. 
    #with 'nearest' the waiting data is half last motor position, and other half first changed position
    mps = da_motor.sel(time=timearray, method='ffill')

    mps = mps.assign_coords(time=timearray)

    da.coords[timeindex] = mps.values
    da = da.rename({timeindex:'mp'}).assign_coords(time=('mp', da.coords[timeindex].values))
    # da.coords['time'] = {'time':('mp', da.coords['time'].values)}
    da.coords['mp'].attrs = dict(long_name='Motor Position', units='mm')
    da = da.sortby('mp')

    return da


def average_mp(da):
    """
    takes a DataArray with duplicate motor positions in the coordinates and averages over those motor positions. 
    """
    def calc_stat(da, stat):
        #da is groups of values with same mp coordinate
        mp = da.coords['mp'].values[0]
        if stat == 'mean':
            da = da.mean('mp', keep_attrs=True).assign_coords(mp=mp)
        elif stat == 'std':
            da = da.std('mp', keep_attrs=True).assign_coords(mp=mp)
        
        return da

    #Removes na from coordinates...don't think nessecary
    # dapl = dapl.where(~np.isnan(dapl.coords['mp'])).dropna('mp', 'all')
    mpattrs = da.coords['mp'].attrs

    mean = da.sortby('mp').groupby('mp').apply(calc_stat, stat='mean')
    std = da.sortby('mp').groupby('mp').apply(calc_stat, stat='std')

    mean.coords['mp'].attrs = mpattrs
    std.coords['mp'].attrs = mpattrs

    return mean, std
