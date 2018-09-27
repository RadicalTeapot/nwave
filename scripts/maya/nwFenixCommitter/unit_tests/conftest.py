# -*- coding: utf-8 -*-
"""Unit tests for the Fenix Committer."""

import zefiro
import os
import maya.standalone

z = zefiro.Zefiro(project='corgi')
if z.auth_token is None:
    z.authenticate(store=True)
os.environ['ZEFIRO_AUTH_TOKEN'] = z.auth_token
maya.standalone.initialize()

import maya.cmds
import pytest

from nwave.effects.tools.nwFenixCommitter.Controller import Controller
from nwave.effects.tools.nwFenixCommitter.Model import Model
from nwave.effects.tools.nwFenixCommitter.Settings import Settings

from nwave.effects.tools.nwFXTDTools.PipelineHelper import PipelineHelper
import zefir


class Scene(object):
    """Simple data class."""

    def __init__(self, assets=[]):
        """Initialize the data class with asset data."""
        self.assets = assets


@pytest.fixture
def mvc(mocker):
    """Yield fixture for controller, model and view."""
    model = Model()
    view = mocker.MagicMock()
    controller = Controller(model, view)

    yield model, view, controller


@pytest.fixture
def settings():
    """Yield fixture for Settings."""
    yield Settings


@pytest.fixture
def scene():
    """Yield fixture for a mock scene."""
    maya.cmds.file(new=True, f=True)
    jelly = PipelineHelper.getAsset(
        'biff_jelly',
        zefir.STAGES.FX_SIMULATION,
        '999', '0010'
    )
    generic_asset = PipelineHelper.getAsset(
        'fx_generic_asset',
        zefir.STAGES.FX_SIMULATION,
        '999', '0010'
    )
    fire_candles = PipelineHelper.getAsset(
        'firecandles',
        zefir.STAGES.FX_SIMULATION,
        '999', '0010'
    )

    scene = Scene(assets=[jelly, generic_asset, fire_candles])

    yield scene
