import xarray as xr
import os
import pandas as pd
import numpy as np


def read_cuttingtimes(fp):
    """
    Reads in cutting times csv and outputs an array of time slices

    Parameters
    ----------
    fp : str
        Csv file path

    Returns
    -------
    slices : list
        List of time slices
    """
    times = pd.read_csv(fp, header=None)

    def func(time):
        return np.datetime64(time, 'us')

    times = times.applymap(func)
    slices = [slice(times.loc[t][0], times.loc[t][1]) for t in times.index]

    return slices


def loadprocesseddata(dsspath, filetype = 'cdf'):
    """
    load datasets contained within a path. TDMS not supported at the moment
    #TODO: This has just been copied from the post processing repo utilites.
    NEed to figure out where loadfunction like tdms2ds will go.
    """

    dss = {}

    if filetype == 'cdf':
        ext = '.cdf'
        loadfn = xr.open_dataset
    elif filetype == 'tdms':
        ext = '.tdms'
        loadfn = tdms2ds

    if not os.path.exists(dsspath):
        return dss

    for fn in os.listdir(dsspath):
        if fn.endswith(ext):
            fp = os.path.join(dsspath, fn)
            fn = os.path.splitext(fn)[0]
            dss[fn] = loadfn(fp)
            if filetype == 'cdf':
                dss[fn].close()   
            elif filetype == 'tdms':
                namemap = gen_namemap(dss[fn].variables, prepend_groupname = False)
                dss[fn] = dss[fn].rename(namemap)
            
    return dss


def match_variables(dss):
    """
    Matches the variables in the datasets in dss_fps some variables can be
    missing if signals were being added in the first few dummy datsets. So the
    datsets are made to include the set of all variables found by adding
    variables filled with nan. One can change the filepath regular expression to
    avoid loading in those files as well. 
    """

    # Get a set of all variable names
    variableset = []
    for ds in dss:
        variableset.extend(list(ds.data_vars))
    variableset = set(variableset)

    # cycle through data sets and if any variables are missing add a dummy Nan variable to the dataset
    
    missing_vars_list = []

    dss_new = []
    for ds in dss:
        for var in variableset:
            if var not in list(ds.data_vars):
                missing_vars_list.append(var)
                da_temp = ds[list(ds.data_vars)[0]]
                da_temp = da_temp.where(False)
                ds = ds.assign({var: da_temp})
        dss_new.append(ds)

    if len(missing_vars_list):
        print('did not find variables' + str(missing_vars_list) + ' , Added dataarrays full of NaN to corresponding ds')

    return dss_new

