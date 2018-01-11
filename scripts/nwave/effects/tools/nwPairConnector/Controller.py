# -*- coding: utf-8 -*-
"""Controller of the Pair Connector."""

import maya.api.OpenMaya as om
import maya.cmds as mc

from nwave.effects.tools.nwPairConnector.Settings import Settings
from nwave.effects.tools.nwPairConnector.Utils import Utils

from nwave.effects.tools.nwFXTDTools.DisplayMayaDialog import displayMayaDialog

from functools import partial


class Controller(object):
    """Class for the controller of the Pair Connector."""

    def __init__(self, model, view):
        """Initialize the controller and connect the view/model methods.

        Parameters
        ----------
        model: Model
            The model of the Pair Connector.
        view: View
            The view of the Pair Connector.

        """
        self._model = model
        self._view = view

        self._connectModel()
        self._connectView()
        self._initialize()

    def _initialize(self):
        """Initialize the tool state."""
        self._model.pair_detection_mode = Settings.DEFAULTS[
            'pair_detection_mode'
        ]
        self._model.bbox_distance_threshold = Settings.DEFAULTS[
            'bbox_distance_threshold'
        ]
        self._model.vertex_distance_threshold = Settings.DEFAULTS[
            'vertex_distance_threshold'
        ]
        self._model.connection_mode = Settings.DEFAULTS['connection_mode']
        self._model.inherit_visibility = Settings.DEFAULTS[
            'inherit_visibility'
        ]
        self._model.inherit_transform = Settings.DEFAULTS['inherit_transform']
        self._model.allow_multi_pairs = Settings.DEFAULTS['allow_multi_pairs']

    # ####################################################################### #
    #                    Model / View methods connections                     #
    # ####################################################################### #

    def _connectModel(self):
        """Connect the model methods to the controller internal methods."""
        self._model.itemsChanged = partial(
            self._buildConnections,
            rebuild=True
        )
        self._model.pairDetectionModeChanged = self._pairDetectionModeChanged
        self._model.bboxDistanceThresholdChanged = \
            self._bboxDistanceThresholdChanged
        self._model.vertexDistanceThresholdChanged = \
            self._vertexDistanceThresholdChanged

        self._model.connectionModeChanged = self._connectionModeChanged
        self._model.inheritVisibilityChanged = self._inheritVisibilityChanged
        self._model.inheritTransformChanged = self._inheritTransformChanged
        self._model.allowMultiPairsChanged = self._allowMultiPairsChanged

    def _connectView(self):
        """Connect the view methods to the controller internal methods."""
        self._view.loadGeometries = self._loadGeometries
        self._view.updatePairDetectionMode = self._updatePairDetectionMode

        self._view.updateBboxDistanceThreshold = \
            self._updateBboxDistanceThreshold
        self._view.updateVertexDistanceThreshold = \
            self._updateVertexDistanceThreshold

        self._view.updateConnectionMode = self._updateConnectionMode
        self._view.updateInheritVisibility = self._updateInheritVisibility
        self._view.updateInheritTransform = self._updateInheritTransform
        self._view.updateAllowMultiPairs = self._updateAllowMultiPairs

        self._view.connect = self._connect
        self._view.closeTool = self._closeTool

        self._view.clearList = self._clearGeometries
        self._view.removeItem = self._removeGeometry
        self._view.selectItem = self._selectGeometry
        self._view.selectPairedItems = self._selectPairedGeometries

        self._view.editPairData = self._editPairData
        self._view.resetPairData = self._resetPairData
        self._view.editPairAdd = self._editPairAdd
        self._view.editPairRemove = self._editPairRemove
        self._view.editPairSelect = self._editPairSelect

        self._view.itemClicked = self._itemClicked
        self._view.selectionCleared = self._selectionCleared

    # ####################################################################### #
    #                       Geometries related methods                        #
    # ####################################################################### #

    def _getSelectedGeometries(self):
        """Return a list of selected geometries in the scene.

        Only the transform nodes of which have a 'mesh' type shape are
        returned.

        Returns
        -------
        list of str
            The selected geometries.

        """
        return filter(
            lambda node: (
                # Check if the selected node is a transform
                mc.nodeType(node) == 'transform' and
                # That has a shape
                mc.listRelatives(node, s=True, fullPath=True) and
                # Which is a mesh
                mc.nodeType(
                    mc.listRelatives(node, f=True, s=True)[0]
                ) == 'mesh'
            ),
            mc.ls(sl=True, l=True)
        )

    def _loadGeometries(self, geo_type):
        """Fill the model with selected object from the maya scene.

        Parameters
        ----------
        geo_type: int
            The type of geometries to return (Settings.SOURCE_GEOS or
            Settings.DESTINATION_GEOS)

        Raises
        -------
        RuntimeError
            Wrong geometry type passed.

        """
        geometries = self._getSelectedGeometries()

        items = set()
        for geometry in geometries:
            item = self._buildItem(geo_type, geometry)
            if not self._model.hasItem(item, ignore_type=True):
                items.add(item)

        self._model.addItems(items)

    def _clearGeometries(self, geo_type):
        """Empty the geometries data for the given type."""
        self._model.clearItems(geo_type)

    def _removeGeometry(self, geo_type, item_name):
        """Remove the item with given name from given type list.

        Parameters
        ----------
        geo_type: int
            The type of item to look for.
        item_name: str
            The name of the item to remove.

        """
        self._model.removeItem(geo_type, item_name)

    def _selectGeometry(self, geo_type, item_name):
        """Select in the viewport the item with given name.

        Parameters
        ----------
        geo_type: int
            The type of item to look for.
        item_name: str
            The name of the item to remove.

        """
        item = self._model.getItem(geo_type, item_name)
        if item is not None:
            mc.select(item.full_path, r=True)

    def _getPairedItems(self, item):
        """Return items connected to the given item.

        Parameters
        ----------
        item:
            The item for which to retrieve the pairs.

        Returns
        -------
        list of ItemHandler.Item
            The connected items.

        """
        if item is None:
            return []
        # Get the pairs containing that item
        pairs = self._model.getItemPairs(item)
        # Filter the item out of the pairs
        items = []
        for source, destination in pairs:
            if source != item:
                items.append(source)
            else:
                items.append(destination)
        return items

    def _selectPairedGeometries(self, geo_type, item_name):
        """Select in the viewport the paired items of the item with given name.

        Parameters
        ----------
        geo_type: int
            The type of item to look for.
        item_name: str
            The name of the item to remove.

        """
        # Get the right clicked item
        source_item = self._model.getItem(geo_type, item_name)
        if source_item is None:
            return
        items = self._getPairedItems(source_item)
        # Select the geometries
        mc.select([item.full_path for item in items], r=True)

    # ####################################################################### #
    #                       Connections related methods                       #
    # ####################################################################### #

    def _editPairData(self, geo_type, item_name):
        """Open the pair editor for the item with given name and type.

        Parameters
        ----------
        geo_type: int
            The type of item to edit.
        item_name: str
            The name of the item to edit.

        """
        # Save the item as the edited one for latter reference
        self._model.edited_item = self._model.getItem(
            geo_type, item_name
        )
        if self._model.edited_item is None:
            return

        # Get the paired items
        items = self._getPairedItems(self._model.edited_item)

        # Open the pair editor
        self._view.showEditPairDialog(
            self._model.edited_item.display_name,
            sorted([pair_item.display_name for pair_item in items])
        )

    def _updatePairDataEditor(self):
        """Update the display of the pair editor."""
        # Get the paired items
        items = self._getPairedItems(self._model.edited_item)

        # Open the pair editor
        self._view.updateEditPairDialog(
            self._model.edited_item.display_name,
            sorted([pair_item.display_name for pair_item in items])
        )

    def _resetPairData(self, geo_type, item_name):
        """Remove all the connection overrides containing given item.

        Parameters
        ----------
        geo_type: int
            The type of item to edit.
        item_name: str
            The name of the item to edit.

        """
        self._model.clearItemConnectionOverrides(
            self._model.getItem(geo_type, item_name)
        )
        # Repaint the list to update the item's bg color
        self._refreshList(Settings.SOURCE_GEOS)
        self._refreshList(Settings.DESTINATION_GEOS)

    def _editPairAdd(self):
        """Add the selected geometries to the edited item connections."""
        # Find the opposite item type of the edited item
        geo_type = Settings.SOURCE_GEOS
        if self._model.edited_item.type == geo_type:
            geo_type = Settings.DESTINATION_GEOS

        # Get objects selected in the scene
        selected_items = self._getSelectedGeometries()

        # Add them as extra connections
        for selected_item in selected_items:
            self._model.addItemConnection(
                self._model.edited_item,
                self._model.getItem(
                    geo_type,
                    self._buildItemDisplayName(selected_item)
                ),
                extra=True
            )

        self._updatePairDataEditor()
        self._refreshList(Settings.SOURCE_GEOS)
        self._refreshList(Settings.DESTINATION_GEOS)

    def _editPairRemove(self, selected_items):
        """Remove the selected items from the edited item connections.

        Parameters
        ----------
        seleted_items: list of str
            The name of the items to remove.

        """
        geo_type = Settings.SOURCE_GEOS
        if self._model.edited_item.type == geo_type:
            geo_type = Settings.DESTINATION_GEOS

        for selected_item in selected_items:
            self._model.removeItemConnection(
                self._model.edited_item,
                self._model.getItem(
                    geo_type,
                    self._buildItemDisplayName(selected_item)
                )
            )

        self._updatePairDataEditor()
        self._refreshList(Settings.SOURCE_GEOS)
        self._refreshList(Settings.DESTINATION_GEOS)

    def _editPairSelect(self, selected_items):
        """Select the given paired items in the viewport.

        Parameters
        ----------
        selected_items: list of str
            The name of the items to select.

        """
        mc.select(selected_items, r=True)

    # ####################################################################### #
    #                       Item / Connections building                       #
    # ####################################################################### #

    def _buildItemCleanName(self, full_path):
        """Return the clean name for a geometry with at given path.

        The clean name is built by removing the namespace from the full path.

        Parameters
        ----------
        full_path: str
            The whole path to the geometry.

        Returns
        -------
        str
            The clean name for the given geometry.

        """
        return '|'.join([
            name.split(':')[-1]
            for name in full_path.split('|')
        ])

    def _buildItemDisplayName(self, full_path):
        """Return the display name for a geometry with at given path.

        The display name is built taking the shortest unique name.

        Parameters
        ----------
        full_path: str
            The whole path to the geometry.

        Returns
        -------
        str
            The clean name for the given geometry.

        """
        return mc.ls(full_path)[0]

    def _buildItem(self, geo_type, long_name):
        """Add an item to the given geo type list.

        Parameters
        ----------
        geo_type: int
            The type of item to create.
        long_name: str
            The full path to the object.

        Returns
        -------
        Model.Item
            The item fill with data from the object.

        """
        # Get the dag path to the object
        sel_list = om.MSelectionList()
        sel_list.add(long_name)
        dag_path = sel_list.getDagPath(0)
        # Build a MFnMesh from the dag path
        mesh = om.MFnMesh(dag_path)
        # Get the MBoundingBox from the dag path
        bbox = om.MFnDagNode(dag_path).boundingBox

        # Build an orthonormal set of vectors from point positions
        points = mesh.getPoints(om.MSpace.kWorld)
        x_axis = (points[1] - points[0]).normalize()
        y_axis = (points[2] - points[0])
        point_id = 2
        while y_axis.isParallel(x_axis) and point_id < len(points):
            point_id += 1
            y_axis = (points[point_id] - points[0])

        # Skip if the whole mesh is a straight line
        if point_id == len(points):
            return

        y_axis = y_axis.normalize()
        z_axis = x_axis ^ y_axis
        y_axis = z_axis ^ x_axis

        # Build a transformation matrix from orthonormal vectors
        world_matrix = om.MMatrix((
            (x_axis[0], x_axis[1], x_axis[2], 0),
            (y_axis[0], y_axis[1], y_axis[2], 0),
            (z_axis[0], z_axis[1], z_axis[2], 0),
            points[0]
        ))

        display_name = self._buildItemDisplayName(long_name)

        # Build and retrun the Item
        return self._model.buildItem(
            name=self._buildItemCleanName(display_name),
            display_name=display_name,
            full_path=long_name,
            point_count=mesh.numVertices,
            vertex_position=mesh.getPoint(0, space=om.MSpace.kWorld),
            bbox=bbox,
            world_matrix=world_matrix,
            item_type=geo_type
        )

    def _buildConnections(self, rebuild=True):
        """Fill the pairs attribute on simulated and asset items."""
        source_items = self._model.getItems(Settings.SOURCE_GEOS)
        destination_items = self._model.getItems(Settings.DESTINATION_GEOS)

        if rebuild:
            self._model.clearConnections()

        for simulated in source_items:
            existing = self._model.getItemConnections(simulated)
            for asset in destination_items:
                # Skip if the pair already exists
                if asset in existing:
                    continue
                if not self._compareItems(simulated, asset):
                    continue
                self._model.addItemConnection(simulated, asset)

        self._refreshList(Settings.SOURCE_GEOS)
        self._refreshList(Settings.DESTINATION_GEOS)

    def _compareMatrix(self, first, second):
        """Return simple distance estimation between two matrices.

        Parameters
        ----------
        first: OpenMaya.MMatrix
            The first matrix to compare.
        second: OpenMaya.MMatrix
            The second matrix to compare.

        Returns
        -------
        float
            The simple distance estimation between the two matrices.

        """
        if not isinstance(first, om.MMatrix):
            raise TypeError(
                'Expected OpenMaya.MMatrix, got {0} instead'.format(
                    type(first).__name__
                )
            )
        if not isinstance(second, om.MMatrix):
            raise TypeError(
                'Expected OpenMaya.MMatrix, got {0} instead'.format(
                    type(first).__name__
                )
            )

        values = zip(list(first), list(second))

        # Use sum of the element wise absolute difference as a distance metric
        distance = 0.
        for first_value, second_value in values:
            distance += abs(first_value - second_value)
        return distance

    def _compareItems(self, first, second):
        """Return whether two given items are a pair.

        Parameters
        -----------
        first: Model.Item
            The fist item to compare.
        second: Model.Item
            The second item to compare.

        Returns
        -------
        bool
            Whether the given items form a pair.

        """
        # Compare the bounding box
        if self._model.pair_detection_mode == Settings.DISTANCE_MODE:
            min_vector = (
                (first.bbox.min - first.bbox.center) -
                (second.bbox.min - second.bbox.center)
            )
            max_vector = (
                (first.bbox.max - first.bbox.center) -
                (second.bbox.max - second.bbox.center)
            )
            return (
                min_vector.length() <= self._model.bbox_distance_threshold
                and
                max_vector.length() <= self._model.bbox_distance_threshold
            )
        # Compare the first vertex position
        elif self._model.pair_detection_mode == Settings.VERTEX_MODE:
            vector = first.vertex_position - second.vertex_position
            return vector.length() <= self._model.vertex_distance_threshold
        # Compare the clean name
        elif self._model.pair_detection_mode == Settings.NAME_MODE:
            first_name = first.name.split('|')
            second_name = second.name.split('|')
            return (
                all(name in second_name for name in first_name) or
                all(name in first_name for name in second_name)
            )
        # Compare the transformation matrix
        elif self._model.pair_detection_mode == Settings.TRANSFORM_MODE:
            return self._compareMatrix(
                first.world_matrix,
                second.world_matrix
            ) <= Settings.MATRIX_DISTANCE_THRESHOLD

        return False

    # ####################################################################### #
    #                     Model / View Connected Methods                      #
    # ####################################################################### #

    def _updatePairDetectionMode(self):
        """Connect view changes to model attribute."""
        self._model.pair_detection_mode = self._view.pair_detection_mode

    def _pairDetectionModeChanged(self):
        """Connect model changes to view controllers."""
        self._view.pair_detection_mode = self._model.pair_detection_mode
        self._buildConnections()

    def _updateBboxDistanceThreshold(self):
        """Connect view changes to model attribute."""
        self._model.bbox_distance_threshold = \
            self._view.bbox_distance_threshold

    def _bboxDistanceThresholdChanged(self):
        """Connect model changes to view controllers."""
        self._view.bbox_distance_threshold = \
            self._model.bbox_distance_threshold
        self._buildConnections()

    def _updateVertexDistanceThreshold(self):
        """Connect view changes to model attribute."""
        self._model.vertex_distance_threshold = \
            self._view.vertex_distance_threshold

    def _vertexDistanceThresholdChanged(self):
        """Connect model changes to view controllers."""
        self._view.vertex_distance_threshold = \
            self._model.vertex_distance_threshold
        self._buildConnections()

    def _updateConnectionMode(self):
        """Connect view changes to model attribute."""
        self._model.connection_mode = self._view.connection_mode

    def _connectionModeChanged(self):
        """Connect model changes to view controllers."""
        self._view.connection_mode = self._model.connection_mode

    def _updateInheritVisibility(self):
        """Connect view changes to model attribute."""
        self._model.inherit_visibility = self._view.inherit_visibility

    def _inheritVisibilityChanged(self):
        """Connect model changes to view controllers."""
        self._view.inherit_visibility = self._model.inherit_visibility

    def _updateInheritTransform(self):
        """Connect view changes to model attribute."""
        self._model.inherit_transform = self._view.inherit_transform

    def _inheritTransformChanged(self):
        """Connect model changes to view controllers."""
        self._view.inherit_transform = self._model.inherit_transform

    def _updateAllowMultiPairs(self):
        """Connect view changes to model attribute."""
        self._model.allow_multi_pairs = self._view.allow_multi_pairs

    def _allowMultiPairsChanged(self):
        """Connect model changes to view controllers."""
        self._view.allow_multi_pairs = self._model.allow_multi_pairs
        self._updateConnect()

    def _updateConnect(self):
        """Enable/Disable connections creation based on multi pairs."""
        # Enable the connect button
        self._view.enableConnect()
        # Stop if multi pairs are allowed
        if self._model.allow_multi_pairs:
            return

        # Find multi pairs
        source_items = self._model.getItems(Settings.SOURCE_GEOS)
        destination_items = self._model.getItems(Settings.DESTINATION_GEOS)

        simulated_multi_pairs = any(
            len(self._model.getItemConnections(item)) > 1
            for item in source_items
        )

        destination_multi_pairs = any(
            len(self._model.getItemConnections(item)) > 1
            for item in destination_items
        )

        # Disable the button if multi-pairs are found
        if simulated_multi_pairs or destination_multi_pairs:
            self._view.disableConnect()

    def _itemClicked(self, geo_type, item_name):
        """Store the newly selected item in the model.

        Parameters
        ----------
        geo_type: int
            The item type of the list to refresh.
        item_name: str
            The name of the selected item.

        """
        self._model.selected_item = self._model.getItem(geo_type, item_name)
        self._refreshList(Settings.SOURCE_GEOS)
        self._refreshList(Settings.DESTINATION_GEOS)

    def _selectionCleared(self, geo_type):
        """Clear the store selected item.

        Parameters
        ----------
        geo_type: int
            The item type of the list to refresh.

        """
        # Stop if no item is selected or the list clicked is not the one
        # containing the selected item
        if (
            not self._model.selected_item or
            geo_type != self._model.selected_item.type
        ):
            return

        self._model.selected_item = None

        self._refreshList(Settings.SOURCE_GEOS)
        self._refreshList(Settings.DESTINATION_GEOS)

    def _refreshList(self, geo_type):
        """Reload the view geo lists using the model data.

        Parameters
        ----------
        geo_type: int
            The item type of the list to refresh.

        """
        # Get item data from the model
        items = self._model.getItems(geo_type)
        # Sort it alphabetically
        items.sort(key=lambda item: item.display_name)

        if not self._model.selected_item:
            # If no item is selected, set all item display to enabled mode
            for item in items:
                item.disabled = False
        else:
            # Disable items
            for item in items:
                item.disabled = True
            # Re-enable the currently selected item if it's the right type
            if geo_type == self._model.selected_item.type:
                self._model.selected_item.disabled = False
            # Otherwise enable the items connected to the selected ones
            else:
                for item in self._getPairedItems(self._model.selected_item):
                    item.disabled = False

        # Refresh the view data
        self._view.setGeometries(
            geo_type,
            zip(
                [str(item) for item in items],
                [self._model.getItemDisplay(item)['color'] for item in items],
                [self._model.getItemDisplay(item)['icon'] for item in items],
            )
        )

        # Restore the item selection
        if (
            self._model.selected_item and
            geo_type == self._model.selected_item.type
        ):
            self._view.selectGeometry(geo_type, str(self._model.selected_item))

        self._updateConnect()

    def _connect(self):
        """Connect the pairs in maya using the selected connection mode."""
        # Open the undo chunk so the whole operation can be undone at once
        mc.undoInfo(openChunk=True)
        try:
            sources = self._model.getItems(Settings.SOURCE_GEOS)

            for source in sources:
                destinations = self._getPairedItems(source)
                if self._model.inherit_visibility:
                    # Connect the visbility attribute
                    map(
                        lambda destination: Utils.connectAttribute(
                            source.full_path,
                            destination.full_path,
                            'visibility'
                        ),
                        destinations
                    )

                if self._model.inherit_transform:
                    # Connect the all transform attributes
                    for attribute in [
                        'translateX', 'translateY', 'translateZ',
                        'rotateX', 'rotateY', 'rotateZ',
                        'scaleX', 'scaleY', 'scaleZ'
                    ]:
                        map(
                            lambda destination: Utils.connectAttribute(
                                source.full_path,
                                destination.full_path,
                                attribute
                            ),
                            destinations
                        )

                # Store the connection method based on selected mode.
                method = None
                if (
                    self._model.connection_mode ==
                    Settings.IN_MESH_OUT_MESH_MODE
                ):
                    method = Utils.connectWorldMesh
                elif self._model.connection_mode == Settings.BLENDSHAPE_MODE:
                    method = Utils.makeBlendShape
                elif self._model.connection_mode == Settings.WRAP_MODE:
                    method = Utils.makeWrap
                elif self._model.connection_mode == Settings.PARENT_MODE:
                    method = lambda source, destination: mc.parent(
                        destination, source
                    )

                # Connect the paired geometries together.
                map(
                    lambda destination: method(
                        source.full_path, destination.full_path
                    ),
                    destinations
                )
        except Exception:
            raise
        finally:
            # Close the chunk whatever happens to avoid messing with undo
            # state in maya
            mc.undoInfo(closeChunk=True)

        displayMayaDialog(
            'Connections successful',
            'The geometries have been successfully connected.'
        )

    def _closeTool(self):
        """Close the tool."""
        self._view.close()
