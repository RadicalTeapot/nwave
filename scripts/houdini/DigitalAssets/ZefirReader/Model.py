# -*- coding: utf-8 -*-
"""Model of the Zefir reader."""

import zefir

from nwave.effects.houdini.DigitalAssets.ZefirReader.Settings import Settings


class AssetData(object):
    """Data storage class for zefir assets."""

    def __init__(
        self, parm_id, instance_id=None, assembly_id=None,
        uv_component_id=None, name=None, stages=None, current_stage=None,
        is_asset_context=False
    ):
        """Initialize the class.

        Parameters
        ----------
        parm_id: int
            The id of the parm for this asset.
        instance_id: int
            The id of the instance representing this asset.
        assembly_id: int
            The id of the assembly containing this asset if it's a set. This
            will be passed to the pipeline_geometry node for directory path
            retrival.
        name: str
            The name to assign to the asset once loaded.
        stage: dict
            The stages id and name available for the asset. This will be used
            to fill the stages ordered menu.
        current_stage: int
            The stage id for the stage to load.
        is_asset_context: bool
            Flag for asset needing data extraction from asset context.
            This will be passed to the pipeline_geometry node for
            directory path retrival.

        """
        self.parm_id = parm_id
        self.instance_id = instance_id
        self.assembly_id = assembly_id
        self.uv_component_id = uv_component_id
        self.name = name
        self.stages = stages
        self.current_stage = current_stage
        self.is_asset_context = is_asset_context
        self.load = False


class Model(object):
    """Class for the model of the Zefir reader."""

    def __init__(self):
        """Initialize the class and setup the methods."""
        self._context = None

        self._sequence = None
        self._shot = None

        self._assets = dict([
            (category, dict()) for category in Settings.CATEGORIES.keys()
        ])

        self._setupMethods()

    def _setupMethods(self):
        """Create the methods to be called when a value has changed."""
        pass

    # ####################################################################### #
    #                            Getters / Setters                            #
    # ####################################################################### #
    @property
    def context(self):
        """zefir.Context: Zefir context."""
        if self._context is None:
            # Create the zefir context and put it in the node cached user data
            self._context = zefir.get_context()
            if self._context is None:
                self._context = zefir.configuration.configure()
        return self._context

    @property
    def sequence(self):
        """int: the current sequence number."""
        return self._sequence

    @sequence.setter
    def sequence(self, value):
        if not isinstance(value, int):
            raise TypeError('Expected int, got {0} instead'.format(
                type(value).__name__
            ))
        self._sequence = value

    @property
    def shot(self):
        """int: the current shot number."""
        return self._shot

    @shot.setter
    def shot(self, value):
        if not isinstance(value, int):
            raise TypeError('Expected int, got {0} instead'.format(
                type(value).__name__
            ))
        self._shot = value

    def getAsset(self, category, parm_id):
        """Return the AssetData with given category and parm_id.

        Parameters
        ----------
        category: zefir.ASSET_TYPES
            The categoryof the asset.
        parm_id: int
            The parm id of the asset.

        Returns
        -------
        AssetData
            The AssetData with given category and parm_id.

        """
        if parm_id not in self._assets[category]:
            raise RuntimeError(
                'Asset with parm_id {} cannot be found'.format(parm_id)
            )
        return self._assets[category][parm_id]

    def getAssets(self, category):
        """Return an AssetData list with given category.

        Parameters
        ----------
        category: zefir.ASSET_TYPES
            The categoryof the asset.

        Returns
        -------
        list of AssetData
            The list of AssetData with given category.

        """
        return self._assets[category].values()

    def getAssetCount(self, category):
        """Return the number of AssetData with given category.

        Parameters
        ----------
        category: zefir.ASSET_TYPES
            The categoryof the asset.

        Returns
        -------
        int
            The number of AssetData with given category.

        """
        return len(self._assets[category])

    @property
    def categories(self):
        """List of zefir.ASSET_TYPES: the list of asset categories."""
        return self._assets.keys()

    # ####################################################################### #
    #                             Regular Methods                             #
    # ####################################################################### #

    def clearShotData(self):
        """Empty the asset data."""
        self._assets = dict([
            (category, dict()) for category in Settings.CATEGORIES.keys()
        ])

    def isEmpty(self):
        """Return if any asset data exists.

        Returns
        -------
        bool
            Whether some asset data exists.

        """
        return sum([len(assets) for assets in self._assets.values()]) == 0

    def addAsset(
        self, category, instance_id, assembly_id, uv_component_id, name,
        stages, current_stage, is_asset_context
    ):
        """Add an asset to the asset data.

        Parameters
        ----------
        category: zefir.ASSET_TYPES
            The category of the asset data.
        instance_id: int
            The instance id of the asset.
        assembly_id: int
            The assembly id of the asset.
        uv_component_id: int
            The id of the uv stage for the asset.
        name: str
            The name of the asset.
        stages: dict
            Tuples of stage id, stage name for the asset.
        current_stage: int
            The current stage id to load for the asset.
        is_asset_context: bool
            Whether the asset is in asset context or shot context.

        """
        # Add one as the parm indices in Houdini start at one
        index = len(self._assets[category]) + 1
        new_asset = AssetData(
            index, instance_id, assembly_id, uv_component_id, name,
            stages, current_stage, is_asset_context
        )
        self._assets[category][index] = new_asset
