# -*- coding: utf-8 -*-
# TODO: improve readability of function and variable names
"""
Functions for getting lists/dicts of filepaths
"""
# stdlib imports
import os
from pathlib import Path


def gen_path(
        basedir='nas',
        *paths
):
    """
    Generates file path strings to commonly used folders.

    Parameters
    ---------- 
    basedir : str
        string specificying base directory for filepath. alternatively use one
        of the following presets:
            'nas'
                'Z\\Data'. If the nas drive cannot be found onedrive is tried
            'onedrive'
                attempts to find it using the 'known folders' in windows.
                Assumes folder structure of `Onedrive\\MHD Common Drive\\Data\\'
    
    paths : str
        optional set of comma separated strings to join to the folder path.
        If the first string is one of the following defaults these paths will
        be added first:
            'raw': Data//Raw Data
            'proc': Data//Processed Data

    Returns
    --------
    str
        string of filepath
    """
    p = ''

    if basedir != 'nas' and basedir != 'onedrive':
        p = basedir
    
    if basedir == 'nas':
        p = "Z:\\"
        try:
            os.listdir(p)
        except FileNotFoundError:
            print('cant find NAS drive, trying onedrive')
            basedir = 'onedrive'

    if basedir == 'onedrive':
        try:
            p = get_onedrive_folder()
        except OSError:
            print(
                'error when trying to find onedrive folder, '
                'defaulting to user dir'
            )
            p = os.path.join(str(Path.home()), 'OneDrive')

        # p = os.path.join(p, "MHD Common Drive\\Data\\")


    if basedir == 'sharepoint':
        p = os.path.join(str(Path.home()), 'National Energy Technology Laboratory', 'MHD Lab - Documents')

    if basedir == 'mhdlab': 
        p = os.path.join(str(Path.home()), 'Git', 'MHDLab')

    if len(paths) > 0:
        paths = list(paths)
        firstpath = paths[0]

        if firstpath == 'raw':
            p = os.path.join(p, "HVOF Booth\\")
            del paths[0]
        # elif firstpath == 'proc':
        #     p = os.path.join(p, "Processed Data\\")
        #     del paths[0]

        if firstpath == 'lee':
            p = os.path.join(p, 'Team Member Files', 'Lee')
            del paths[0]

        p = os.path.join(p, *paths)

    return p


#Change the definition of "get_onedrive_folder" based on operating system
# https://stackoverflow.com/questions/35851281/python-finding-the-users-downloads-folder
if os.name == 'nt':
    import ctypes
    from ctypes import windll, wintypes
    from uuid import UUID

    # ctypes GUID copied from MSDN sample code
    class GUID(ctypes.Structure):
        _fields_ = [
            ("Data1", wintypes.DWORD),
            ("Data2", wintypes.WORD),
            ("Data3", wintypes.WORD),
            ("Data4", wintypes.BYTE * 8)
        ]

        def __init__(self, uuidstr):
            uuid = UUID(uuidstr)
            ctypes.Structure.__init__(self)
            self.Data1, self.Data2, self.Data3, \
                self.Data4[0], self.Data4[1], rest = uuid.fields
            for i in range(2, 8):
                self.Data4[i] = rest >> (8 - i - 1) * 8 & 0xff

    SHGetKnownFolderPath = windll.shell32.SHGetKnownFolderPath
    SHGetKnownFolderPath.argtypes = [
        ctypes.POINTER(GUID), wintypes.DWORD,
        wintypes.HANDLE, ctypes.POINTER(ctypes.c_wchar_p)
    ]

    def _get_known_folder_path(uuidstr):
        pathptr = ctypes.c_wchar_p()
        guid = GUID(uuidstr)
        if SHGetKnownFolderPath(
                ctypes.byref(guid),
                0,
                0,
                ctypes.byref(pathptr)
        ):
            raise ctypes.WinError()
        return pathptr.value

    FOLDERID = '{A52BBA46-E9E1-435f-B3D9-28DAA648C0F6}'

    def get_onedrive_folder():
        return _get_known_folder_path(FOLDERID)
else:
    def get_onedrive_folder():
        home = os.path.expanduser("~")
        print('get onedrive folder function did not get nt for os...')
        return os.path.join(home, "Onedrive")


