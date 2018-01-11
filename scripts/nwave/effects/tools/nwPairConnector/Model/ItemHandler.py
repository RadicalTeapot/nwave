# -*- coding: utf-8 -*-
"""Model of the Pair Connector."""

from nwave.effects.tools.nwPairConnector.Settings import Settings


# ########################################################################### #
#                            Item related classes                             #
# ########################################################################### #

class ItemHandler(object):
    """Collection of methods to handle Items."""

    def __init__(self):
        """Create the source and destination items dictonnaries."""
        self._source_items = dict()
        self._destination_items = dict()

    def _getData(self, item_type):
        """Return the list for the given item type.

        Raises
        -------
        RuntimeError
            Wrong item type passed.

        Returns
        -------
        list
            The list.

        """
        if item_type == Settings.SOURCE_GEOS:
            return self._source_items
        elif item_type == Settings.DESTINATION_GEOS:
            return self._destination_items
        raise RuntimeError('Wrong item type.')

    def buildItem(
        self, name, display_name, full_path, point_count, vertex_position,
        bbox, world_matrix, item_type
    ):
        """Build and return an ItemHandler.Item.

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
        -------
        ItemHandler.Item
            The item.

        """
        return Item(
            name=name,
            display_name=display_name,
            full_path=full_path,
            point_count=point_count,
            vertex_position=vertex_position,
            bbox=bbox,
            world_matrix=world_matrix,
            item_type=item_type
        )

    def addItem(self, item_type, item):
        """Add the given item to the item dictonary of the given type.

        Parameters
        ----------
        item_type: int
            The type of item to add.
        item: ItemHandler.Item
            The item to add.

        """
        self._getData(item_type)[str(item)] = item

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
            Wrong item type passed.

        Returns
        -------
        list of Model.Items
            The items for the given type.

        """
        return self._getData(item_type).values()

    def updateData(self, item_type, items):
        """Update the item list corresponding to the given type.

        Parameters
        ----------
        item_type: int
            The type of items to return (Settings.SOURCE_GEOS or
            Settings.DESTINATION_GEOS)
        items: dict of Model.Items
            The items to save for the given type.

        Raises
        -------
        RuntimeError
            Wrong geometry type passed.

        """
        self._getData(item_type).update(items)

    def clearData(self, item_type):
        """Empty the item list corresponding to the given type.

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
        self._getData(item_type).clear()

    def hasItem(self, item_type, name):
        """Return if an item with the given name exists for the given type.

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
        bool
            The item existence.

        """
        return name in self._getData(item_type)

    def getItem(self, item_type, name):
        """Return the item with the given name and the given type.

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
        KeyError
            Item with given name is not in given type list.

        Returns
        -------
        Model.Item
            The item with given name and given type.

        """
        return self._getData(item_type)[name]

    def removeItem(self, item_type, name):
        """Remove the item with given name from the given type list.

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
        KeyError
            Item with given name is not in given type list.

        """
        del self._getData(item_type)[name]


class Item(object):
    """Data storing class representing a geometry to be paired."""

    def __init__(
        self, name, display_name, full_path, item_type, point_count,
        vertex_position, bbox, world_matrix
    ):
        """Store data representing a maya geometry.

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

        """
        self.name = name
        self.display_name = display_name
        self.full_path = full_path
        self.point_count = point_count
        self.vertex_position = vertex_position
        self.bbox = bbox
        self.world_matrix = world_matrix
        self.type = item_type
        self.disabled = False

    def __repr__(self):
        """Return the display name of the item."""
        return self.display_name

    def __eq__(self, other):
        """Compare two items by comparing their full_path attribute."""
        if not isinstance(other, Item):
            raise TypeError('Expected Model.Item, got {0} instead'.format(
                type(other).__name__
            ))
        return self.full_path == other.full_path
