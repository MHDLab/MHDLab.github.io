# -*- coding: utf-8 -*-
"""
Various functions for conversions of time objects
"""
# stdlib imports
from __future__ import unicode_literals
import datetime

# third party imports
import pandas as pd
import numpy as np
import pytz

def np64_to_utc(np64_dt):
    """
    converts a np64 datetime into a datetime datetime with utc timezone,
    converting through a timestamp first.

    Parameters
    ----------
    np64_dt : np.datetime64

    Returns
    -------
    datetime.datetime
    """
    return datetime.datetime.utcfromtimestamp(
        np64_to_unix(np64_dt)
    ).replace(tzinfo=pytz.utc)


def np64_to_unix(
        timestamp,
        unit='s'
):
    """
    converts a np64 datetime to a unix timestamp

    Parameters
    ----------
    timestamp : np.datetime64
    unit : str

    Returns
    -------
    np.float64
    """
    return (timestamp - np.datetime64(
        '1970-01-01T00:00:00Z',
        dtype='M8[' + unit + ']'
    )) / np.timedelta64(1, unit)


def datetime_to_unix(timestamp):
    """
    converts a datetime datetime into a unix timestamp

    Parameters
    ----------
    timestamp : datetime.datetime

    Returns
    -------
    float
    """
    return (timestamp - datetime.datetime(
        1970,
        1,
        1,
        tzinfo=pytz.utc
    )).total_seconds()


def labview_to_unix(timestamps):
    """
    converts a labview timestamp into a unix timestamp

    Parameters
    ----------
    timestamps : list

    Returns
    -------
    list
    """
    return list(map(lambda x: x - 2082844800, timestamps))


def nearest_timeind(
        timearray,
        pivot
):
    """
    Returns the nearest index in a time array corresponding to the pivot time.
    
    The method varies depending on the datatype. datetime.datetime objects
    require lambda functions to convert an array to timestamps. numpy
    datetimes can just undergo simple element by element subtraction, which
    is much quicker.
    """
    if isinstance(pivot, datetime.datetime):
        seconds = np.array(
            list(
                map(
                    lambda x: abs(x - pivot).total_seconds(),
                    timearray
                )
            )
        )
    elif isinstance(pivot, np.datetime64):
        seconds = np.abs(timearray - pivot)
    else:
        raise TypeError(
            'pivot has a bad dtype. '
            'dtype must be `datetime.datetime` or `np.datetime64`'
        )
    return seconds.argmin()

def save_cuttimes_list(cuttimes, filepath):
    """converts a list of cuttimes (pd Timestamps) into a dataframe and writes to csv without index"""
    timelist = [[sl.start, sl.stop] for sl in cuttimes]
    df = pd.DataFrame(timelist, columns=['start', 'stop'])
    df.to_csv(filepath, index=False, float_format="%d", line_terminator='\n',)

def load_cuttimes(filepath):
    """loads cuttimes list into array of slices"""
    df = pd.read_csv(filepath, parse_dates=['start', 'stop'])

    cuttimelist = []
    for timelist in df.values:
        cuttimelist.append(slice(timelist[0],timelist[1]))

    return cuttimelist