# -*- coding: utf-8 -*-
"""Model of the Pair Connector."""


class ConnectionHandler(object):
    """Collection of methods to handle Connections."""

    def __init__(self):
        """Create the regular, extra ant suppressed connection sets."""
        self._connections = set()
        self._extra_connections = set()
        self._suppressed_connections = set()

    def _getConnections(self):
        """Return all the connections stored.

        The extra and suppressed connections are respecively added and removed
        (in that order) for the regular ones to represent the final connection
        set.

        Returns
        --------
        set of ConnectionHandler.Connections
            The stored connections.

        """
        return (
            (
                self._connections |
                self._extra_connections
            ) - self._suppressed_connections
        )

    def clear(self):
        """Remove all stored connection data."""
        self.clearConnections()
        self.clearOverrides()

    def clearOverrides(self):
        """Remove all extra and suppressed connection data."""
        self._extra_connections.clear()
        self._suppressed_connections.clear()

    def clearConnections(self):
        """Remove all regular connection data."""
        self._connections.clear()

    def addConnection(self, source, destination):
        """Add a regular connection between the source and destination.

        Parameters
        ----------
        source: ItemHandler.Item
            The source item.
        destination: ItemHandler.Item
            The destination item.

        """
        self._connections.add(Connection(source, destination))

    def addItemConnection(self, source, destination):
        """Add an override connection between the source and destination.

        If the connection was suppressed, the suppressed connection data is
        removed. Otherwise an extra connection is created.

        Parameters
        ----------
        source: ItemHandler.Item
            The source item.
        destination: ItemHandler.Item
            The destination item.

        """
        connection = Connection(source, destination)
        if connection in self._suppressed_connections:
            self._suppressed_connections.remove(connection)
        else:
            self._extra_connections.add(connection)

    def removeItemConnection(self, source, destination):
        """Remove a connection between the source and destination.

        If the connection was an extra connection, it is removed. Otherwise
        a suppressed connection is created.

        Parameters
        ----------
        source: ItemHandler.Item
            The source item.
        destination: ItemHandler.Item
            The destination item.

        """
        connection = Connection(source, destination)
        if connection in self._extra_connections:
            self._extra_connections.remove(connection)
        else:
            self._suppressed_connections.add(connection)

    def removeItemOverrides(self, item):
        """Remove all extra and suppressed connections affecting an item.

        Parameters
        ----------
        item: ItemHandler.Item
            The item for which to remove the connection overrides.

        """
        self._extra_connections = self._extra_connections.difference(
            self.getItemExtraConnections(item)
        )

        self._suppressed_connections = self._suppressed_connections.difference(
            self.getItemSuppressedConnections(item)
        )

    def getItemConnections(self, item):
        """Return the connections affecting the given item.

        Parameters
        ----------
        item: ItemHanlder.Item
            The item affected by the connections.

        Returns
        -------
        list of ConnectionHandler.Connection
            The connections affecting the given item.

        """
        connections = self._getConnections()
        return set([
            connection
            for connection in connections
            if connection.hasItem(item)
        ])

    def getItemExtraConnections(self, item):
        """Return the extra connections affecting the given item.

        Parameters
        ----------
        item: ItemHanlder.Item
            The item affected by the connections.

        Returns
        -------
        list of ConnectionHandler.Connection
            The extra connections affecting the given item.

        """
        return set([
            connection
            for connection in self._extra_connections
            if connection.hasItem(item)
        ])

    def getItemSuppressedConnections(self, item):
        """Return the suppressed connections affecting the given item.

        Parameters
        ----------
        item: ItemHanlder.Item
            The item affected by the connections.

        Returns
        -------
        list of ConnectionHandler.Connection
            The suppressed connections affecting the given item.

        """
        return set([
            connection
            for connection in self._suppressed_connections
            if connection.hasItem(item)
        ])

    def getConnectionItems(self, connection):
        """Return the source and destination items of a connection.

        Parameters
        ----------
        connection: ConnectionHandler.Connection
            The connection from which to extract the data.

        Returns
        -------
        tuple of ItemHandler.Item
            The source and destination items.

        """
        return (connection.source, connection.destination)


class Connection(object):
    """Data storing class representing a pair connection between two items."""

    def __init__(self, source, destination):
        """Store the source and destination items.

        Parameters
        -----------
        source: ItemHandler.Item
            The source item of the connection.
        destination: ItemHandler.Item
            The destination item of the connection.

        """
        self._source = source
        self._destination = destination

    @property
    def source(self):
        """ItemHandler.Item: the source item of the connection."""
        return self._source

    @property
    def destination(self):
        """ItemHandler.Item: the destination item of the connection."""
        return self._destination

    def hasItem(self, item):
        """Return wheter the given item is part of the connection.

        Parameters
        ----------
        item: ItemHandler.Item
            The item to check.

        Returns
        --------
        bool
            Whether the item is part of the connection.

        """
        return item == self._source or item == self._destination

    def __repr__(self):
        """Return a string representing the connection."""
        return '{} to {}'.format(self.source, self.destination)

    def __eq__(self, other):
        """Compare two connection by comparing their source and destination.

        The connection will be equal to the other one if both sources are the
        same and both destination are the same or if the source of one is the
        destination of the other and vice versa.

        """
        if not isinstance(other, Connection):
            return False
        return (
            (
                self._source == other.source and
                self._destination == other.destination
            ) or (
                self._source == other.destination and
                self._destination == other.source
            )
        )

    def __hash__(self):
        """Return a hash using source and destination items."""
        return hash(str(self.source)) ^ hash(str(self.destination))
