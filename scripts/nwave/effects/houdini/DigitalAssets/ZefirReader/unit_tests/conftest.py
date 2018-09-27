# -*- coding: utf-8 -*-
"""DOCSTRING."""

import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(__file__),
    '..', '..'
)))

sys.path.insert(1, os.path.abspath(os.path.join(
    os.path.dirname(__file__),
    '..'
)))

from ZefirReader import Controller
from ZefirReader import Model
from ZefirReader import View
from ZefirReader import zefir
from Settings import Settings


class Parm(object):
    def __init__(self):
        self._value = None

    def set(self, value):
        self._value = value

    def evalAsInt(self):
        return int(self._value)

    def evalAsString(self):
        return str(self._value)

    def pressButton(self):
        pass


class Node(object):
    def __init__(self):
        self._parms = dict()

    def parm(self, name):
        if name not in self._parms:
            self._parms[name] = Parm()
        return self._parms[name]

    def name(self):
        return 'node'

@pytest.fixture
def node():
    return Node()


@pytest.fixture
def mvc():
    """Return the model, view and controller and node of the tool."""
    view = View(Node())
    model = Model()
    controller = Controller(model, view)

    yield (model, view, controller)


@pytest.fixture
def settings():
    return Settings


@pytest.fixture
def shot_instance(settings, mocker):
    shot_instance = mocker.MagicMock()
    shot_instance.id = 10
    shot_instance.string_repr = mocker.MagicMock(return_value='test')

    component = mocker.MagicMock()
    component.stage = settings.AUTHORIZED_STAGES[
        zefir.ASSET_TYPES.CHARACTER
    ][0]
    component.id = 20
    component.variant = 1

    uv_component = mocker.MagicMock()
    uv_component.stage = zefir.STAGES.UVS
    uv_component.variant = 1
    uv_component.id = 30

    uv_asset_component = mocker.MagicMock()
    uv_asset_component.stage = zefir.STAGES.UVS
    uv_asset_component.variant = 1
    uv_asset_component.id = 40

    shot_instance.asset.components = [component, uv_asset_component]
    shot_instance.components = [component, uv_component]

    return shot_instance
