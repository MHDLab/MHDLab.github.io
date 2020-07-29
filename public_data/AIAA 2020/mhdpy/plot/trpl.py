# -*- coding: utf-8 -*-
# TODO: fix function and variable names
# third party imports
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import animation, rc
from matplotlib.collections import PolyCollection

mpl.rcParams.update({'font.size': 18})

def cutspectraldf(
        spectraldf,
        wl1=None,
        wl2=None
):
    """
    TODO: improve documentation
    cut up a spectral dataframe between two wavelengths.

    Parameters
    ----------
    spectraldf : pd.DataFrame
    wl1
    wl2

    Returns
    -------
    spectra_cut : pd.DataFrame
    """
    wavelength = spectraldf.index
    if wl1 is None:
        wl1 = wavelength.min()
    if wl2 is None:
        wl2 = wavelength.max()

    idx1 = wavelength.get_loc(wl1, method='nearest')
    idx2 = wavelength.get_loc(wl2, method='nearest')

    spectra_cut = spectraldf.iloc[idx1:idx2]

    return spectra_cut


def maxandarea(spectra_cut):
    """
    calculate the area and maximum of a peak in a cut spectral dataframe

    Parameters
    ----------
    spectra_cut : pd.DataFrame
    """
    areas = pd.Series(index=spectra_cut.columns)
    maximums = pd.Series(index=spectra_cut.columns)

    wavelength_cut = spectra_cut.index
    for gatedelay in spectra_cut.columns:
        areas[gatedelay] = np.trapz(spectra_cut[gatedelay], wavelength_cut)
        maximums[gatedelay] = spectra_cut[gatedelay].max()

    return areas, maximums



class SpectraPlot:
    """
    plot of a simple intensity vs wavelength spectra
    """
    def __init__(
            self,
            wavelength,
            spectra,
            label=None
    ):
        """
        TODO: add documentation

        Parameters
        ----------
        wavelength
        spectra
        label
        """
        self.fig, self.ax1 = plt.subplots(figsize=(8, 6))
        self.ax1.plot(
            wavelength,
            spectra,
            label=label
        )
        self.ax1.set_xlabel("Wavelength (nm)")
        self.ax1.set_ylabel("Intensity (a.u.)")


class PLplot_new:
    """
    plot of a PL decay. First initializes the figure by adding a laser
    profile, then you call add_decay to add further PL decay plots
    """
    def __init__(
            self,
            laserseries
    ):
        """
        TODO: add documentation

        Parameters
        ----------
        laserseries
        """
        self.fig, self.ax1 = plt.subplots(figsize=(8, 6))

        self.ax1.set_xlabel("Gate Delay (ns)")
        self.ax1.set_ylabel("$Delta$ PL Intensity (Normalized)")
        self.ax1.tick_params('y')
        self.ax1.set_yscale('log')

        self.ax2 = self.ax1.twinx()
        self.ax2.set_ylabel("Laser Intensity (Normalized)")
        self.ax2.tick_params('y')
        self.ax2.set_yscale('log')

        self.legend = self.ax1.legend()
        self.legend.set_visible(False)

        self.lns = self.ax2.plot(
            laserseries.index,
            laserseries,
            '--',
            color='gray',
            label='Laser profile'
        )

        self.setlegend()
        self.fig.suptitle(
            'PL Plot',
            y=1
        )
        self.fig.tight_layout()

    def add_decay(
            self,
            spectraldf,
            label,
            method="max",
            wl1=None,
            wl2=None,
            color=None
    ):
        """
        TODO: add documentation

        Parameters
        ----------
        spectraldf
        label
        method
        wl1
        wl2
        color

        Returns
        -------

        """
        spectra_cut = cutspectraldf(
            spectraldf,
            wl1,
            wl2
        )

        areas, maximums = maxandarea(spectra_cut)

        if color is None:
            colorlist = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w']
            color = colorlist[len(self.lns)]

        if method == "max":
            ln = self.ax1.plot(
                spectra_cut.columns,
                maximums,
                '.-',
                color=color,
                label=label
            )
        elif method == "area":
            ln = self.ax1.plot(
                spectra_cut.columns,
                areas,
                '.-',
                color=color,
                label=label
            )
        else:
            raise ValueError(
                'Bad method. Use `max` or `area`'
            )

        self.lns = self.lns + ln

        self.legend.remove()
        self.setlegend()

    def setlegend(self):
        """
        iterate through lines and make a label
        """
        labs = [l.get_label() for l in self.lns]
        self.legend = self.ax1.legend(
            self.lns,
            labs,
            loc=0
        )
        self.legend.set_visible(True)


class PLplot():
    """
    TODO: add documentation
    """
    def __init__(
            self,
            Laser,
            Lasertime,
            peak1,
            peak2,
            PLtime
    ):
        """
        TODO: add documentation

        Parameters
        ----------
        Laser
        Lasertime
        peak1
        peak2
        PLtime
        """
        self.fig, self.ax1 = plt.subplots(figsize=(8, 6))
        ln1 = self.ax1.plot(
            PLtime,
            peak1,
            'b.',
            label='Peak 1'
        )
        ln2 = self.ax1.plot(
            PLtime,
            peak2,
            'g.',
            label='Peak 2'
        )

        self.ax2 = self.ax1.twinx()

        self.ax2.set_ylabel("Laser Intensity (Normalized)")
        self.ax2.tick_params('y')

        plt.legend()

        ln3 = self.ax2.plot(
            Lasertime,
            Laser,
            'r',
            label='Laser profile'
        )

        self.ax1.set_xlabel("Gate Delay (ns)")

        # Make the y-axis label, ticks and tick labels match the line color.
        self.ax1.set_ylabel("$Delta$ PL Intensity (Normalized)")
        self.ax1.tick_params('y')

        self.fig.suptitle(
            'Potassium HVOF PL',
            y=1
        )
        self.fig.tight_layout()

        lns = ln1 + ln2 + ln3
        labs = [l.get_label() for l in lns]
        self.ax1.legend(
            lns,
            labs,
            loc=0
        )

        self.ax2.set_yscale('log')
        self.ax1.set_yscale('log')


def spectral_anim(
        RawData_Frames,
        spectra_wl,
        ts,
        interval=15,
        time_template = 'Gate Delay = %.1fns'
):
    """
    Matplotlib Animation Example
    
    author: Jake Vanderplas
    email: vanderplas@astro.washington.edu
    website: http://jakevdp.github.com
    license: BSD
    Please feel free to use and modify this, but keep the above information.
    Thanks!

    TODO: add documentation

    Parameters
    ----------
    RawData_Frames
    spectra_wl
    ts
    interval

    Returns
    -------

    """

    xs = spectra_wl

    # First set up the figure, the axis, and the plot element we want to animate
    fig = plt.figure()
    ax = plt.axes(
        xlim=(xs[0], xs[-1]),
        ylim=(0, 1.1)
    )

    line, = ax.plot(
        [],
        [],
        lw=2
    )

    
    time_text = ax.text(
        0.05,
        0.9,
        '',
        transform=ax.transAxes
    )

    fig.tight_layout()

    #
    def init():
        """
        TODO: improve documentation

        initialization function: plot the background of each frame

        Returns
        -------
        line
        """
        line.set_data([], [])
        time_text.set_text('')
        ax.set_ylabel("Normalized Emission Intensity (a.u.)")
        ax.set_xlabel("Wavelength (nm)")
        return line,

    def animate(i):
        """
        TODO: improve documentation

        animation function.  This is called sequentially

        Parameters
        ----------
        i : int

        Returns
        -------

        """
        y = RawData_Frames.iloc[:, i]#.as_matrix()
        y = y / RawData_Frames.max().max()
        line.set_data(
            xs,
            y
        )
        if time_template is not None:
            time_text.set_text(time_template % ts[i])
        else:
            time_text.set_text(str(ts[i].astype('datetime64[ms]')))
        return line, time_text

    # call the animator.
    # blit=True means only re-draw the parts that have changed.
    anim = animation.FuncAnimation(
        fig,
        animate,
        init_func=init,
        frames=len(ts),
        interval=interval,
        blit=True
    )

    # # equivalent to rcParams['animation.html'] = 'html5'
    # rc(
    #     'animation',
    #     html='html5'
    # )

    return anim

import numpy as np

def spectral_anim_xr(
        da,
        interval=15,
        time_template = 'Gate Delay = %.1fns'
):


    xs = da.coords['wavelength'].values
    ts = da.coords['time'].values

    # First set up the figure, the axis, and the plot element we want to animate
    fig, ax = plt.subplots()

    lines = da.isel(time=0).plot(ax=ax)

    line = lines[0]

    
    time_text = ax.text(
        0.05,
        0.9,
        '',
        transform=ax.transAxes
    )

    ax.set_ylim(0,1.1*da.max().item())
    ax.set_title('')

    fig.tight_layout()

    #
    def init():
        line.set_ydata([np.nan]*len(ts))
        return line,

    def animate(i):
        """
        TODO: improve documentation

        animation function.  This is called sequentially

        Parameters
        ----------
        i : int

        Returns
        -------

        """
        y = da.isel(time=i).values
        # y = y / RawData_Frames.max().max()
        line.set_data(
            xs,
            y
        )
        if time_template is not None:
            time_text.set_text(time_template % ts[i])
        else:
            time_text.set_text(str(ts[i].astype('datetime64[ms]')))
        return line, time_text

    # call the animator.
    # blit=True means only re-draw the parts that have changed.
    anim = animation.FuncAnimation(
        fig,
        animate,
        init_func=init,
        frames=len(ts),
        interval=interval,
        blit=True
    )

    # # equivalent to rcParams['animation.html'] = 'html5'
    # rc(
    #     'animation',
    #     html='html5'
    # )

    return anim


def PL_waterfall(
        RawData_Frames,
        spectra_wl,
        ts
):
    """
    TODO: add documentation

    Parameters
    ----------
    RawData_Frames
    spectra_wl
    ts

    Returns
    -------

    """
    fig = plt.figure()
    ax = fig.gca(projection='3d')

    xs = spectra_wl
    verts = []
    zs = ts
    i = 0
    numexposures = len(zs) - 1
    for _ in zs:
        ys = RawData_Frames.iloc[:, numexposures - i].as_matrix()
        i = i + 1
        ys[0], ys[-1] = 0, 0
        verts.append(list(zip(xs, ys)))

    poly = PolyCollection(
        verts,
        facecolors=(1, 1, 1, 0),
        edgecolors=(0, 0, 1, 0.5)
    )
    ax.add_collection3d(
        poly,
        zs=zs,
        zdir='y'
    )

    ax.set_xlabel('X')
    ax.set_xlim3d(xs[0], xs[-1])
    ax.set_ylabel('Y')
    ax.set_ylim3d(zs[0], zs[-1])
    ax.set_zlabel('Z')
    ax.set_zlim3d(0, RawData_Frames.max().max())

    ax.view_init(20, 300)
    plt.show()
