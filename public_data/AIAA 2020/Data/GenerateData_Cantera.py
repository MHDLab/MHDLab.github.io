"""
This script uses cantera to calculate the outlet temprature, potassium number
density, and conductivity at the outlet of the MHDgen system. The measured wall
heat transfers of the combustor and barrel are used to remove the enthalpy from
the gasses in stages, with enthalpy also removed from work done on the gasses to
reach 1e3 m/s. 
"""

import cantera as ct
import numpy as np
import pandas as pd
import xarray as xr
import pickle
import os
import xyzpy

from mhdpy import load, timefuncs, fp, analysis

finalanalysisfolder = fp.gen_path('mhdlab','Analysis', 'Lee', 'MHDGEN','Final')
dataoutputfolder = os.path.join(finalanalysisfolder, 'Data')
metadatafolder = os.path.join(dataoutputfolder, 'data_generation_metadata')

dsst = load.loadprocesseddata(os.path.join(dataoutputfolder, 'dsst'))

with open(os.path.join(dataoutputfolder, 'da_ct.pickle'), 'rb') as file:
    da_ct = pickle.load(file)

#mhdcantera repository cantera utilities (originally from table gen)
import sys
mhdcantera_repo_path = r'C:\Users\aspit\Git\MHDLab\mhdcantera'
sys.path.append(mhdcantera_repo_path)
from cantera_utils import util as ct_utils

ct_path = os.path.join(mhdcantera_repo_path, 'cantera_utils', 'data')
ct.add_directory(ct_path)

g, electron_trans = ct_utils.gen_gas(
                    GasThermo_tr = 'data/drm19_SeededKero.cti',
                    GasThermoName_tr = 'gas',
                    CrossSectionFile = 'data/NETL_CF2017.csv',
                    basis = 'mass'
                    )

W = g.molecular_weights
MW = {name:W[i] for i, name in enumerate(g.species_names)}
MW["K2CO3"] = 2*MW["K"] + MW["CO2"] + 0.5*MW["O2"]

def gen_Y_str(Y_K, debug=False):
    
    #f are mass fractions in the emulsion
    recepie_em = {
        'rho_em': 1.155, #g/ml
        'f_K2CO3': 0.15577,
        'f_fuel': 0.2,
        'percent_K_to_K2CO3': 0.566
    }
    recepie_em['f_water'] = 1 - recepie_em['f_K2CO3'] -  recepie_em['f_fuel']    
    
    Y_seed = Y_K*MW["K2CO3"]/(2*MW["K"])
    Y_K = Y_seed*(   MW["K"]/MW["K2CO3"] )
    Y_CO2 = Y_seed*( MW["CO2"]/MW["K2CO3"] )
    Y_KO =  Y_seed*( MW["KO"]/MW["K2CO3"] )
    Y_H2O = Y_seed*(recepie_em['f_water']/recepie_em['f_K2CO3'])
#     Y_H2O = 0
    
    Y_em = Y_K + Y_CO2 + Y_KO + Y_H2O
    
#     print("Y_em: " + str(Y_em))
    
    phi = 0.8
    
    # C12H26 + (13/2 + 12) O2 => 13H2O + 12CO2
    OtoF = (13.0/2.0 + 12.0)
    OtoF_mass = OtoF*MW["O2"]/MW["C12H26"]

    # oxygen-to-fuel
    alpha = 1/OtoF_mass
    
    Y_O2 = (1-Y_em)/(1+alpha*phi)
    Y_fuel = Y_O2*alpha*phi  

    Y_str = "C12H26:{:} O2:{:} K:{:} KO:{:} CO2:{:}, H2O:{:}".format(Y_fuel, Y_O2, Y_K, Y_KO, Y_CO2, Y_H2O)

    return Y_str

def H_removal(Y_str, mdot, q_wall_combustor, q_wall_channel, debug=False):
    """Perform the 3-stage enthalpy removal process. Returns T, nK, and simga after the final stage (barrel outlet)"""
    
    T_in = 300.0
    p_comb = 6e5
    p_out = 1e5
    T_ref = 298.15
    
    #step 2: lose heat to KE increase
    q_KE = (1/2)*mdot*(1.5e3)**2

    q_walls = q_wall_combustor + q_wall_channel

    q_total = q_wall_combustor + q_KE + q_wall_channel

    if debug:
        print("\nenthalpy [MJ/kg]")
        print("combustor wall heat tranfer | {:11.2e}".format(q_wall_combustor/mdot/1e6))
        print("channel wall heat tranfer | {:11.2e}".format(q_wall_channel/mdot/1e6))
        print("Kinetic energy loss | {:11.2e}".format(q_KE/mdot/1e6))
        print("Total energy loss to walls  | {:11.2e}".format(q_walls/mdot/1e6))
        print("Total energy loss | {:11.2e}".format(q_total/mdot/1e6))

    g.TPY = T_in, p_comb, Y_str
    # enthalply
    cp_cold = g.cp_mass
    g.equilibrate("HP")
    T_ad = g.T
    h_comb = g.enthalpy_mass
    cp_comb = g.cp_mass

    # Step1: Loss in combustion chamber to walls. pressure remains combustor pressure. remaining at combustor temperature does not seem to affect result
    h_1 = h_comb - (q_wall_combustor/mdot)
    g.HPX = h_1, p_comb, g.X
    g.equilibrate("HP")
    T_1 = g.T
    cp_1 = g.cp_mass
    nK_1 = g.X[g.species_index('K')]*g.density_mole*6.02e26

    # Step 2: Loss from kinetic enegy, the pressure drops to atmospheric
    h_2 = h_1 - (q_KE/mdot)
    g.HPX = h_2, p_out, g.X
    g.equilibrate("HP")
    T_2 = g.T
    cp_2 = g.cp_mass
    nK_2 = g.X[g.species_index('K')]*g.density_mole*6.02e26

    # Step 3: Loss to channel walls
    h_3 = h_2 - (q_wall_channel/mdot)
    g.HPX = h_3, p_out, g.X
    g.equilibrate("HP")
    T_3 = g.T
    cp_3 = g.cp_mass
    
    T_outlet = T_3
    nK_outlet = g.X[g.species_index('K')]*g.density_mole*6.02e26
    
    if nK_outlet == 0.0:
        sigma_outlet = 0.0
    else:
        sigma_outlet = electron_trans.conductivity(g)
    

    g.TPX = T_ref, p_out, g.X
    g.equilibrate("TP")
    h_ref = g.enthalpy_mass

    
    if debug:
        print("temperature [K]")
        print("inlet                       | {:11.2f}".format(T_in))
        print("adiabatic flame             | {:11.2f}".format(T_ad))
        print("Stage 1                     | {:11.2f}".format(T_1))
        print("Stage 2                     | {:11.2f}".format(T_2))
        print("Stage 3                     | {:11.2f}".format(T_3))
        
        print("\nnK [#/m^3]")
        print("Stage 1                     | {:11.2e}".format(nK_1))
        print("Stage 2                     | {:11.2e}".format(nK_2))
        print("Stage 3                     | {:11.2e}".format(nK_outlet))
        
        print("\nenthalpy [MJ/kg]")
        print("adiabatic                   | {:11.2e}".format(h_comb/1e6))
        print("combustor wall heat tranfer | {:11.2e}".format(q_wall_combustor/mdot/1e6))
        print("Stage 1                     | {:11.2e}".format(h_1/1e6))
        print("Kinetic energy loss         | {:11.2e}".format(q_KE/mdot/1e6))
        print("Stage 2                     | {:11.2e}".format(h_2/1e6))
        print("channel wall heat tranfer   | {:11.2e}".format(q_wall_channel/mdot/1e6))
        print("Stage 3                     | {:11.2e}".format(h_3/1e6))
        print("reference                   | {:11.2e}".format(h_ref/1e6))

        print("\n% heat transfer walls     | {:11.2f}".format( 100*q_walls/(h_comb - h_ref)/mdot))
        print("\n% heat transfer KE        | {:11.2f}".format( 100*q_KE/(h_comb - h_ref)/mdot))
        print("\n% heat transfer total     | {:11.2f}".format( 100*q_total/(h_comb - h_ref)/mdot))
        print("\nspecific heat  [kJ/kg-K]")
        print("inlet                       | {:11.2e}".format(cp_cold/1e3))
        print("adiabatic                   | {:11.2e}".format(cp_comb/1e3))
        print("outlet                      | {:11.2e}".format(cp_3/1e3)) #This was originally 'cp_out' which was not defined...assumed meant cp_3 but slightly different value than old notebook

    return T_outlet, nK_outlet, sigma_outlet

def calc_outlet(Y_K, mdot, q_wall_combustor, q_wall_channel, debug=False):
    """combination function to generate the composition and run enthalpy removal calculations"""
    Y_str = gen_Y_str(Y_K)
    T, nK, sigma = H_removal(Y_str, mdot, q_wall_combustor, q_wall_channel, debug=debug)
    return T, nK, sigma

#Run the case in the initial notebook to ensure the same result
calc_outlet(0.01, 9.32e-3, 19.4e3, 6.2e3, debug=True)

#Load in calorimetry data and assign test cases
ds_calor = dsst['calor_combined']
ds_calor = analysis.ct.assign_tc_general(ds_calor, da_ct)
ds_calor = ds_calor.mean('time', keep_attrs=True)

#Run through combinations of coordinates with xyzpy to calculatate outlet properties

def calc_outlet_xyz(date, Kwt, tf):
    """
    Function to calculate outlet properties with xyzpy. Needs to be able to
    handle coordinate combinations with missing values
    """
    ds_sel = ds_calor.sel(date=date, Kwt=Kwt, tf=tf)
    comb_ht = ds_sel['comb_ht'].item()*1000
    chan_ht = ds_sel['chan_ht'].item()*1000
    if comb_ht != comb_ht:
        return np.nan, np.nan, np.nan
    else:
        T, nK, sigma = calc_outlet(Kwt/100, tf/1000, comb_ht , chan_ht)
    return T, nK, sigma

combos = {
    'date': ds_calor.coords['date'].values,
    'Kwt': ds_calor.coords['Kwt'].values,
    'tf': ds_calor.coords['tf'].values
}

r = xyzpy.Runner(calc_outlet_xyz,
    var_names = ['T', 'nK_cant', 'sigma'])
ds_out = r.run_combos(combos)

ds_out['nK_cant'].attrs = dict(long_name='$n_{K,cantera}$', units = '$\\#/m^3$')
ds_out['T'].attrs = dict(long_name='$T_{outlet}$', units = 'K')
ds_out['sigma'].attrs = dict(long_name='$\\sigma_{outlet}$', units = 'S/m')


L = 0.1 #m
A = np.pi*(0.005)**2 #m^2

G_cantera = ds_out['sigma']*(A/L)
G_cantera.attrs = dict(long_name='Conductance', units='S')

R_cantera = 1/G_cantera
R_cantera.attrs = dict(long_name='$R_{cantera}$', units='Ohm')

ds_out = ds_out.assign(R_cantera=R_cantera)
ds_out = ds_out.assign(G_cantera=G_cantera)

ds_cantera = xr.merge([ds_out, ds_calor])

for coord in ds_cantera.coords:
    ds_cantera.coords[coord].attrs = ds_calor.coords[coord].attrs

ds_cantera.to_netcdf(os.path.join(dataoutputfolder, 'ds_cantera.cdf'))


#Convert CFD data
cfd_data = pd.read_csv(os.path.join(finalanalysisfolder,'Data', 'CFD_2D_21July20.csv'), index_col= [1,2]).drop('case', axis = 1)

ds_cfd = xr.Dataset.from_dataframe(cfd_data)

rename_map = {
    'Res(Ohm)': 'resistance',
    'n_K_ave[#/m3]' : 'nK',
    'QwallChannel[kW]': 'chan_ht',
    'QwallComb[kW]': 'comb_ht',
    'T_center(K)': 'T_outlet',
    'K(wt%)' : 'Kwt',
    'mdot(g/s)': 'tf'
}

ds_cfd =ds_cfd.rename(rename_map)

for var in ds_cfd.data_vars:
    if var not in list(rename_map.values()):
        ds_cfd = ds_cfd.drop(var)

ds_cfd.coords['Kwt'].attrs = dict(long_name='K wt% CFD')
ds_cfd.coords['tf'].attrs = dict(long_name='Total Mass Flow CFD', units = 'g/s')
ds_cfd['resistance'].attrs = dict(long_name='Resistance CFD', units = 'ohm')
ds_cfd['nK'].attrs = dict(long_name='${n_K, CFD}$', units = '$\\#/m^3$')
ds_cfd['chan_ht'].attrs = dict(long_name='Channel Heat Transfer CFD', units = 'kW')
ds_cfd['comb_ht'].attrs = dict(long_name='Combustor Heat Transfer CFD', units = 'kW')
ds_cfd['T_outlet'].attrs = dict(long_name='Outlet Temperature CFD', units = 'K')


ds_cfd.to_netcdf(os.path.join(dataoutputfolder, 'ds_cfd.cdf'))