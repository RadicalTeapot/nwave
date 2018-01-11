# -*- coding: utf-8 -*-
"""Global FX scripts variables."""
import os

################################
#    SETTING GLOBAL FX VARS    #
################################
FX_TD_EMAIL = "mathiasc@nwavedigital.com"

FX_DATABASE_NAME = "database.db"
FX_MOST_USED_TABLE = "most_used"

FX_MENU_DATA = "fx_menu.json"
FX_SHELF_DATA = "fx_shelf.json"

FX_TEAM_NAME = 'EFFECTS'

#############################
#    GLOBAL FX FUNCTIONS    #
#############################
def getPathToFXTools():
    """Return the path to the root of FX scripts folder.

    Returns
    -------
    string:
        Path to the root of the script FX folder.

    Raises
    ------
    IOError
        If effect module file cannot be found.

    """
    effects_module_path = os.environ['FX_MODULE']
    files = os.listdir(effects_module_path)
    if not files:
        raise IOError("Cannot find effect module file.")
    effects_file = os.path.normpath(
        os.path.join(effects_module_path, files[0])
    )

    effects_path = ""
    with open(effects_file, 'r') as f:
        effects_path = f.read().strip().split()[-1]
    return effects_path


def getPathToFXDatabase():
    """Return the fx tool usage database.

    Returns
    -------
    str
        The path to the fx tools usage database.

    Raises
    -------
    IOError
        If database cannot be found.

    """
    tools_path = getPathToFXTools()
    database_path = os.path.join(tools_path, "_internal", FX_DATABASE_NAME)
    if not os.path.exists(database_path):
        raise IOError("Database not found at {0}".format(database_path))

    return database_path
