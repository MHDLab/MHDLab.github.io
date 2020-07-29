"""
Utilitiy functions related to the electrical measurements of the MHD impedance tester
"""


import numpy as np
import xarray as xr
from .xr import gen_seldicts, bin_da


def bin_gen(da_gen, bins = np.arange(-2.5,602.5,5), min_points = 10, curname = 'cur_gen', voltname = 'volt_gen'):

    i = da_gen[curname]
    v = da_gen[voltname]

    seldicts = gen_seldicts(v, [dim for dim in v.dims if dim != 'time'])

    vs = []
    for seldict in seldicts:
        v_time = v.sel(seldict)
        for dim in seldict:
            v_time = v_time.drop(dim)

        vs.append(v_time)
    vs = xr.merge(vs)[voltname]
    i_v = i.assign_coords(time=vs).rename(time='voltage')    
    i_v.coords['voltage'].attrs = v.attrs

    da_mean, da_std = bin_da(i_v, bin_dim='voltage', bins=bins, min_points=min_points)
    
    return da_mean, da_std


def subtract_current_offsets(da_current, offsetcurrent_times):
    """
    Multiple current offsets, perhaps should just explicity set windows

    takes in multiple windows for current offsets and makes the data after that window subtracted by the current offset window before the next current offset window
    not sure if this is the best method 
    """

    xr.set_options(keep_attrs=True)
    if type(offsetcurrent_times) == slice:
        currentoffset = da_current.sel(time=offsetcurrent_times).mean('time', keep_attrs=True)

        da_out = da_current - currentoffset

    else:
        #list of times
        das = []

        for i, time in enumerate(offsetcurrent_times):
            currentoffset = da_current.sel(time=time).mean('time', keep_attrs=True)

            if i == 0:
                starttime = da_current.coords['time'][0]
                endtime = offsetcurrent_times[i+1].start
            if i == (len(offsetcurrent_times) -1):
                starttime = offsetcurrent_times[i].start
                endtime = da_current.coords['time'][-1]
            else:
                starttime = offsetcurrent_times[i].start
                endtime = offsetcurrent_times[i+1].start

            
            da = da_current.sel(time=slice(starttime,endtime)) - currentoffset
            
            da = da.isel(time=slice(1,-2)) #remove end points so no duplicate index

            das.append(da)

        da_out = xr.concat(das, 'time')


    xr.set_options(keep_attrs=False)
    da_out.attrs['current_offsets_subracted'] = str(offsetcurrent_times)


    return da_out
