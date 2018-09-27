# -*- coding: utf-8 -*-
"""Common methods of the Zefir reader."""

import hou


class Utils:
    """Collection of methods of the Zefir reader."""

    @staticmethod
    def bestNodePosition(offset=(3, 0)):
        """Return a hou.Vector2 representing a position in the ntework editor.

        Parameters
        ----------
        offset: (int, int)
            A tuple representing the quantity of offset space to leave between
            exisiting nodes and the new node placement on x and y axes.

        Raises
        ------
        RuntimeError
            If no network editor tab can be found.

        Returns
        -------
        hou.Vector2
            The placement for the new node.

        """
        # Get all the network editor tabs
        network_editors = filter(
            lambda tab:
                tab.type() == hou.paneTabType.NetworkEditor,
            hou.ui.paneTabs()
        )
        if not network_editors:
            raise RuntimeError('Could not find an open network editor.')

        rects = []
        # Find the fist netwrok editor with visible nodes
        for network_editor in network_editors:
            rects = network_editor.allVisibleRects([])
            if rects:
                break

        right = -1e6
        top = -1e6
        for rect in rects[1:]:
            pos = rect[0].position()
            if pos[1] > top:
                top = pos[1]
            if pos[0] > right:
                right = pos[0]
        return hou.Vector2(right + offset[0], top + offset[1])
