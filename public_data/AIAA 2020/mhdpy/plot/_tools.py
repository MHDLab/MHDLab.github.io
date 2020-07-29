# -*- coding: utf-8 -*-
# TODO: fix function and variable names

# stdlib imports
import os

# third party imports
import git
import matplotlib as mpl
import pandas as pd
import xarray as xr


class exp_formatter:
    """
    used to format exponentials of ticks
    """

    def __init__(self, exponent, formatstr="{:0=1.3f}"):
        self.exponent = exponent
        self.formatstr = formatstr

    def func(self, value, tick_number):
        return self.formatstr.format(value / 10 ** self.exponent)


# noinspection PyUnresolvedReferences
def dropna(g):
    """
    general dropna function. takes an output from a xarray plotting
    function and applies the correct dropna function.
    """
    if type(g) == list and type(g[0]) == mpl.lines.Line2D:
        for ln in g:
            dropna_ln(ln)
    elif type(g) == xr.plot.facetgrid.FacetGrid:
        for ax in g.axes.flatten():
            dropna_ax(ax)


def dropna_ln(ln):
    """
    drops na for traces on a facet grid
    """
    d = ln.get_data()
    s = pd.Series(d[1], index=d[0]).dropna()
    ln.set_data([s.index, s.values])


def dropna_ax(ax):
    """
    Iterates through all lines in an axes object and removes na values
    """
    lns = ax.lines
    for ln in lns:
        dropna_ln(ln)


def get_label_for_line(line, leg):
    """
    Can't remember what I was using this for but seems useful to keep
    """
    # leg = line.figure.legends[0]
    #     leg = line.axes.get_legend()
    for h, t in zip(leg.legendHandles, leg.texts):
        if h.get_label() == line.get_label():
            return t.get_text()


def get_legend_labels(lns, leg):
    labs = []
    for ln in lns:
        lab = get_label_for_line(ln, leg)
        if lab is not None:
            labs.append(lab)
    return labs


def versioninfo(short=True):
    """
    prints the current filepath and git commit hash. set short = False for
    non-truncated strings
    """
    path = os.path.abspath('')

    if 'MHDLab' in path:
        path = path.split('MHDLab')[1]

    repo = git.Repo(search_parent_directories=True)
    sha = repo.head.object.hexsha

    if short is True:
        path = os.path.split(path)[1]
        sha = sha[0:6]

    text = 'File: ' + path + '\r\n' + 'Hash: ' + sha

    return text
