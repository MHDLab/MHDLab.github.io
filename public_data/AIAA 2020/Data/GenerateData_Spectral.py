"""
This code is used to generate final data for the AIAA 2020 MHDGEN manuscript.
The starting data is the processed data on the sharepoint
"""

import os
import numpy as np
import pandas as pd
import xarray as xr
from pandas import Timestamp
import pickle

from mhdpy import load, timefuncs, fp, analysis


finalanalysisfolder = fp.gen_path('mhdlab','Analysis', 'Lee', 'MHDGEN','Final')
dataoutputfolder = os.path.join(finalanalysisfolder, 'Data')
metadatafolder = os.path.join(dataoutputfolder, 'data_generation_metadata')

dsst = load.loadprocesseddata(os.path.join(dataoutputfolder,  'dsst'))


datestrs = ['2020-03-13', '2020-06-11', '2020-06-23', '2020-07-01']

#Generate the list of calibration cuttimes for each date
ct_calib_all = timefuncs.load_cuttimes(os.path.join(metadatafolder, 'CT_absem_calibration.csv'))
ct_dict = {datestr : [] for datestr in datestrs}

for sl in ct_calib_all:
    ts = pd.Timestamp(sl.start)
    datestr = str(ts.year) + '-' + str(ts.strftime('%m'))+ '-' + str(ts.strftime('%d'))
    ct_dict[datestr].append(sl)


with open(os.path.join(dataoutputfolder, 'da_ct.pickle'), 'rb') as file:
    da_ct = pickle.load(file)

#Run through each date and 
alphas = []
for datestr in datestrs:
    print('Calculating alpha for date ' + datestr)
    datafolder = fp.gen_path('sharepoint','Data Share', 'MHD Lab', 'HVOF Booth',datestr)
    raw_cdf_folder = os.path.join(datafolder, 'Munged', 'CDF')
    ds_absem = xr.load_dataset(os.path.join(raw_cdf_folder,'absem.cdf'))
    ds_absem_calib = xr.load_dataset(os.path.join(raw_cdf_folder,'absem_calib.cdf'))
    dss = {'absem' : ds_absem , 'absem_calib' : ds_absem_calib}

    #TODO: reprocess spectral data with a wider high resolution range and update these ranges to match (then ranges later aren't needed)
    dss['absem'] = dss['absem'].sel(wavelength = slice(761,775))
    dss['absem_calib'] = dss['absem_calib'].sel(wavelength = slice(761,775))

    dss['absem'] = dss['absem']#.sel(inttime=10).drop('inttime').dropna('time','all')
    dss['absem_calib'] = dss['absem_calib']#.sel(inttime=10).drop('inttime').dropna('time','all')

    ct_calib = ct_dict[datestr]

    #assumes each date has only two calibrations. This labelling isn't actually necessary in this script
    tcs = ['before','after',]

    
    calib = analysis.spectral.process_calib(dss['absem_calib'],ct_calib, tcs)
    calib = calib.sel(wavelength=dss['absem'].coords['wavelength'])
    calib_int = calib['intensity']

    #TODO: comment and replace fixed dates with avg_time values For 07-01, the
    #used test cases before the seed ramp used integration time of 40 ms. I
    #neglected to take 20 and 40 ms acquisitions so I just make the 40 ms
    #acquisition as 4X the 10 ms one. I confirmed that this procedure reproduced
    #the correct spectrum when applied to the data after the measurement where
    #40 ms calibration was taken i.e. the spectrometer is linear in this regime.
    if datestr == '2020-07-01':
        calib_int.loc[calib_int.coords['avg_time'].values[0],:,20] = calib_int.loc[calib_int.coords['avg_time'].values[0],:,10]*2
        calib_int.loc[calib_int.coords['avg_time'].values[0],:,40] = calib_int.loc[calib_int.coords['avg_time'].values[0],:,10]*4

    #drop data where the led on (which will be brigher than led off) is near the limit of the spectrometer
    diff = dss['absem']['diff'].where(dss['absem']['led_on'] <18000).dropna('time','all')

    #Interpolate the calibration in time
    calib_int_interp = calib_int.interp(avg_time=diff.time).drop('avg_time')

    #Calculate alpha
    alpha = 1 - diff/calib_int_interp
    alpha.attrs = dict(long_name=r'$\alpha$')
    alpha.name = 'alpha'

    if datestr == '2020-07-01':
        #Residual seed
        timesl_residualseed = slice(Timestamp('2020-07-01 18:21:40'), Timestamp('2020-07-01 18:22:40'), None)
        alpha_residualseed = alpha.sel(time=timesl_residualseed).mean('time').sel(inttime=10).drop('inttime')
        #Data a few minutes later with torch off to subract. residual seed data seemed to have a slight vertical offset
        timesl_residualseed_offset = slice(Timestamp('2020-07-01 18:24:35'), Timestamp('2020-07-01 18:25:00'), None)
        alpha_residualseed_offset = alpha.sel(time=timesl_residualseed_offset).mean('time').sel(inttime=10).drop('inttime')
        alpha_residualseed = (alpha_residualseed-alpha_residualseed_offset)

    #Assign test cases and average over time
    alpha_tc = analysis.ct.assign_tc_general(alpha,da_ct).mean('time', keep_attrs = True)

    #Remove integration time coordinate
    alphas_inttime = []
    for inttime in alpha_tc.coords['inttime']:
        alphas_inttime.append(alpha_tc.sel(inttime=inttime).drop('inttime'))

    alpha_tc = xr.merge(alphas_inttime)

    alphas.append(alpha_tc)

print('Merging')
alpha_tc = xr.merge(alphas)['alpha']

def interp_alpha(alpha):
    """
    For the gaussian blurring used in the fitting model the datapoints are
    assumed to be evenly spaced. This is nearly true with the spectometer
    withing a few percent. The spacing is near the gaussian standard deviation
    of the spectrometer resolution (0.026) which I assume was intentional by the
    manufacturer. So just interpolate to this value, then gaussian blurring with
    standard deviation of 1 datapoint in the model will be equivalent to
    analytically perforiming a convolution which I found difficult to implement.
    Most information I could find on the internet indicated convoluting with
    unevenly spaced datapoints should involve a interpolation anyway. 
    """
    print('Interpolating wavelengths...')
    wls = alpha.coords['wavelength'].values
    wls_interp = np.arange(wls.min(),wls.max(),0.026)
    alpha = alpha.interp(wavelength=wls_interp)
    return alpha


final_model, pars = analysis.spectral.model_blurredalpha_2peak()

###Residual seed fitting
alpha_residualseed = interp_alpha(alpha_residualseed)
wls = alpha_residualseed.coords['wavelength'].values
out = final_model.fit(alpha_residualseed, pars, x=wls)
print('residual seed fit report: ')
print(out.fit_report())
alpha_residualseed_fit = alpha_residualseed.copy()
alpha_residualseed_fit.values = out.eval(x=wls)
alpha_residualseed_fit.attrs['fit_nK'] = out.params['nK_m3'].value
alpha_residualseed_fit.attrs['fit_nK_stderr'] = out.params['nK_m3'].stderr

alpha_residualseed.name = 'alpha'
alpha_residualseed_fit.name = 'alpha_fit'
ds_alpha_residualseed = xr.merge([alpha_residualseed, alpha_residualseed_fit])


###Seeded cases fitting
alpha_tc = interp_alpha(alpha_tc)
wls = alpha_tc.coords['wavelength'].values

spectral_reduction_params_fp = os.path.join(metadatafolder, 'spectral_reduction_params.csv')
spect_red_dict = pd.read_csv(spectral_reduction_params_fp, index_col=0,squeeze=True).to_dict()
print('Reducing alpha with following data reduction parameters: ')
print(spect_red_dict)
alpha_tc_red = analysis.spectral.alpha_cut(alpha_tc,**spect_red_dict).dropna('wavelength','all')
alpha_tc_red.name = 'alpha_red'

fits, ds_p, ds_p_stderr = analysis.xr.fit_da_lmfit(alpha_tc_red, final_model, pars, 'wavelength', wls)
ds_p['nK_m3'].attrs = dict(long_name='$n_{K,expt}$', units = '$\\#/m^3$')
fits.name = 'alpha_fit'

ds_alpha = xr.merge([alpha_tc, alpha_tc_red, fits])

ds_alpha.to_netcdf(os.path.join(dataoutputfolder, 'spectral_data', 'ds_alpha.cdf'))
ds_alpha_residualseed.to_netcdf(os.path.join(dataoutputfolder, 'spectral_data', 'ds_alpha_residualseed.cdf'))
ds_p.to_netcdf(os.path.join(dataoutputfolder,'spectral_data','fit_params.cdf'))
ds_p_stderr.to_netcdf(os.path.join(dataoutputfolder,'spectral_data','fit_params_stderr.cdf'))
