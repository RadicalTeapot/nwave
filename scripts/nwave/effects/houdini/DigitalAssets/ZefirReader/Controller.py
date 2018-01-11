# -*- coding: utf-8 -*-
"""Controller of the Zefir reader."""

import zefir

import hou
import os

from nwave.effects.houdini.DigitalAssets.ZefirReader.Settings import Settings
from nwave.effects.houdini.DigitalAssets.ZefirReader.Utils import Utils

import nwave.effects.houdini.nwHoudiniTools.DisplayHoudiniDialog as \
    DisplayHoudiniDialog


class Controller(object):
    """Class for the controller of the Zefir reader."""

    def __init__(self, model, view):
        """Initialize the controller and connect the view/model methods.

        Parameters
        ----------
        model: Model
            The model of the test.
        view: View
            The view of the test.

        """
        self._model = model
        self._view = view

        self._connectModel()
        self._connectView()

    def _connectModel(self):
        """Connect the model methods to the controller internal methods."""
        pass

    def _connectView(self):
        """Connect the view methods to the controller internal methods."""
        self._view.loadData = self._loadData
        self._view.getUpdate = self._getUpdate
        self._view.setChecked = self._setChecked
        self._view.loadAssetChecked = self._loadAssetChecked
        self._view.assetNameChanged = self._assetNameChanged
        self._view.assetStageChanged = self._assetStageChanged

    def _loadData(self):
        """Load data from zefir database."""
        # Update the model
        self._model.sequence = self._view.sequence
        self._model.shot = self._view.shot

        # Reset the node error message
        self._view.severity = 0
        self._view.message = ''

        # Get the shot from zefir
        seq_num = self._view.sequence
        shot_num = self._view.shot
        shot = self._model.context.find_shot(
            code='{0}_{1}'.format(
                str(seq_num).zfill(3),
                str(shot_num).zfill(4)
            )
        )

        if not shot:
            # Set the node error message
            self._view.severity = 2
            self._view.message = 'Could not find shot {seq}_{shot}'.format(
                seq=str(seq_num).zfill(3),
                shot=str(shot_num).zfill(4)
            )
            return

        # Initialize storage for data
        self._model.clearShotData()

        # Loop through all the asset assigned to the current shot
        # and group them by asset category
        shot_data = dict([
            (category, [
                shot_instance
                for shot_instance in shot.shot_instances
                if shot_instance and shot_instance.asset.asset_type == category
            ]) for category in Settings.CATEGORIES.keys()
        ])

        # Loop through each category stored for the current shot
        for category in shot_data.keys():
            # Fill the model with data from each asset in the category
            map(
                lambda shot_instance: self._addAsset(category, shot_instance),
                shot_data[category]
            )

            # Set the asset count for the current category. This creates
            # all the attributes to fill in the UI
            self._view.setAssetCount(
                Settings.CATEGORIES[category],
                self._model.getAssetCount(category)
            )

            # Set the asset names
            map(
                lambda asset: self._view.setAssetName(
                    Settings.CATEGORIES[category],
                    asset.parm_id,
                    asset.name
                ),
                self._model.getAssets(category)
            )

    def _addAsset(self, category, shot_instance):
        """Build AssetData and update the model from given shot instance.

        Parameters
        ----------
        category: zefir.ASSET_TYPE
            The category of the asset.
        shot_instance: zefir.ShotInstance
            The shot instance to extract data from.

        """
        # Initialize flag for asset needing data extraction from
        # asset context.
        asset_context_data = False

        # Initialize storage for asset stages
        components = None
        # If the current asset is an 'instance' asset
        # get it's stages from the asset context
        if category is zefir.ASSET_TYPES.INSTANCES:
            components = shot_instance.asset.components
            asset_context_data = True
        # Otherwise get it's stages from the shot context
        else:
            components = shot_instance.components

        # Stop if no stages were found for the current asset
        if components is None:
            return

        # Filter the components to keep only authorized stages
        components = [
            component
            for component in components
            if component.stage in Settings.AUTHORIZED_STAGES[category]
        ]

        # Stop if no stages were found for the current asset
        if not components:
            return

        # Build a (stage_id, stage_name) dict for all found stages
        stages = dict([
            (int(component.id), str(component.stage.name))
            for component in components
        ])

        # Build a list of loaded variations
        # (it is used to load the proper uv stage for each component)
        variations = [component.variant for component in components]

        # Get the assembly id for sets.
        assembly_id = None
        if category is zefir.ASSET_TYPES.SET_ELEMENT:
            # Find the category the shot instance belongs to
            asset_category = shot_instance.asset.category
            # Get the asset representing the category
            asset = self._model.context.find_asset(code=asset_category.code)
            if (
                asset and
                asset.asset_type is zefir.ASSET_TYPES.ASSEMBLY
            ):
                assembly_id = int(asset.id)

        uv_component_id = None
        if (
            category is zefir.ASSET_TYPES.CHARACTER or
            category is zefir.ASSET_TYPES.PROP
        ):
            uv_stage_components = [
                component.stage
                for component in shot_instance.components
                if component.stage == zefir.STAGES.UVS and
                component.variant in variations
            ]
            if not uv_stage_components:
                uv_component_id = [
                    component
                    for component in shot_instance.asset.components
                    if component.stage == zefir.STAGES.UVS and
                    component.variant in variations
                ][0].id
            else:
                uv_component_id = uv_stage_components[0].id

        self._model.addAsset(
            category=category,
            instance_id=int(shot_instance.id),
            assembly_id=assembly_id,
            uv_component_id=uv_component_id,
            name=str(shot_instance.string_repr(shot=False)),
            stages=stages,
            current_stage=int(components[0].id),
            is_asset_context=asset_context_data
        )

    def _getAsset(self, category, parm_id):
        """Get an asset from the model data.

        Parameters
        -----------
        category: str
            The name of the asset category.
        parm_id: int
            The parm id for the asset.

        Returns
        -------
        AssetData
            The asset data from the model.

        """
        zefir_category = None
        for key, value in Settings.CATEGORIES.items():
            if value == category:
                zefir_category = key
                break
        if zefir_category is None:
            raise RuntimeError(
                'Could not find zefir.ASSET_TYPE for category {}'.format(
                    category
                )
            )
        return self._model.getAsset(zefir_category, parm_id)

    def _loadAssetChecked(self, category, parm_id, state=None):
        """Set an asset load state.

        Parameters
        -----------
        category: str
            The name of the asset category.
        parm_id: int
            The parm id for the asset.
        state: bool
            The new load state value for the asset.

        """
        if state is None:
            state = self.view.getLoadAsset(category, parm_id)
        else:
            self._view.setLoadAsset(category, parm_id, state)
        self._getAsset(category, parm_id).load = state
        if not state:
            self._view.setLoadAll(category, state)

    def _assetNameChanged(self, category, parm_id):
        """Set an asset name.

        Parameters
        -----------
        category: str
            The name of the asset category.
        parm_id: int
            The parm id for the asset.
        name: str
            The new name for the asset.

        """
        name = self.view.getAssetName(category, parm_id)
        self._getAsset(category, parm_id).name = name

    def _assetStageChanged(self, category, parm_id):
        """Set an asset current stage id.

        Parameters
        -----------
        category: str
            The name of the asset category.
        parm_id: int
            The parm id for the asset.
        stage_id: int
            The new current stage id value for the asset.

        """
        stage_id = self.view.getAssetStage(category, parm_id)
        self._getAsset(category, parm_id).current_stage = stage_id

    def _getUpdate(self):
        """Extract the path to alembic files for selected assets."""
        if self._model.isEmpty():
            DisplayHoudiniDialog.displayHoudiniDialog(
                'No loaded data'
                'No data is available, make sure Zefir data has been loaded.',
                severity=DisplayHoudiniDialog.SeverityTypes.WARNING,
            )
            return

        # List all pipeline_geometry nodes currently in the scene
        nodes = filter(
            lambda node: (
                'pipeline_geometry' in node.type().name() or
                'pipeline_camera' in node.type().name()
            ),
            hou.node("/obj").children()
        )

        # Create look up dictionnary for pipeline_geometry nodes
        # and their instanceId parameter value
        pipeline_geometry_nodes = dict([
            (node.parm('instanceID').evalAsInt(), node) for node in nodes
        ])

        # Initialize data storage
        errors = []  # Storage for error messages
        created = []  # Storage for creation messages
        updated = []  # Storage for update messages
        # Loop over the asset categories
        latest_position = None
        for category in self._model.categories:
            # Get assets to load
            assets = [
                asset
                for asset in self.model.getAssets(category)
                if self._validateAsset(asset)
            ]
            for asset in assets:
                # If pipeline_geometry node with the instance id doesn't exist
                if asset.instance_id not in pipeline_geometry_nodes:
                    # Create the node
                    asset_node, latest_position = self._createAssetNode(
                        category, asset, latest_position
                    )

                    # Set asset_node stage_id param and update it
                    asset_node.parm("stageID").set(asset.current_stage)
                    asset_node.parm("instanceID").set(asset.instance_id)
                    if category != zefir.ASSET_TYPES.CAMERA:
                        asset_node.parm("uvStageID").set(
                            -1
                            if asset.uv_component_id is None
                            else asset.uv_component_id
                        )
                        asset_node.parm("assetContext").set(
                            asset.is_asset_context
                        )
                        asset_node.parm("assemblyID").set(
                            -1
                            if asset.assembly_id is None
                            else asset.assembly_id
                        )
                    asset_node.parm("update").pressButton()

                    # Update the pipepline_geo look up dictionnary
                    pipeline_geometry_nodes[asset.instance_id] = asset_node

                    # Append to the creation messages list
                    created.append(
                        '{0} node created for asset {1}'.format(
                            asset_node.name(),
                            asset.name
                        )
                    )
                else:
                    # If a pipeline_geometry node with the same instanceId
                    # already exist, just update it
                    pipeline_geometry_nodes[asset.instance_id].parm(
                        "stageID"
                    ).set(asset.current_stage)
                    if category != zefir.ASSET_TYPES.CAMERA:
                        pipeline_geometry_nodes[asset.instance_id].parm(
                            "uvStageID"
                        ).set(
                            -1
                            if asset.uv_component_id is None
                            else asset.uv_component_id
                        )
                        pipeline_geometry_nodes[asset.instance_id].parm(
                            "assetContext"
                        ).set(asset.is_asset_context)
                        pipeline_geometry_nodes[asset.instance_id].parm(
                            "assemblyID"
                        ).set(
                            -1
                            if asset.assembly_id is None
                            else asset.assembly_id
                        )
                    pipeline_geometry_nodes[asset.instance_id].parm(
                        "update"
                    ).pressButton()

                    # Append to the updated messages list
                    updated.append(
                        '{0} node updated for asset {1}'.format(
                            pipeline_geometry_nodes[asset.instance_id].name(),
                            asset.name
                        )
                    )

        if errors:
            DisplayHoudiniDialog.displayHoudiniDialog(
                'Error while getting some assets',
                '\n'.join(errors),
                severity=DisplayHoudiniDialog.SeverityTypes.WARNING
            )

        if created or updated:
            DisplayHoudiniDialog.displayHoudiniDialog(
                'Data imported successfully',
                '\n'.join(['\n'.join(created), '\n'.join(updated)]),
                severity=DisplayHoudiniDialog.SeverityTypes.MESSAGE
            )

        # Uncheck all load assets
        for zefir_category, category_name in Settings.CATEGORIES.items():
            map(
                lambda asset: self._loadAssetChecked(
                    category_name,
                    asset.parm_id,
                    False
                ),
                self._model.getAssets(zefir_category)
            )

    def _validateAsset(self, asset):
        """Return whether given asset is valid to load.

        Parameters
        ----------
        asset: Model.AssetData
            The asset to validate.

        Returns
        -------
        bool
            Whether the asset can be loaded.

        """
        context = self._model.context

        # Skip if the asset is not marked to be loaded
        if not asset.load:
            return False

        # Verify the existence of the stage for the current asset
        asset_stage = None
        if asset.is_asset_context:
            asset_stage = context.find_asset_component(
                id=asset.current_stage
            )
        else:
            asset_stage = context.find_shot_instance_component(
                id=asset.current_stage
            )
        # Skip if the stage can't be found
        if asset_stage is None:
            return False

        # Verify the existence of commited data for the current
        # asset's stage
        commit_data = asset_stage.commits
        # Skip if commited data can't be found
        if commit_data is None:
            return False

        return True

    def _createAssetNode(self, category, asset, latest_position=None):
        """Create and return a hou.Node and fill it's data with given asset.

        The hou.Node created is either a pipeline_geometry or a
        pipeline_camera depending on the category.

        Parameters
        ----------
        category: zefir.ASSET_TYPES
            The asset category.
        asset: Model.AssetData
            The asset used to fill the node data.
        latest_position: hou.Vector
            The last position used to create a node.

        Returns
        -------
        hou.Node, hou.Vector2
            The created node and it's position.

        """
        # Choose the node type based on the current category
        node_type = "pipeline_geometry"
        if category is zefir.ASSET_TYPES.CAMERA:
            cam_asset = self._model.context.find_shot_instance_component(
                id=asset.stages.keys()[0]
            )
            commit = cam_asset.get_latest_or_new_commit_revising()
            alembic_files = [
                filename
                for filename in os.listdir(str(commit.resolved_directory))
                if 'abc' in os.path.splitext(filename)[-1]
            ]
            if alembic_files:
                node_type = "pipeline_camera_alembic"
            else:
                node_type = "pipeline_camera"

        # Create the node for this asset
        root_node = hou.node("/obj")
        asset_node = root_node.createNode(
            node_type,
            node_name=asset.name.replace('#', '').replace(' ', '_')
        )

        # Find the network box for the asset or create it if it doesn't exist
        network_box = root_node.findNetworkBox(Settings.CATEGORIES[category])
        if network_box is None:
            network_box = root_node.createNetworkBox(
                Settings.CATEGORIES[category]
            )
            network_box.setComment(str(
                Settings.CATEGORIES[category]
            ).capitalize())
            network_box.setMinimized(False)
            network_box.setAutoFit(True)
            network_box.setColor(Settings.COLORS[category])
        # Set the asset node color based on it's category
        asset_node.setColor(Settings.COLORS[category])

        other_nodes = network_box.nodes()
        if not other_nodes:
            if latest_position is None:
                try:
                    latest_position = Utils.bestNodePosition()
                except RuntimeError:
                    latest_position = asset_node.moveToGoodPosition()
            else:
                latest_position = hou.Vector2(
                    latest_position[0] + 3,
                    latest_position[1]
                )
            asset_node.setPosition(latest_position)
        else:
            left = other_nodes[0].position()[0]
            bottom = other_nodes[0].position()[1]
            for other in other_nodes[1:]:
                pos = other.position()
                if pos[1] < bottom:
                    bottom = pos[1]
                if pos[0] < left:
                    left = pos[0]
            asset_node.setPosition(hou.Vector2(left, bottom - 1))
        network_box.addNode(asset_node)
        network_box.fitAroundContents()

        return asset_node, latest_position

    def _setChecked(self, parm):
        """Check / Uncheck all checkers for a given category.

        Parameters
        ----------
        parm: hou.Parm
            The load all parm which state changed.

        """
        # Get the name of the global checker
        name = parm.name()
        # And it's value
        check_state = bool(parm.evalAsInt())

        # Extract the category from the checker's name
        zefir_category, category_name = None, None
        for key, value in Settings.CATEGORIES.items():
            if value in name:
                zefir_category = key
                category_name = value
                break
        if category_name is None:
            raise RuntimeError(
                'Could not find the category for parm {}'.format(name)
            )

        for index in range(self._model.getAssetCount(zefir_category)):
            # Add one as the Houdini parm indices start at one
            parm_id = index + 1
            # Update the model value
            self._loadAssetChecked(category_name, parm_id, check_state)
            # Update the view
            self._view.setLoadAsset(category_name, parm_id, check_state)

    # ####################################################################### #
    #                            Getters / Setters                            #
    # ####################################################################### #
    @property
    def model(self):
        """Model: the model associated with the controller."""
        return self._model

    @property
    def view(self):
        """View: the view associated with the controller."""
        return self._view

    # ####################################################################### #
    #                             Regular Methods                             #
    # ####################################################################### #

    def getAssetStages(self, parm):
        """Return the available stages for a given asset.

        This method is called by the Houdini node to fill the stages ordered
        menus.
        """
        category, parm_id = self._view.getParmCategoryAndId(parm)
        zefir_category = None
        for key, value in Settings.CATEGORIES.items():
            if value == category:
                zefir_category = key
                break
        if zefir_category is None:
            raise RuntimeError(
                'Could not find zefir.ASSET_TYPE for category {}'.format(
                    category
                )
            )

        try:
            asset = self._model.getAsset(zefir_category, parm_id)
        except RuntimeError:
            return []
        # Sort the stages by alphabetical order
        stages = sorted(asset.stages.items(), key=lambda item: item[1])

        data = []
        for stage_id, stage_name in stages:
            data.extend([str(stage_id), stage_name])
        return data

    # ####################################################################### #
    #                           Node static methods                           #
    # ####################################################################### #

    @staticmethod
    def nodeUpdate():
        """Cook the node.

        This method is called by Houdini when the node is cooking.

        """
        # Get a handle to the node
        self = hou.pwd()

        # Activate the node's warning/error flag based on the severity
        # attribute
        severity = self.parm('severity').evalAsInt()
        message = self.parm('message').evalAsString()
        if severity == 1:
            raise hou.NodeWarning(message)
        elif severity == 2:
            raise hou.NodeError(message)

        # Update the node if it has not beed updated yet and set it's update
        # flag
        if not self.cachedUserData('loaded'):
            hou.phm().loadDataCallback()
            self.setCachedUserData('loaded', True)

    @staticmethod
    def nodeCreate():
        """Initialize the node.

        This methods is called by Houdini when the node is created.

        """
        # Mark the node has not updated
        hou.pwd().setCachedUserData('loaded', False)

    @staticmethod
    def nodeLoad():
        """Initialize the node.

        This methods is called by Houdini when the node is loaded.

        """
        # Mark the node has not updated
        hou.pwd().setCachedUserData('loaded', False)
