# -*- coding: utf-8 -*-
"""Model of the Pair Connector."""

from nwave.effects.tools.nwPairConnector.Model.ConnectionHandler import \
    ConnectionHandler
from nwave.effects.tools.nwPairConnector.Model.ItemHandler import \
    Item
from nwave.effects.tools.nwPairConnector.Model.ItemHandler import \
    ItemHandler
from nwave.effects.tools.nwPairConnector.Settings import Settings


class Model(object):
    """Class for the model of the Pair Connector."""

    def __init__(self):
        """Initialize the class and setup the methods."""
        self._itemHandler = ItemHandler()
        self._connectionHandler = ConnectionHandler()

        self._pair_detection_mode = None
        self._bbox_distance_threshold = None
        self._vertex_distance_threshold = None

        self._connection_mode = None
        self._inherit_visibility = None
        self._inherit_transform = None
        self._allow_multi_pairs = None

        self._edited_item = None
        self._selected_item = None

        self._setupMethods()

    def _setupMethods(self):
        """Create the methods to be called when a value has changed."""
        self.itemsChanged = lambda: None
        self.pairDetectionModeChanged = lambda: None
        self.bboxDistanceThresholdChanged = lambda: None
        self.vertexDistanceThresholdChanged = lambda: None

        self.connectionModeChanged = lambda: None
        self.inheritVisibilityChanged = lambda: None
        self.inheritTransformChanged = lambda: None
        self.allowMultiPairsChanged = lambda: None

    # ####################################################################### #
    #                            Getters / Setters                            #
    # ####################################################################### #

    @property
    def pair_detection_mode(self):
        """Int: pair detection algorithm used."""
        return self._pair_detection_mode

    @pair_detection_mode.setter
    def pair_detection_mode(self, value):
        if value not in [
            Settings.DISTANCE_MODE,
            Settings.VERTEX_MODE,
            Settings.NAME_MODE,
            Settings.TRANSFORM_MODE
        ]:
            raise TypeError('Wrong pair detection mode type.')
        self._pair_detection_mode = value
        self.pairDetectionModeChanged()

    @property
    def bbox_distance_threshold(self):
        """Float: the bbox distance threshold value for pair finding."""
        return self._bbox_distance_threshold

    @bbox_distance_threshold.setter
    def bbox_distance_threshold(self, value):
        if not isinstance(value, float):
            raise TypeError('Expected float, got {0} instead'.format(
                type(value).__name__
            ))
        self._bbox_distance_threshold = value
        self.bboxDistanceThresholdChanged()

    @property
    def vertex_distance_threshold(self):
        """Float: the vertex distance threshold value for pair finding."""
        return self._vertex_distance_threshold

    @vertex_distance_threshold.setter
    def vertex_distance_threshold(self, value):
        if not isinstance(value, float):
            raise TypeError('Expected float, got {0} instead'.format(
                type(value).__name__
            ))
        self._vertex_distance_threshold = value
        self.vertexDistanceThresholdChanged()

    @property
    def connection_mode(self):
        """Int: Connection method used."""
        return self._connection_mode

    @connection_mode.setter
    def connection_mode(self, value):
        if value not in [
            Settings.IN_MESH_OUT_MESH_MODE,
            Settings.BLENDSHAPE_MODE,
            Settings.WRAP_MODE,
            Settings.PARENT_MODE
        ]:
            raise TypeError('Wrong connection mode type.')
        self._connection_mode = value
        self.connectionModeChanged()

    @property
    def inherit_visibility(self):
        """Bool: Whether to transfer meshes visibility attributes."""
        return self._inherit_visibility

    @inherit_visibility.setter
    def inherit_visibility(self, value):
        if not isinstance(value, bool):
            raise TypeError('Expected bool, got {0} instead'.format(
                type(value).__name__
            ))
        self._inherit_visibility = value
        self.inheritVisibilityChanged()

    @property
    def inherit_transform(self):
        """Bool: Whether to transfer meshes transform."""
        return self._inherit_transform

    @inherit_transform.setter
    def inherit_transform(self, value):
        if not isinstance(value, bool):
            raise TypeError('Expected bool, got {0} instead'.format(
                type(value).__name__
            ))
        self._inherit_transform = value
        self.inheritTransformChanged()

    @property
    def allow_multi_pairs(self):
        """Bool: Whether to transfer meshes transform."""
        return self._allow_multi_pairs

    @allow_multi_pairs.setter
    def allow_multi_pairs(self, value):
        if not isinstance(value, bool):
            raise TypeError('Expected bool, got {0} instead'.format(
                type(value).__name__
            ))
        self._allow_multi_pairs = value
        self.allowMultiPairsChanged()

    @property
    def edited_item(self):
        """ItemHandler.Item: item for which pairs are edited."""
        return self._edited_item

    @edited_item.setter
    def edited_item(self, value):
        if not isinstance(value, Item):
            raise TypeError(
                'Expected ItemHandler.Item, got {0} instead'.format(
                    type(value).__name__
                )
            )
        self._edited_item = value

    @property
    def selected_item(self):
        """ItemHandler.Item: the currently selected item."""
        return self._selected_item

    @selected_item.setter
    def selected_item(self, value):
        if value is not None and not isinstance(value, Item):
            raise TypeError(
                'Expected ItemHandler.Item, got {0} instead'.format(
                    type(value).__name__
                )
            )
        self._selected_item = value

    # ####################################################################### #
    #                          Item related methods                           #
    # ####################################################################### #

    def buildItem(
        self, name, display_name, full_path, point_count, vertex_position,
        bbox, world_matrix, item_type
    ):
        """Build and add an item to the given type list.

        Parameters
        ----------
        name: str
            String used for item name comparaison.
        display_name: str
            The name to display for this item.
        full_path: str
            The full path string to the maya geometry.
        point_count: int
            The vertex count of the maya geometry.
        vertex_position: OpenMaya.MVector
            The world space position of the first vertex.
        bbox: OpenMaya.MBoundingBox
            The bouding box of the maya geometry.
        world_matrix: OpenMaya.MMatrix
            The world transform matrix of the maya geometry.
        item_type: int
            The type of the item.

        Returns
        --------
        ItemHandler.Item
            The built item.

        """
        return self._itemHandler.buildItem(
            name=name,
            display_name=display_name,
            full_path=full_path,
            point_count=point_count,
            vertex_position=vertex_position,
            bbox=bbox,
            world_matrix=world_matrix,
            item_type=item_type
        )

    def addItems(self, items):
        """Add items.

        Parameters
        ----------
        item: set of ItemHanlder.Item
            The items to add.

        """
        for item in items:
            self._itemHandler.addItem(item.type, item)
        self.itemsChanged()

    def clearItems(self, item_type):
        """Empty the list of items corresponding to the given type.

        Parameters
        ----------
        item_type: int
            The type of items to return (Settings.SOURCE_GEOS or
            Settings.DESTINATION_GEOS)

        Raises
        -------
        RuntimeError
            Wrong geometry type passed.

        """
        self._itemHandler.clearData(item_type)
        self.itemsChanged()

    def hasItem(self, item, ignore_type=False):
        """Return whether the given item exists.

        Parameter
        ---------
        item: ItemHandler.Item
            The item to find.
        ignore_type: bool
            Whether to check for both item type.

        Returns
        -------
        bool
            The item existence.

        """
        if ignore_type:
            other_type = Settings.SOURCE_GEOS
            if item.type == other_type:
                other_type = Settings.DESTINATION_GEOS
            return (
                self._itemHandler.hasItem(other_type, str(item)) or
                self._itemHandler.hasItem(item.type, str(item))
            )
        return self._itemHandler.hasItem(item.type, str(item))

    def getItem(self, item_type, name):
        """Return the item with the given name for the given type.

        Return None if no item with given name can be found.
        Parameters
        ----------
        item_type: int
            The type of items to return (Settings.SOURCE_GEOS or
            Settings.DESTINATION_GEOS)
        name: str
            The name of the item to find.

        Raises
        -------
        RuntimeError
            Wrong geometry type passed.

        Returns
        -------
        Model.Item or None
            The item with given name and given type.

        """
        if not self._itemHandler.hasItem(item_type, name):
            return
        return self._itemHandler.getItem(item_type, name)

    def getItems(self, item_type):
        """Return the list of items corresponding to the given type.

        Parameters
        ----------
        item_type: int
            The type of items to return (Settings.SOURCE_GEOS or
            Settings.DESTINATION_GEOS)

        Raises
        -------
        RuntimeError
            Wrong geometry type passed.

        Returns
        -------
        list of Model.Items
            The items for the given type.

        """
        return self._itemHandler.getItems(item_type)

    def getItemPairs(self, item):
        """Return an Item tuple for each connection for the given item.

        Parameters
        ----------
        item: ItemHanlder.Item
            The item for which to retrieve the connections.

        Returns
        --------
        set of tuples
            The item pairs for each connection.

        """
        if item is None:
            return set()
        connections = self._connectionHandler.getItemConnections(item)
        return set([
            self._connectionHandler.getConnectionItems(connection)
            for connection in connections
        ])

    def removeItem(self, item_type, name):
        """Remove the item wih given name from the given type list.

        Parameters
        ----------
        item_type: int
            The type of items to return (Settings.SOURCE_GEOS or
            Settings.DESTINATION_GEOS)
        name: str
            The name of the item to remove.

        Raises
        -------
        RuntimeError
            Wrong geometry type passed.

        """
        if self._itemHandler.hasItem(item_type, name):
            self._itemHandler.removeItem(item_type, name)
            self.itemsChanged()

    def getItemDisplay(self, item):
        """Return the data used for colors and icon assignement.

        Parameters
        ----------
        item: ItemHanlder.Item
            The item for which to get the color and icon.

        Returns
        -------
        dict
            The data used for color and icon assignment.

        """
        data = dict({'color': None, 'icon': None})
        if item is None:
            return data

        data['color'] = (
            len(self._connectionHandler.getItemConnections(item)),
            item.disabled
        )
        data['icon'] = (
            len(self._connectionHandler.getItemExtraConnections(item)),
            len(self._connectionHandler.getItemSuppressedConnections(item))
        )
        return data

    # ####################################################################### #
    #                       Connection related methods                        #
    # ####################################################################### #

    def getItemConnections(self, item):
        """Return a list of connections for given item.

        Parameters
        ----------
        item: ItemHandler.Item
            The item for which to get the connections.

        Returns
        -------
        list of ConnectionHanlder.Connection
            The connections containing the given item.

        """
        if item is None:
            return
        return self._connectionHandler.getItemConnections(item)

    def clearItemConnectionOverrides(self, item):
        """Remove all extra and suppressed connection data for given item.

        Paramters
        ---------
        item: ItemHandler.Item
            The item for which to clear the extra and suppressed connection
            data.

        """
        if item is None:
            return
        self._connectionHandler.removeItemOverrides(item)

    def addItemConnection(self, source, destination, extra=False):
        """Add a connection between the source and destination items.

        If the extra flag is True, the new connection is added by either
        creating an extra connection or removing a suppressed connection
        if it exists between the two items. Otherwise a normal item connection
        is created.

        Parameters
        -----------
        source: ItemHandler.Item
            The source item to connect.
        destination: ItemHandler.Item
            The destination item to connect.
        extra: bool
            Whether to create the new connection as an override or a regular
            connection.

        """
        if source is None or destination is None:
            return
        if extra:
            self._connectionHandler.addItemConnection(source, destination)
        else:
            self._connectionHandler.addConnection(source, destination)

    def removeItemConnection(self, source, destination):
        """Remove a connection between the source and destination items.

        The new connection is removed by either deleting an extra connection
        if it exists between the two items or creating a suppressed connection.

        Parameters
        -----------
        source: ItemHandler.Item
            The source item to connect.
        destination: ItemHandler.Item
            The destination item to connect.

        """
        if source is None or destination is None:
            return
        self._connectionHandler.removeItemConnection(source, destination)

    def clearConnections(self):
        """Remove all stored connections."""
        self._connectionHandler.clearConnections()
