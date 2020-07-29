"""
This code is used to generate final datasets with respect to time (dsst) and the
data arrays of cuttimes (da_ct) for the AIAA 2020 MHDGEN manuscript. The
starting data is the processed dsst on the sharepoint
"""

import os
import numpy as np
import pandas as pd
import xarray as xr
import pickle

from mhdpy import load, timefuncs, fp, analysis


finalanalysisfolder = fp.gen_path('mhdlab','Analysis', 'Lee', 'MHDGEN','Final')
dataoutputfolder = os.path.join(finalanalysisfolder, 'Data')
metadatafolder = os.path.join(dataoutputfolder, 'data_generation_metadata')


datestrs = ['2020-03-13', '2020-06-11', '2020-06-23', '2020-07-01']

processed_data_ignore = ['spectral_fit_params', 'spectral_fits', 'spectral_stats']

# #Load in datasets with respect to time
dsst = {}
for datestr in datestrs:
    sharepointdatafolder = fp.gen_path('sharepoint','Data Share', 'MHD Lab', 'HVOF Booth',datestr)
    dsst_temp = load.loadprocesseddata(os.path.join(sharepointdatafolder, 'Processed CDF'))
    for key in dsst_temp:
        if key not in processed_data_ignore:
            if key not in dsst:
                dsst[key] = [dsst_temp[key]]
            else:
                dsst[key].append(dsst_temp[key])

for key in dsst:
    dsst[key] = xr.concat(load.match_variables(dsst[key]),'time')

#Simplify names
dsst['hvof_input_calcs']['totalmassflow_hvof'].attrs['long_name'] ='Total Mass Flow'
dsst['hvof_input_calcs']['Kwt_hvof'].attrs['long_name'] = 'K wt%'

for key in dsst:    
    dsst[key].to_netcdf(os.path.join(dataoutputfolder, 'dsst', key + '.cdf'))
    

da_cts = []

ct = timefuncs.load_cuttimes(os.path.join(metadatafolder, 'CT_finalmatrix_seedonly.csv'))
ct = analysis.ct.sort_ct_list(ct)

da_ct = analysis.ct.gen_da_ct_data(ct,
                            dim_dict = {
                                'tf': {'data' : dsst['hvof_input_calcs']['totalmassflow_hvof'], 'round_value': 10},
                                'Kwt': {'data' : dsst['hvof_input_calcs']['Kwt_hvof'], 'round_value':10 },
                            })

ct_datestrs = []
for sl in ct:
    ts = pd.Timestamp(sl.start)
    datestr = str(ts.year) + '-' + str(ts.strftime('%m'))+ '-' + str(ts.strftime('%d'))
    ct_datestrs.append(datestr)

da_ct = da_ct.assign_coords(date = ('ct', ct_datestrs))
da_ct = analysis.xr.fix_coord_grid_bins(da_ct, 'tf', 3, round_value=2)
da_ct = analysis.xr.fix_coord_grid_bins(da_ct, 'Kwt', [0,0.15,0.5,2], round_value=2)

da_ct = analysis.ct.assign_measnum(da_ct)

da_ct, da_ct_stack = analysis.ct.set_index_da_ct(da_ct)

#Some datasets have another totalflow = 12.9 and smf =0.1% as mnum =1 but not all, so just using the datafrom the total flow ramp for the seed ramp for now
da_ct = da_ct.sel(mnum=0).drop('mnum')

with open(os.path.join(dataoutputfolder,'da_ct.pickle'), 'wb') as f:
    pickle.dump(da_ct, f)

### No seed data### 
# This data was taken at various total flows that mess up the test case grid, so it is processed separately for now

ct_noseed = timefuncs.load_cuttimes(os.path.join(metadatafolder, 'CT_finalmatrix_noseed.csv'))

ct_noseed = analysis.ct.sort_ct_list(ct_noseed)

da_ct_noseed = analysis.ct.gen_da_ct_data(ct_noseed,
                            dim_dict = {
                                'tf': {'data' : dsst['hvof_input_calcs']['totalmassflow_hvof'], 'round_value': 10},
                                'Kwt': {'data' : dsst['hvof_input_calcs']['Kwt_hvof'], 'round_value':10 },
                            })


noseed_datestrs = []
for sl in ct_noseed:
    ts = pd.Timestamp(sl.start)
    datestr = str(ts.year) + '-' + str(ts.strftime('%m'))+ '-' + str(ts.strftime('%d'))
    noseed_datestrs.append(datestr)

da_ct_noseed = da_ct_noseed.assign_coords(date = ('ct', noseed_datestrs))
da_ct_noseed = analysis.xr.fix_coord_grid_bins(da_ct_noseed, 'Kwt', [0,0.15,0.5,2], round_value=10)
da_ct_noseed, da_ct_noseed_stack = analysis.ct.set_index_da_ct(da_ct_noseed)

with open(os.path.join(dataoutputfolder,'da_ct_noseed.pickle'), 'wb') as f:
    pickle.dump(da_ct_noseed, f)