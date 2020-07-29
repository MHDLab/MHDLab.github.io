import mhdpy.analysis as analysis
import matplotlib as mpl
import matplotlib.pyplot as plt


def tc_plot(ds, da_ct, grid=True, yspace=3):
    ds_sel = analysis.ct.assign_tc_general(ds,da_ct)

    data_vars = ds_sel.data_vars

    fig,axes = plt.subplots(len(data_vars),1,figsize=(10,yspace*len(data_vars)), sharex=True)
    
    if len(da_ct.coords) > 1:
        raise "only da_ct with one dim supported"
        
    tcdim = list(da_ct.coords.keys())[0]
    

    for i, var in enumerate(data_vars):
        ds[var].plot(ax=axes[i], color = 'grey', linestyle = '--')
        ds_sel[var].plot(hue=tcdim, ax=axes[i])
        if grid: axes[i].grid()
        # axes[i].xaxis.set_major_locator(mpl.dates.SecondLocator(interval=60)) 
        if i == 0:
    #         axes[i].get_legend().set_bbox_to_anchor([1.1,1])
            pass
        else:
            axes[i].get_legend().remove()

    return fig


from xarray.plot.utils import label_from_attrs

#TODO:Make this accept kwargs in general to pass onto plt.errorbar

def xr_errorbar(da_mean, da_std, huedim=None, xerr=None, label=None, capsize = 3):
    """
    Generates an error bar plot from xarray datarrays
    assumes da_mean and da_std are the same shape
    if huedim is unspecified the datarrays should be 1D
    if huedim is specified then datarrays should be 2D and the other dimension will be the xaxis
    """
    
    fig, axes = plt.subplots(1,1)

    if huedim==None:
        plotdim = list(da_mean.coords)[0]
        axes.errorbar(da_mean.coords[plotdim], da_mean.values, da_std.values, xerr=xerr, capsize=capsize, marker = 'o', label= label)

    else:
        plotdim = list(da_mean.isel({huedim:0}).drop(huedim).coords)[0]
        for coord in da_mean.coords[huedim]:
            axes.errorbar(da_mean.sel({huedim:coord}).dropna(plotdim,'all').coords[plotdim],
                        da_mean.sel({huedim:coord}).dropna(plotdim,'all').values,
                        yerr = da_std.sel({huedim:coord}).dropna(plotdim,'all').values,xerr=xerr,
                        capsize = capsize, marker = 'o', label = coord.item())     
        axes.legend(title = label_from_attrs(da_mean.coords[huedim]))       
    
    axes.set_ylabel(label_from_attrs(da_mean))
    axes.set_xlabel(label_from_attrs(da_mean.coords[plotdim]))

    return fig, axes


def xr_errorbar_axes(da_mean, da_std, axes, huedim=None, xerr=None, label=None, capsize = 3):
    """
    Generates an error bar plot from xarray datarrays, 
    plots on an existing ax. quick fix for manuscript,need to improve
    assumes da_mean and da_std are the same shape
    if huedim is unspecified the datarrays should be 1D
    if huedim is specified then datarrays should be 2D and the other dimension will be the xaxis
    """
    

    if huedim==None:
        plotdim = list(da_mean.coords)[0]
        axes.errorbar(da_mean.coords[plotdim], da_mean.values, da_std.values, xerr=xerr, capsize=capsize, marker = 'o', label= label)

    else:
        plotdim = list(da_mean.isel({huedim:0}).drop(huedim).coords)[0]
        for coord in da_mean.coords[huedim]:
            axes.errorbar(da_mean.sel({huedim:coord}).dropna(plotdim,'all').coords[plotdim],
                        da_mean.sel({huedim:coord}).dropna(plotdim,'all').values,
                        yerr = da_std.sel({huedim:coord}).dropna(plotdim,'all').values,xerr=xerr,
                        capsize = capsize, marker = 'o', label = coord.item())     
        axes.legend(title = label_from_attrs(da_mean.coords[huedim]))       
    
    axes.set_ylabel(label_from_attrs(da_mean))
    axes.set_xlabel(label_from_attrs(da_mean.coords[plotdim]))