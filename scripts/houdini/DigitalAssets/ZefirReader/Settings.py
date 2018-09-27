# -*- coding: utf-8 -*-
"""Settings of the Zefir reader."""

import hou
import zefir


class Settings(object):
    """Class for the settings of the Zefir reader.

    Attributes
    ----------
    CATEGORIES: dict
        Asset categories names and their zefir asset_types.
    AUTHORIZED_STAGES: dict
        Stages the can be loaded for each type of asset.
    COLORS: dict
        Colors for nodes and network boxes for each asset type.

    """

    # Asset categories names and their zefir asset_types
    CATEGORIES = {
        zefir.ASSET_TYPES.CAMERA: 'camera',
        zefir.ASSET_TYPES.EFFECT: 'effect',
        zefir.ASSET_TYPES.CHARACTER: 'character',
        zefir.ASSET_TYPES.PROP: 'prop',
        zefir.ASSET_TYPES.SET_ELEMENT: 'set_element',
        zefir.ASSET_TYPES.INSTANCES: 'instances'
    }

    # Stages the can be loaded for each type of asset
    AUTHORIZED_STAGES = {
        zefir.ASSET_TYPES.CAMERA: [
            zefir.STAGES.CAMERA_ANIMATION_DATA
        ],

        zefir.ASSET_TYPES.EFFECT: [
            zefir.STAGES.FX_SIMULATION
        ],

        zefir.ASSET_TYPES.CHARACTER: [
            zefir.STAGES.ANIMATION_ALEMBIC
        ],

        zefir.ASSET_TYPES.PROP: [
            zefir.STAGES.ANIMATION_ALEMBIC
        ],

        zefir.ASSET_TYPES.INSTANCES: [
            zefir.STAGES.INSTANCES
        ],

        zefir.ASSET_TYPES.SET_ELEMENT: [
            zefir.STAGES.ANIMATION_PROXY,
            zefir.STAGES.DISPLACEMENT_VISUALIZATION,
            zefir.STAGES.STATIC_TRANSFORMATION
        ]
    }

    # Colors for nodes and network boxes for each asset type.
    COLORS = dict([
        (zefir.ASSET_TYPES.CAMERA, hou.Color(0.8, 0.016, 0.016)),
        (zefir.ASSET_TYPES.EFFECT, hou.Color(0.573, 0.353, 0.)),
        (zefir.ASSET_TYPES.CHARACTER, hou.Color(0.302, 0.525, 0.114)),
        (zefir.ASSET_TYPES.PROP, hou.Color(0.094, 0.369, 0.69)),
        (zefir.ASSET_TYPES.INSTANCES, hou.Color(0.322, 0.259, 0.58)),
        (zefir.ASSET_TYPES.SET_ELEMENT, hou.Color(0.624, 0.329, 0.396))
    ])
