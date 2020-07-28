# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%



# %%
import os
import numpy as np
import pandas as pd
import xarray as xr
import matplotlib as mpl
import matplotlib.pyplot as plt
from pandas import Timestamp
import pickle

from mhdpy import *
import mhdpy

import pytz
mpl.rcParams.update({'font.size': 16, 'timezone': pytz.timezone('America/Los_Angeles')})


# %%
datestr = '2020-06-23'
datafolder = mhdpy.fp.gen_path('sharepoint','Data Share', 'MHD Lab', 'HVOF Booth',datestr)
dsst = mhdpy.load.loadprocesseddata(os.path.join(datafolder, 'Processed CDF'))
analysisfolder = mhdpy.fp.gen_path('mhdlab','Analysis', 'Lee', 'MHDGEN',datestr)


# %%
import numpy as np
import pandas as pd
import holoviews as hv

from holoviews.util.transform import dim
from holoviews.selection import link_selections
from holoviews.operation import gridmatrix
from holoviews.operation.element import histogram
from holoviews import opts

hv.extension('bokeh', 'plotly', width=100)


# %%
dsst.keys()


# %%
timewindows_tf = slice(Timestamp('2020-06-23 18:03:12.990436096'), Timestamp('2020-06-23 18:12:54.039913216'), None)


# %%
dss = [
    dsst['hvof_input_calcs'],
    dsst['spectral_stats'][['led_off_mean', 'led_off_max']],
    dsst['tc1'][['T_comb_center', 'T_Barrel_2']]
]



dss = [ds.sel(time=timewindows_tf).resample(time='s').mean(keep_attrs=True) for ds in dss]

ds = xr.merge(dss)

df = ds.to_dataframe()


# %%
hvds = hv.Dataset(df)

mopts = opts.Points(size=2, tools=['box_select','lasso_select'], active_tools=['box_select'])

gm = gridmatrix(hvds, chart_type=hv.Points).opts(mopts)


# %%
gm


# %%
#Save to a html document

fp = os.path.join(os.getcwd(), 'gridmatrix.html')

hv.save(gm, fp)


