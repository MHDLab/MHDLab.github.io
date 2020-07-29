# -*- coding: utf-8 -*-
# TODO: improve readability of function and variable names
"""
Functions for use in Data Analysis
"""

# third party imports
import numpy as np
import re


def find_nearest(
        a,
        a0
):
    """"
    Element in nd array `a` closest to the scalar value `a0`

    Parameters
    ----------
    a : np.ndarray
        Array of data
    a0 : float
        Value to search array for the closest value to

    Returns
    -------
    idx : int
        Index corresponding to the data point closest to the desired input value
    """
    idx = np.abs(a - a0).argmin()
    return idx


def convertpstring(string):
    """
    converts a string of the form 7p5 to 7.5 float

    Parameters
    ----------
    string : str
        String needing replacement

    Returns
    -------
    f : float
        Converted value
    """

    regex = r"(\d+)p(\d+)"
    m = re.search(regex, string)
    if m is not None:
        stringnew = m.groups()[0] + "." + m.groups()[1]
        f = (float(stringnew))
    else:
        f = (float(string))

    return f