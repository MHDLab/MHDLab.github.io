"""
Functions related to analysis of spectral data
"""

import numpy as np
from scipy.special import wofz


def twocolortemp(wl1,wl2,s):
    c2 = 14394264.78261
    wi1 = np.where(np.abs(s.index - wl1)<3.28)[0][0]
    wi2 = np.where(np.abs(s.index - wl2)<3.28)[0][0]
    e1 = s.iloc[wi1]
    e2 = s.iloc[wi2]
    num = c2*((1/wl1)-(1/wl2))
    den = -np.log(e1*wl1**5)+np.log(e2*wl2**5)
    return num/den


def gauss(x, x0, alpha):
    """ Return Gaussian line shape at x with HWHM alpha """
    xs = x - x0
    return np.sqrt(np.log(2) / np.pi) / alpha\
                             * np.exp(-(xs / alpha)**2 * np.log(2))


def lor(x, x0, gamma):
    """ Return Lorentzian line shape at x with HWHM gamma """
    xs = x - x0
    return gamma / np.pi / (xs**2 + gamma**2)

                                                    
def V(x, x0, w, gamma):
    """
    Return the Voigt line shape at x with Lorentzian component HWHM gamma
    and Gaussian component HWHM w.

    """
    sigma = w / np.sqrt(2 * np.log(2))

    return np.real(wofz(( (x-x0) + 1j*gamma)/sigma/np.sqrt(2))) / sigma\
                                                           /np.sqrt(2*np.pi)

def calc_Sv(x, x01, x02, w, gamma):
    Sv = ( (4/6)*0.7*V(x, x01, w, gamma) + 0.35*V(x, x02, w, gamma) )
    return Sv

def beta_2peak(x, x01, x02, w, gamma, nK, L=0.01, wl0 = 770e-9):

    e = 1.6e-19
    me = 9.1e-31
    epsilon0 = 8.85e-12
    c = 3e8
    f0 = (e**2)/(4*epsilon0*me*(c**2))

    x = x*1e-9
    x01 = x01*1e-9
    x02 = x02*1e-9
    gamma = gamma*1e-9
    w = w*1e-9
    
    Sv = calc_Sv(x, x01, x02, w, gamma)

    kappa = f0*(wl0**2)*Sv

    beta = kappa*nK*L

    return beta

def alpha_cut(alpha, hori_limit, peak1_low, peak1_high, peak2_low, peak2_high):
    """
    Removes data from potassium absorption coreffection  spectral dataset.
    Removes data above horizontal limit and between two peaks
    """
    alpha_red = alpha.where(alpha<hori_limit)
    alpha_red = alpha_red.where(alpha_red>0)

    wls = alpha_red.sel(wavelength=slice(peak1_low, peak1_high)).coords['wavelength']
    alpha_red = alpha_red.drop_sel(wavelength=wls)

    wls = alpha_red.sel(wavelength=slice(peak2_low, peak2_high)).coords['wavelength']
    alpha_red = alpha_red.drop_sel(wavelength=wls)    
    
    return alpha_red

import xarray as xr
import mhdpy

def process_calib(ds_absem_calib, cuttimes, test_cases):
    """
    processes absorption emission calibration data, assuming that calibrations
    were taken at a few times throughout the experiment labeled by an array of
    strings 'test_cases'  (usually 'before' and 'after'). The data over these
    time windows (cuttimes) is averaged and the average time of this window is
    assigned as a coordinate 'avg_time' 
    """

    da_ct_calib = xr.DataArray(cuttimes, dims='tc', coords={'tc':test_cases})
    ds_absem_calib = mhdpy.analysis.ct.assign_tc_general(ds_absem_calib,da_ct_calib)


    das = []
    for tc in ds_absem_calib.coords['tc']:
        da = ds_absem_calib.sel(tc=tc).drop('tc').dropna('time','all')
        avg_time = da.time.mean().astype('datetime64[s]')
        da= da.mean('time').assign_coords(avg_time=avg_time).expand_dims('avg_time')
        das.append(da)
        
    ds_absem_calib = xr.concat(das, 'avg_time').sortby('avg_time')

    calib = xr.merge([
        ds_absem_calib['led_off'].rename('background'),
        (ds_absem_calib['led_on'] - ds_absem_calib['led_off']).rename('intensity'),
    ])

    return calib


import lmfit
from lmfit.models import GaussianModel, LorentzianModel, VoigtModel, ConstantModel
from lmfit import Model, CompositeModel
from lmfit.lineshapes import gaussian, voigt
from scipy.ndimage import gaussian_filter1d

def model_absorbance_2peak(base_model = 'voigt'):

    # units converted from m to nm
    e = 1.6e-19
    me = 9.1e-31
    epsilon0 = 8.85e-39 
    c = 3e17
    f0 = (e**2)/(4*epsilon0*me*(c**2))
    wl0=768 #TODO: Convert to average or make per peak
    L = 1e7

    #TODO: Figure out a more elegant way to include this factor in the constant model. This is used to convert the amplitude of the resultant fit to nK.

    factor = f0*(wl0**2)*L
    # print('Amplitude factor: ' + str(factor))

    T = 3000
    kb = 1.38e-5
    mK = 39*1.67e-27

    delta_wl_D = 2*np.sqrt(2*np.log(2)*kb*T/mK)*(wl0/c)
    # print('delta_wl_D: ' + str(delta_wl_D))
    delta_wl_C = ((wl0**2)/c)*3.1e9 #TODO: This is different for each peak
    # print('delta_wl_C: ' + str(delta_wl_C))

    if base_model == 'voigt':
        model_base = VoigtModel
    elif base_model =='lor':
        model_base = LorentzianModel

    mod_p1 = model_base(prefix='p1_')
    mod_p2 = model_base(prefix='p2_')

    Sv_mod = mod_p1 + mod_p2

    mod_amp = ConstantModel(prefix='amp_')

    final_model = Sv_mod*mod_amp

    pars = final_model.make_params()

    pars['amp_c'].value = 1 #initial guess, would be nice to do this wiht nK...

    #Centers determined from residual seed fit

    pars['p1_center'].value = 766.504333
    pars['p1_center'].vary = False

    pars['p2_center'].value = 769.913219
    pars['p2_center'].vary = False

    # pars['p1_amplitude'].expr = 'p2_amplitude*(4/6)*0.7/0.35'
    pars['p1_amplitude'].value = (4/6)*0.7
    pars['p1_amplitude'].vary = False

    pars['p2_amplitude'].value = 0.35
    pars['p2_amplitude'].vary = False



    if base_model == 'voigt':
        pars['p1_gamma'].value = delta_wl_C
        pars['p1_gamma'].vary = False
        pars['p1_gamma'].expr = None
        pars['p2_gamma'].expr = 'p1_gamma'

        pars['p1_sigma'].value = np.sqrt(delta_wl_D**2 + 0.026**2)
        pars['p1_sigma'].vary = False
        pars['p2_sigma'].expr = 'p1_sigma'

    elif base_model == 'lor':
        pars['p1_sigma'].value = delta_wl_C
        pars['p1_sigma'].vary = False
        pars['p1_sigma'].expr = None
        pars['p2_sigma'].expr = 'p1_sigma'        

    # pars += mod_amp.make_params()

    pars.add('nK', expr='amp_c/(52352117.43686319*0.4343)') #This factor is what is calculated above
    pars.add('nK_cm3', expr = 'nK*1e21')
    pars.add('nK_m3', expr = 'nK*1e27')

    return final_model, pars


def blurred_alpha(
    x, nK =1e-7, L=1e7, p1_stat_weight = (4/6)*0.7, 
    p1_center = 766.504333, p1_delta_f_C = 3.19e9,p2_stat_weight = 0.35, 
    p2_center = 769.913219, p2_delta_f_C = 3.04e9
                ):


    # units converted from m to nm
    e = 1.6e-19
    me = 9.1e-31
    epsilon0 = 8.85e-39 
    c = 3e17
    f0 = (e**2)/(4*epsilon0*me*(c**2))

    T = 3000
    kb = 1.38e-5
    K_MW        = 39.1
    NA = 6.022E23
    mK         = (K_MW/1000)/NA
    # mK = 39*1.67e-27

    #TODO: convert to array math

    p1_delta_wl_D = 2*np.sqrt(2*np.log(2)*kb*T/mK)*(p1_center/c)
    p1_delta_wl_C = ((p1_center**2)/c)*p1_delta_f_C
    p1_prefactor = p1_stat_weight*f0*p1_center**2

    p2_delta_wl_D = 2*np.sqrt(2*np.log(2)*kb*T/mK)*(p2_center/c)
    p2_delta_wl_C = ((p2_center**2)/c)*p2_delta_f_C
    p2_prefactor = p2_stat_weight*f0*p2_center**2
    

    kappa = p1_prefactor*voigt(x, 1, p1_center, p1_delta_wl_D, p1_delta_wl_C) + p2_prefactor*voigt(x, 1, p2_center, p2_delta_wl_D, p2_delta_wl_C)

    
    y = 1-np.exp(-nK*L*kappa)


    # assert all(np.diff(x) == np.diff(x)[0]) #Assuming all interpolated data at 0.026
    
    y = gaussian_filter1d(y, 1)
    return y


def model_blurredalpha_2peak():


    final_model = Model(blurred_alpha)

    pars = final_model.make_params(L = 1e7, nK = 1e-7,
        p1_stat_weight = (4/6)*0.7, p1_center = 766.504333, p1_delta_f_C = 3.19e9,
        p2_stat_weight = 0.35, p2_center = 769.913219, p2_delta_f_C = 3.04e9
    )

    # pars['p2_nK'].expr = 'p1_nK'
    # pars['p2_L'].expr = 'p1_L'

    for par in pars:
        if 'nK' not in par:
            pars[par].vary = False

    pars.add('nK_m3', expr = 'nK*1e27')

    return final_model, pars