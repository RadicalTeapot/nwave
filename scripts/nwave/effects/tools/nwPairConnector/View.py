# -*- coding: utf-8 -*-
"""View of the Pair Connector."""

from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets

from Settings import Settings

from UI import PairEditorPanel
from UI import UI

import os


class View(QtWidgets.QMainWindow):
    """Class for the view of the Pair Connector.

    Attributes
    ----------
    objectName: str
        The name of the tool.

    """

    object_name = 'Pair Connector'

    def __init__(self, parent=None):
        """Initialize the view, setup the ui and the methods."""
        super(View, self).__init__(parent)

        self._right_clicked_list = None
        self._right_clicked_item = None

        self._setupUi()
        self._setupMethods()
        self._connectSignals()

    def _setupUi(self):
        """Create the tool ui."""
        self.setObjectName(self.object_name)
        UI.setupUi(self)
        self._edit_pair_panel = PairEditorPanel(self)
        self._edit_pair_panel.resize(*Settings.EDIT_PAIR_DIALOG_SIZE)
        self.resize(*Settings.WINDOW_SIZE)

    def _setupMethods(self):
        """Create the methods to be called when an ui event is called."""
        self.loadGeometries = lambda geo_type: None
        self.updatePairDetectionMode = lambda: None

        self.updateBboxDistanceThreshold = lambda: None
        self.updateVertexDistanceThreshold = lambda: None

        self.updateConnectionMode = lambda: None
        self.updateInheritVisibility = lambda: None
        self.updateInheritTransform = lambda: None
        self.updateAllowMultiPairs = lambda: None

        self.connect = lambda: None
        self.closeTool = lambda: None

        self.clearList = lambda geo_type: None
        self.removeItem = lambda geo_type, item_name: None
        self.selectItem = lambda geo_type, item_name: None
        self.selectPairedItems = lambda geo_type, item_name: None

        self.editPairData = lambda geo_type, item_name: None
        self.resetPairData = lambda geo_type, item_name: None
        self.editPairAdd = lambda: None
        self.editPairRemove = lambda selected_items: None
        self.editPairSelect = lambda selected_items: None
        self.updatePairData = lambda new_pairs: None

        self.itemClicked = lambda geo_type, item_name: None
        self.selectionCleared = lambda geo_type: None

    def _connectSignals(self):
        """Connect qt object signals to internal methods."""
        self._loadSimulatedGeoBtn.clicked.connect(self._loadSimulatedGeos)
        self._loadAssetGeoBtn.clicked.connect(self._loadAssetGeos)

        self._useDistanceRadio.clicked.connect(
            self._updatePairDetectionMode
        )
        self._useVerticesRadio.clicked.connect(
            self._updatePairDetectionMode
        )
        self._useNameRadio.clicked.connect(
            self._updatePairDetectionMode
        )
        self._useTransformRadio.clicked.connect(
            self._updatePairDetectionMode
        )

        self._bboxDistanceThresholdSpin.valueChanged.connect(
            self._updateBboxDistanceThreshold
        )
        self._vertexDistanceThresholdSpin.valueChanged.connect(
            self._updateVertexDistanceThreshold
        )

        self._inMeshOutMeshRadio.clicked.connect(
            self._updateConnectionMode
        )
        self._blendshapeRadio.clicked.connect(
            self._updateConnectionMode
        )
        self._wrapRadio.clicked.connect(
            self._updateConnectionMode
        )
        self._parentRadio.clicked.connect(
            self._updateConnectionMode
        )

        self._visibilityCheck.stateChanged.connect(
            self._updateInheritVisibility
        )
        self._inheritsTransformCheck.stateChanged.connect(
            self._updateInheritTransform
        )
        self._allowMultiPairsCheck.stateChanged.connect(
            self._updateAllowMultiPairs
        )

        self._connectBtn.clicked.connect(self._connect)
        self._closeBtn.clicked.connect(self._closeTool)

        self._sourceGeometriesList.rightClicked.connect(
            self._sourceListRightClicked
        )
        self._sourceGeometriesList.itemRightClicked.connect(
            self._sourceItemRightClicked
        )
        self._destinationGeometriesList.rightClicked.connect(
            self._destinationListRightClicked
        )
        self._destinationGeometriesList.itemRightClicked.connect(
            self._destinationItemRightClicked
        )

        self._list_right_click_menu.clear_list_action.triggered.connect(
            self._clearList
        )

        self._item_right_click_menu.remove_item_action.triggered.connect(
            self._removeItem
        )
        self._item_right_click_menu.select_item_action.triggered.connect(
            self._selectItem
        )
        self._item_right_click_menu.select_paired_items_action.\
            triggered.connect(self._selectPairedItems)
        self._item_right_click_menu.edit_pair_data_action.triggered.connect(
            self._editPairData
        )
        self._item_right_click_menu.reset_pair_data_action.triggered.connect(
            self._resetPairData
        )

        self._edit_pair_panel._add_button.clicked.connect(self._editPairAdd)
        self._edit_pair_panel._remove_button.clicked.connect(
            self._editPairRemove
        )
        self._edit_pair_panel._select_button.clicked.connect(
            self._editPairSelect
        )
        self._edit_pair_panel._close_button.clicked.connect(
            self._editPairClose
        )

        self._sourceGeometriesList.itemClicked.connect(
            self._sourceItemClicked
        )
        self._destinationGeometriesList.itemClicked.connect(
            self._destinationItemClicked
        )

        self._sourceGeometriesList.selectionCleared.connect(
            self._sourceSelectionCleared
        )
        self._destinationGeometriesList.selectionCleared.connect(
            self._destinationSelectionCleared
        )

    # ####################################################################### #
    #                            Internal Methods                             #
    # ####################################################################### #

    def _loadSimulatedGeos(self):
        """Fetch selected geometries and add them to simulated geos list.

        This method is called when the load simulated geometries button is
        clicked.

        """
        self.loadGeometries(Settings.SOURCE_GEOS)

    def _loadAssetGeos(self):
        """Fetch selected geometries and add them to asset geos list.

        This method is called when the load asset geometries button is
        clicked.

        """
        self.loadGeometries(Settings.DESTINATION_GEOS)

    def _updatePairDetectionMode(self):
        """Update the pair detection mode.

        This method is called when a pair detection radio button is clicked.

        """
        self.updatePairDetectionMode()

    def _updateBboxDistanceThreshold(self):
        """Update the bbox distance threshold value.

        This method is called when the bbox distance threshold spin value is
        changed.

        """
        self.updateBboxDistanceThreshold()

    def _updateVertexDistanceThreshold(self):
        """Update the vertex distance threshold value.

        This method is called when the vertex distance threshold spin value is
        changed.

        """
        self.updateVertexDistanceThreshold()

    def _updateConnectionMode(self):
        """Update the connection mode.

        This method is called when a connection radio button is clicked.

        """
        self.updateConnectionMode()

    def _updateInheritVisibility(self):
        """Update the inherit visibility connection value.

        This method is called when the inherit visibility toggle state is
        changed.

        """
        self.updateInheritVisibility()

    def _updateInheritTransform(self):
        """Update the inherit transform connection value.

        This method is called when the inherit transform toggle state is
        changed.

        """
        self.updateInheritTransform()

    def _updateAllowMultiPairs(self):
        """Update the allow multi pairs value.

        This method is called when the allow multi pairs toggle state is
        changed.

        """
        self.updateAllowMultiPairs()

    def _connect(self):
        """Connect the geometry pairs together.

        This method is called when the connect button is clicked.
        """
        self.connect()

    def _closeTool(self):
        """Close the tool.

        This method is called when the close button is clicked.
        """
        self.closeTool()

    def _displayListRightClickMenu(self, x, y):
        """Open the right click menu for lists.

        Parameters
        -----------
        x: int
            The horizontal position at which to display the right click menu.
        y: int
            The vertical position at which to display the right click menu.

        """
        self._list_right_click_menu.popup(QtCore.QPoint(x, y))

    def _sourceListRightClicked(self, x, y):
        """Open the right click menu for lists.

        This method is called when an empty space in the source list
        is right clicked.
        Parameters
        -----------
        x: int
            The horizontal position at which to display the right click menu.
        y: int
            The vertical position at which to display the right click menu.

        """
        self._right_clicked_list = Settings.SOURCE_GEOS
        self._displayListRightClickMenu(x, y)

    def _sourceItemRightClicked(self, item, x, y):
        """Open the right click menu for items.

        This method is called when an item in the source list is right clicked.
        Parameters
        -----------
        x: int
            The horizontal position at which to display the right click menu.
        y: int
            The vertical position at which to display the right click menu.

        """
        self._right_clicked_list = Settings.SOURCE_GEOS
        self._displayItemRightClickMenu(item, x, y)

    def _destinationListRightClicked(self, x, y):
        """Open the right click menu for lists.

        This method is called when an empty space in the destination list
        is right clicked.
        Parameters
        -----------
        x: int
            The horizontal position at which to display the right click menu.
        y: int
            The vertical position at which to display the right click menu.

        """
        self._right_clicked_list = Settings.DESTINATION_GEOS
        self._displayListRightClickMenu(x, y)

    def _destinationItemRightClicked(self, item, x, y):
        """Open the right click menu for items.

        This method is called when an item in the destination list
        is right clicked.
        Parameters
        -----------
        x: int
            The horizontal position at which to display the right click menu.
        y: int
            The vertical position at which to display the right click menu.

        """
        self._right_clicked_list = Settings.DESTINATION_GEOS
        self._displayItemRightClickMenu(item, x, y)

    def _displayItemRightClickMenu(self, item, x, y):
        """Open the right click menu for items.

        This method is called when an item is right clicked.
        Parameters
        -----------
        x: int
            The horizontal position at which to display the right click menu.
        y: int
            The vertical position at which to display the right click menu.

        """
        self._right_clicked_item = item
        self._item_right_click_menu.popup(QtCore.QPoint(x, y))

    def _clearList(self):
        """Remove all items from the right clicked list.

        This method is called when the 'Clear items' option is clicked in
        a list right click menu.
        """
        self.clearList(self._right_clicked_list)

    def _removeItem(self):
        """Remove the right clicked items from it's list.

        This method is called when the 'Remove item' option is clicked in
        an item right click menu.
        """
        self.removeItem(
            self._right_clicked_list, str(self._right_clicked_item.text())
        )

    def _selectItem(self):
        """Select the right clicked item in maya.

        This method is called when the 'Select item' option is clicked
        in an item right click menu.
        """
        self.selectItem(
            self._right_clicked_list, str(self._right_clicked_item.text())
        )

    def _selectPairedItems(self):
        """Select the paired items of the right clicked item in maya.

        This method is called when the 'Select paired items' option is clicked
        in an item right click menu.
        """
        self.selectPairedItems(
            self._right_clicked_list, str(self._right_clicked_item.text())
        )

    def _editPairData(self):
        """Open the pair editor dialog for the right clicked item.

        This method is called when the 'Edit pair data' option is clicked
        in an item right click menu.
        """
        self.editPairData(
            self._right_clicked_list,
            str(self._right_clicked_item.text())
        )

    def _resetPairData(self):
        """Delete all connection overrides containing the right clicked item.

        This method is called when the 'Reset pair data' option is clicked
        in an item right click menu.
        """
        self.resetPairData(
            self._right_clicked_list,
            str(self._right_clicked_item.text())
        )

    def _editPairAdd(self):
        """Add selected geometries as an extra pair to the right clicked item.

        This method is called when the 'Add' button of the pair editor dialog
        is clicked.
        """
        self.editPairAdd()

    def _editPairRemove(self):
        """Remove selected item as a pair override to the right clicked item.

        This method is called when the 'Remove' button of the pair editor
        dialog is clicked.
        """
        items = self._edit_pair_panel._pair_list.selectedItems()
        if items:
            self.editPairRemove([str(item.text()) for item in items])

    def _editPairSelect(self):
        """Select in maya the selected item in the pair editor dialog.

        This method is called when the 'Select item' button of the pair editor
        dialog is clicked.
        """
        items = self._edit_pair_panel._pair_list.selectedItems()
        if items:
            self.editPairSelect([str(item.text()) for item in items])

    def _editPairClose(self):
        """Close the pair editor dialog.

        This method is called when the 'Close' button of the pair editor dialog
        is clicked.
        """
        self._edit_pair_panel.hide()

    def _sourceItemClicked(self, item):
        """Mark the selected item from the source list as selected.

        This method is called an item from the source list is clicked.
        """
        self.itemClicked(Settings.SOURCE_GEOS, str(item.text()))

    def _destinationItemClicked(self, item):
        """Mark the selected item from the destination list as selected.

        This method is called an item from the destination list is clicked.
        """
        self.itemClicked(Settings.DESTINATION_GEOS, str(item.text()))

    def _sourceSelectionCleared(self):
        """Clear the selected source list item.

        This method is called an empty space in the source list is clicked.
        """
        self.selectionCleared(Settings.SOURCE_GEOS)

    def _destinationSelectionCleared(self):
        """Clear the selected destination list item.

        This method is called an empty space in the destination list
        is clicked.
        """
        self.selectionCleared(Settings.DESTINATION_GEOS)

    # ####################################################################### #
    #                            Getters / Setters                            #
    # ####################################################################### #

    @property
    def pair_detection_mode(self):
        """Int: pair detection algorithm used."""
        mode = None
        if self._useDistanceRadio.isChecked():
            mode = Settings.DISTANCE_MODE
        elif self._useVerticesRadio.isChecked():
            mode = Settings.VERTEX_MODE
        elif self._useNameRadio.isChecked():
            mode = Settings.NAME_MODE
        elif self._useTransformRadio.isChecked():
            mode = Settings.TRANSFORM_MODE

        return mode

    @pair_detection_mode.setter
    def pair_detection_mode(self, value):
        # Disable controls
        for control in [
            self._bboxDistanceThresholdSpin, self._bboxDistanceLabel,
            self._vertexDistanceThresholdSpin, self._vertexDistanceLabel
        ]:
            control.setEnabled(False)

        # Check radio button based on given mode and active related controls
        if value == Settings.DISTANCE_MODE:
            self._useDistanceRadio.setChecked(True)
            self._bboxDistanceThresholdSpin.setEnabled(True)
            self._bboxDistanceLabel.setEnabled(True)
        elif value == Settings.VERTEX_MODE:
            self._useVerticesRadio.setChecked(True)
            self._vertexDistanceThresholdSpin.setEnabled(True)
            self._vertexDistanceLabel.setEnabled(True)
        elif value == Settings.NAME_MODE:
            self._useNameRadio.setChecked(True)
        elif value == Settings.TRANSFORM_MODE:
            self._useTransformRadio.setChecked(True)
        else:
            raise TypeError('Wrong pair detection mode type.')

    @property
    def bbox_distance_threshold(self):
        """Float: the bbox distance threshold value for pair finding."""
        return float(self._bboxDistanceThresholdSpin.value())

    @bbox_distance_threshold.setter
    def bbox_distance_threshold(self, value):
        if not isinstance(value, float):
            raise TypeError('Expected float, got {0} instead'.format(
                type(value).__name__
            ))
        self._bboxDistanceThresholdSpin.blockSignals(True)
        self._bboxDistanceThresholdSpin.setValue(value)
        self._bboxDistanceThresholdSpin.blockSignals(False)

    @property
    def vertex_distance_threshold(self):
        """Float: the bbox distance threshold value for pair finding."""
        return float(self._vertexDistanceThresholdSpin.value())

    @vertex_distance_threshold.setter
    def vertex_distance_threshold(self, value):
        if not isinstance(value, float):
            raise TypeError('Expected float, got {0} instead'.format(
                type(value).__name__
            ))
        self._vertexDistanceThresholdSpin.blockSignals(True)
        self._vertexDistanceThresholdSpin.setValue(value)
        self._vertexDistanceThresholdSpin.blockSignals(False)

    @property
    def connection_mode(self):
        """Int: The method to use to connect the paired geometries."""
        mode = None
        if self._inMeshOutMeshRadio.isChecked():
            mode = Settings.IN_MESH_OUT_MESH_MODE
        elif self._blendshapeRadio.isChecked():
            mode = Settings.BLENDSHAPE_MODE
        elif self._wrapRadio.isChecked():
            mode = Settings.WRAP_MODE
        elif self._parentRadio.isChecked():
            mode = Settings.PARENT_MODE

        return mode

    @connection_mode.setter
    def connection_mode(self, value):
        if not isinstance(value, int):
            raise TypeError('Expected int, got {0} instead'.format(
                type(value).__name__
            ))
        if value == Settings.IN_MESH_OUT_MESH_MODE:
            self._inMeshOutMeshRadio.setChecked(True)
        elif value == Settings.BLENDSHAPE_MODE:
            self._blendshapeRadio.setChecked(True)
        elif value == Settings.WRAP_MODE:
            self._wrapRadio.setChecked(True)
        elif value == Settings.PARENT_MODE:
            self._parentRadio.setChecked(True)
        else:
            raise TypeError('Wrong connection mode type.')

    @property
    def inherit_visibility(self):
        """Bool: Whether to transfer meshes visibility attributes."""
        return bool(self._visibilityCheck.isChecked())

    @inherit_visibility.setter
    def inherit_visibility(self, value):
        if not isinstance(value, bool):
            raise TypeError('Expected bool, got {0} instead'.format(
                type(value).__name__
            ))
        self._visibilityCheck.blockSignals(True)
        self._visibilityCheck.setChecked(value)
        self._visibilityCheck.blockSignals(False)

    @property
    def inherit_transform(self):
        """Bool: Whether to transfer meshes transform."""
        return bool(self._inheritsTransformCheck.isChecked())

    @inherit_transform.setter
    def inherit_transform(self, value):
        if not isinstance(value, bool):
            raise TypeError('Expected bool, got {0} instead'.format(
                type(value).__name__
            ))
        self._inheritsTransformCheck.blockSignals(True)
        self._inheritsTransformCheck.setChecked(value)
        self._inheritsTransformCheck.blockSignals(False)

    @property
    def allow_multi_pairs(self):
        """Bool: Whether to transfer meshes transform."""
        return bool(self._allowMultiPairsCheck.isChecked())

    @allow_multi_pairs.setter
    def allow_multi_pairs(self, value):
        if not isinstance(value, bool):
            raise TypeError('Expected bool, got {0} instead'.format(
                type(value).__name__
            ))
        self._allowMultiPairsCheck.blockSignals(True)
        self._allowMultiPairsCheck.setChecked(value)
        self._allowMultiPairsCheck.blockSignals(False)

    # ####################################################################### #
    #                         Lists related methods                           #
    # ####################################################################### #

    def _getList(self, geo_type):
        """Return the UI list controller for the given geometry type.

        Raises
        -------
        RuntimeError
            Wrong geometry type passed.

        Returns
        -------
        QtWidgets.QListWidget
            The list controller.

        """
        if geo_type == Settings.SOURCE_GEOS:
            return self._sourceGeometriesList
        elif geo_type == Settings.DESTINATION_GEOS:
            return self._destinationGeometriesList
        raise RuntimeError('Wrong geometry type.')

    def getGeometries(self, geo_type):
        """Return the content of a geometry list for the given type.

        Parameters
        ----------
        geo_type: int
            The type of geometries to return (Settings.SOURCE_GEOS or
            Settings.DESTINATION_GEOS)

        Raises
        -------
        RuntimeError
            Wrong geometry type passed.

        Returns
        -------
        list of str or None
            The geometries for the given type.

        """
        controller = self._getList(geo_type)

        items = [
            str(controller.item(row).text())
            for row in range(controller.count())
        ]

        if not items:
            return None

        return items

    def setGeometries(self, geo_type, data):
        """Set the content of a geometry list for the given type.

        Parameters
        ----------
        geo_type: int
            The type of geometries to return (Settings.SOURCE_GEOS or
            Settings.DESTINATION_GEOS)
        data: list of tuples or None
            The name and color for items to put in the geometry list.

        Raises
        -------
        RuntimeError
            Wrong geometry type passed.

        """
        controller = self._getList(geo_type)
        controller.clear()

        if data is None:
            return

        for name, color_data, icon_data in data:
            item = QtWidgets.QListWidgetItem(name)

            color = self._getColor(*color_data)
            item.setForeground(color['foreground'])
            item.setBackground(color['background'])

            icon = self._getIcon(*icon_data)
            if icon:
                item.setIcon(icon)

            controller.addItem(item)

    def selectGeometry(self, geo_type, name):
        """Select the item with given name in the list of given type.

        Parameters
        ----------
        geo_type: int
            The type of the list where the item is located.
        name: str
            The name of the item to select.

        """
        controller = self._getList(geo_type)
        items = [
            controller.item(index)
            for index in range(controller.count())
            if controller.item(index).text() == name
        ]
        for item in items:
            item.setSelected(True)

    def showEditPairDialog(self, item_name, paired_items):
        """Open the pair editor dialog.

        Parameters
        ----------
        item_name: str
            The name of the item for which to edit the pair data.
        paired_items: list of str
            The list of currently paired items for the item name.

        """
        self.updateEditPairDialog(item_name, paired_items)
        self._edit_pair_panel.show()

    def updateEditPairDialog(self, item_name, paired_items):
        """Update the pair dialog item list.

        Parameters
        ----------
        item_name: str
            The name of the item for which to edit the pair data.
        paired_items: list of str
            The list of currently paired items for the item name.

        """
        self._edit_pair_panel.loadItem(item_name, paired_items)

    # ####################################################################### #
    #                              Other Methods                              #
    # ####################################################################### #

    def enableConnect(self):
        """Set the connect button to be enabled."""
        self._connectBtn.setEnabled(True)

    def disableConnect(self):
        """Set the connect button to be disabled."""
        self._connectBtn.setEnabled(False)

    def _getColor(self, connection_count, disabled):
        """Return the foreground and background color as QBrushes for an item.

        Parameters
        ----------
        connection_count: int
            The count of connections of the item.
        disabled: bool
            Whether the item is disabled.

        Returns
        -------
        dictionary
            The QBrushes for item foreground and background.

        """
        colors = dict({
            'foreground': Settings.FOREGROUND,
            'background': Settings.NON_PAIRED_COLOR
        })
        if not disabled:
            if connection_count == 1:
                colors['background'] = Settings.PAIRED_COLOR
            elif connection_count > 1:
                colors['background'] = Settings.MULTI_PAIR_COLOR
        else:
            colors['foreground'] = Settings.DISABLED_FOREGROUND
            colors['background'] = Settings.DISABLED_NON_PAIRED_COLOR
            if connection_count == 1:
                colors['background'] = Settings.DISABLED_PAIRED_COLOR
            elif connection_count > 1:
                colors['background'] = Settings.DISABLED_MULTI_PAIR_COLOR

        return dict({
            'foreground': QtGui.QBrush(QtGui.QColor(*colors['foreground'])),
            'background': QtGui.QBrush(QtGui.QColor(*colors['background']))
        })

    def _getIcon(self, added, removed):
        """Return the icon for an item.

        Parameters
        ----------
        added: int
            The count of extra connections of the item.
        removed: int
            The count of suppressed connections of the item

        Returns
        -------
        QIcon
            The icon (or None) to assign to the item.

        """
        path = ""
        if added > 0 and removed == 0:
            path = Settings.ADDED_ICON_PATH
        elif added == 0 and removed > 0:
            path = Settings.REMOVED_ICON_PATH
        elif added > 0 and removed > 0:
            path = Settings.MODIFIED_ICON_PATH
        else:
            return None

        return QtGui.QIcon(os.path.join(os.path.dirname(__file__), path))
