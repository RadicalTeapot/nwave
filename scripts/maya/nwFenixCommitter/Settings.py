# -*- coding: utf-8 -*-
"""Settings of the Fenix Committer."""

import platform


class Settings(object):
    """Class for the settings of the Fenix Committer."""

    _WIN_TEMD_DIR = "C:/tmp/mayaCaches/"
    _UNIX_TEMP_DIR = "/usr/tmp/mayaCaches/"
    TEMP_DIR = {
        'windows': _WIN_TEMD_DIR,
        'linux': _UNIX_TEMP_DIR,
    }[platform.system().lower()]

    MUSTER_FOLDER = "/effects/commit"
