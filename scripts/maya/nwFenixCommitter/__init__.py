# -*- coding: utf-8 -*-
"""Tool description."""

from Controller import Controller as c
from Model import Model
from View import View

import maya.cmds as mc

from nwave.effects.tools.nwFXTDTools.getMayaWindow import getMayaWindow


def main():
    """Launch the Fenix Committer."""
    if mc.window(View.object_name, q=True, ex=True):
        mc.deleteUI(View.object_name)

    view = View(getMayaWindow())
    controller = c(Model(), view)

    if controller.valid:
        view.show()
