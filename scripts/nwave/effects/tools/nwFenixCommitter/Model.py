# -*- coding: utf-8 -*-
"""Model of the Fenix Committer."""


class Model(object):
    """Class for the model of the Fenix Committer."""

    def __init__(self):
        """Initialize the class and setup the methods."""
        self._setupMethods()

        self.assets = {}
        self.user = None
        self.frame_in = None
        self.frame_out = None
        self.motion_blur_in = None
        self.motion_blur_out = None

    def _setupMethods(self):
        """Create the methods to be called when a value has changed."""
        pass
