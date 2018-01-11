# -*- coding: utf-8 -*-
"""Code for Zefir Reader node."""

import zefir
zefir.configuration.configure()

from nwave.effects.houdini.DigitalAssets.ZefirReader.View import View
from nwave.effects.houdini.DigitalAssets.ZefirReader.Model import Model
from nwave.effects.houdini.DigitalAssets.ZefirReader.Controller import \
    Controller


def main(node):
    """Create the model, view and controller. Return the controller."""
    return Controller(Model(), View(node))
