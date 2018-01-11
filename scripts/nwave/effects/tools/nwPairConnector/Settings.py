# -*- coding: utf-8 -*-
"""Settings of the Pair Connector."""


class Settings(object):
    """Class for the settings of the Pair Connector."""

    # Default window size
    WINDOW_SIZE = (700, 450)

    # Default edit pair dialog size
    EDIT_PAIR_DIALOG_SIZE = (300, 300)

    # Flag for source geometries operations
    SOURCE_GEOS = 0
    # Flag for destination geometries operations
    DESTINATION_GEOS = 1

    # Distance pair detection mode
    DISTANCE_MODE = 0
    # Vertex id pair detection mode
    VERTEX_MODE = 1
    # Transform pair detection mode
    TRANSFORM_MODE = 2
    # Object name pair detection mode
    NAME_MODE = 3

    # In mesh out mesh connection mode
    IN_MESH_OUT_MESH_MODE = 0
    # Blenshape connection mode
    BLENDSHAPE_MODE = 1
    # Wrap connection mode
    WRAP_MODE = 2
    # Parent connection mode
    PARENT_MODE = 3

    # Default UI values
    DEFAULTS = dict({
        'pair_detection_mode': NAME_MODE,
        'bbox_distance_threshold': .001,
        'vertex_distance_threshold': .001,
        'name_skip_count': 0,

        'connection_mode': BLENDSHAPE_MODE,
        'inherit_visibility': True,
        'inherit_transform': False,
        'allow_multi_pairs': False
    })

    # The "distance" threshold for matrix comparaison
    MATRIX_DISTANCE_THRESHOLD = .01

    # Path to icons
    MODIFIED_ICON_PATH = 'icons/star.png'
    ADDED_ICON_PATH = 'icons/plus.png'
    REMOVED_ICON_PATH = 'icons/minus.png'

    # Colors for active items
    FOREGROUND = (200, 200, 200)
    PAIRED_COLOR = (32, 64, 128)
    NON_PAIRED_COLOR = (128, 16, 8)
    MULTI_PAIR_COLOR = (145, 100, 40)

    # Colors for inactive items
    DISABLED_FOREGROUND = (100, 100, 100)
    DISABLED_PAIRED_COLOR = (41, 50, 68)
    DISABLED_NON_PAIRED_COLOR = (56, 27, 25)
    DISABLED_MULTI_PAIR_COLOR = (79, 59, 33)
