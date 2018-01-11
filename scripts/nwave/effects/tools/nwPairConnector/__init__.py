# -*- coding: utf-8 -*-
"""Tool description."""

from Controller import Controller
from Model import Model
from View import View

import maya.cmds as mc

from nwave.effects.tools.nwFXTDTools.getMayaWindow import getMayaWindow


def main():
    """Launch the Pair Connector."""
    if mc.window(View.object_name, q=True, ex=True):
        mc.deleteUI(View.object_name)

    view = View(getMayaWindow())
    Controller(Model(), view)

    view.show()
