# -*- coding: utf-8 -*-
"""Ui for nwPairConnector."""

from PySide2 import QtCore
from PySide2 import QtWidgets


class PairItemList(QtWidgets.QListWidget):
    """Subclass of QListWidget to add signals.

    Attributes
    ----------
    itemRightClicked: QtCore.Signal
        Signal emitted when an item is right clicked.
    rightClicked: QtCore.Signal
        Signal emitted when an empty space in the list is right clicked.
    selectionCleared: QtCore.Signal
        Signal emitted when an empty space in the list is left clicked.

    """

    itemRightClicked = QtCore.Signal(
        QtWidgets.QListWidgetItem,
        int, int
    )
    rightClicked = QtCore.Signal(
        int, int
    )
    selectionCleared = QtCore.Signal()

    def __init__(self, parent=None):
        """Initialize the class parent method."""
        super(PairItemList, self).__init__(parent)

    def mouseReleaseEvent(self, event):
        """Override the mouseReleaseEvent of the QListWidget."""
        item = self.itemAt(event.pos())
        if item:
            if (event.button() == QtCore.Qt.RightButton):
                self.itemRightClicked.emit(
                    item, event.globalX(), event.globalY()
                )
            else:
                super(PairItemList, self).mouseReleaseEvent(event)
        else:
            if (event.button() == QtCore.Qt.RightButton):
                self.rightClicked.emit(event.globalX(), event.globalY())
            else:
                self.clearSelection()
                self.selectionCleared.emit()
        event.accept()


class RightClickMenu(QtWidgets.QMenu):
    """Subclass of QMenu displayed when right clicking."""

    def __init__(self, parent):
        """Initialize the class parent method."""
        super(RightClickMenu, self).__init__(parent)

    @classmethod
    def itemRightClick(cls, parent):
        """Create an instance of the menu for item right clicking."""
        self = cls(parent)

        self.edit_pair_data_action = QtWidgets.QAction(parent)
        self.edit_pair_data_action.setText("Edit pair data")
        self.addAction(self.edit_pair_data_action)

        self.reset_pair_data_action = QtWidgets.QAction(parent)
        self.reset_pair_data_action.setText("Reset pair data")
        self.addAction(self.reset_pair_data_action)

        self.select_item_action = QtWidgets.QAction(parent)
        self.select_item_action.setText("Select item")
        self.addAction(self.select_item_action)

        self.select_paired_items_action = QtWidgets.QAction(parent)
        self.select_paired_items_action.setText("Select paired item(s)")
        self.addAction(self.select_paired_items_action)

        self.remove_item_action = QtWidgets.QAction(parent)
        self.remove_item_action.setText("Remove item")
        self.addAction(self.remove_item_action)

        return self

    @classmethod
    def listRightClick(cls, parent):
        """Create an instance of the menu for list right clicking."""
        self = cls(parent)

        self.clear_list_action = QtWidgets.QAction(parent)
        self.clear_list_action.setText("Clear Items")
        self.addAction(self.clear_list_action)

        return self


class PairEditorPanel(QtWidgets.QDialog):
    """Dialog to edit pair."""

    def __init__(self, parent):
        """Create the UI and initialize the class parent."""
        super(PairEditorPanel, self).__init__(parent)

        self._item = None
        self.setupUi()

    def setupUi(self):
        """Create the UI."""
        main_layout = QtWidgets.QHBoxLayout(self)

        self._pair_list = PairItemList()
        main_layout.addWidget(self._pair_list)

        layout = QtWidgets.QVBoxLayout()
        self._add_button = QtWidgets.QPushButton("Add")
        layout.addWidget(self._add_button)
        self._remove_button = QtWidgets.QPushButton("Remove")
        layout.addWidget(self._remove_button)
        self._select_button = QtWidgets.QPushButton("Select")
        layout.addWidget(self._select_button)
        layout.addStretch()
        self._close_button = QtWidgets.QPushButton("Done")
        layout.addWidget(self._close_button)

        main_layout.addLayout(layout)

    def loadItem(self, item_name, paired_items):
        """Load the given item and populate the pair list.

        Parameters
        ----------
        item_name: str
            The name of the item to edit.
        paired_items: list of str
            The items used to populated the pair list.

        """
        self._item = item_name
        self._pair_list.clear()
        self._pair_list.addItems(paired_items)


class UI(object):
    """Class for the UI of the Pair Connector."""

    @staticmethod
    def setupUi(tool_window):
        """Create and attach UI controls to the tool window.

        Parameters
        -----------
        tool_window: View
            The tool's View.

        """
        central_widget = QtWidgets.QWidget(tool_window)
        tool_window.setCentralWidget(central_widget)

        main_layout = QtWidgets.QHBoxLayout(central_widget)

        # ################################################################### #
        #                     Simulated Geometries Panel                      #
        # ################################################################### #

        layout = QtWidgets.QVBoxLayout()

        label = QtWidgets.QLabel("Source Geometries :")
        layout.addWidget(label)

        tool_window._sourceGeometriesList = PairItemList(central_widget)
        layout.addWidget(tool_window._sourceGeometriesList)

        tool_window._loadSimulatedGeoBtn = QtWidgets.QPushButton(
            "Load From Selection"
        )
        layout.addWidget(tool_window._loadSimulatedGeoBtn)

        main_layout.addLayout(layout)

        # ################################################################### #
        #                       Asset Geometries Panel                        #
        # ################################################################### #

        layout = QtWidgets.QVBoxLayout()

        label = QtWidgets.QLabel("Destination Geometries :")
        layout.addWidget(label)

        tool_window._destinationGeometriesList = PairItemList(central_widget)
        layout.addWidget(tool_window._destinationGeometriesList)

        tool_window._loadAssetGeoBtn = QtWidgets.QPushButton(
            "Load From Selection"
        )
        layout.addWidget(tool_window._loadAssetGeoBtn)

        main_layout.addLayout(layout)

        verticalLayout = QtWidgets.QVBoxLayout()

        # ################################################################### #
        #                        Pair Detection Panel                         #
        # ################################################################### #

        groupBox = QtWidgets.QGroupBox("Pair Detection")
        layout = QtWidgets.QVBoxLayout(groupBox)

        # Distance mode

        tool_window._useDistanceRadio = QtWidgets.QRadioButton(groupBox)
        tool_window._useDistanceRadio.setText("Use Distance")
        layout.addWidget(tool_window._useDistanceRadio)

        horizontalLayout = QtWidgets.QHBoxLayout()
        tool_window._bboxDistanceLabel = QtWidgets.QLabel("Distance Threshold")
        horizontalLayout.addWidget(tool_window._bboxDistanceLabel)

        tool_window._bboxDistanceThresholdSpin = QtWidgets.QDoubleSpinBox(
            groupBox
        )
        tool_window._bboxDistanceThresholdSpin.setButtonSymbols(
            QtWidgets.QAbstractSpinBox.NoButtons
        )
        tool_window._bboxDistanceThresholdSpin.setDecimals(3)
        tool_window._bboxDistanceThresholdSpin.setMinimum(0.001)
        tool_window._bboxDistanceThresholdSpin.setMaximum(10000.0)
        horizontalLayout.addWidget(tool_window._bboxDistanceThresholdSpin)
        layout.addLayout(horizontalLayout)

        # Vertex mode

        line = QtWidgets.QFrame(groupBox)
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        layout.addWidget(line)

        tool_window._useVerticesRadio = QtWidgets.QRadioButton(groupBox)
        tool_window._useVerticesRadio.setText("Use Vertices")
        layout.addWidget(tool_window._useVerticesRadio)

        horizontalLayout = QtWidgets.QHBoxLayout()
        tool_window._vertexDistanceLabel = QtWidgets.QLabel(
            "Distance Threshold"
        )
        horizontalLayout.addWidget(tool_window._vertexDistanceLabel)

        tool_window._vertexDistanceThresholdSpin = QtWidgets.QDoubleSpinBox(
            groupBox
        )
        tool_window._vertexDistanceThresholdSpin.setButtonSymbols(
            QtWidgets.QAbstractSpinBox.NoButtons
        )
        tool_window._vertexDistanceThresholdSpin.setDecimals(3)
        tool_window._vertexDistanceThresholdSpin.setMinimum(0.001)
        tool_window._vertexDistanceThresholdSpin.setMaximum(10000.0)
        horizontalLayout.addWidget(tool_window._vertexDistanceThresholdSpin)
        layout.addLayout(horizontalLayout)

        # Name mode

        line = QtWidgets.QFrame(groupBox)
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        layout.addWidget(line)

        tool_window._useNameRadio = QtWidgets.QRadioButton(groupBox)
        tool_window._useNameRadio.setText("Use name")
        layout.addWidget(tool_window._useNameRadio)

        # Transform mode

        line = QtWidgets.QFrame(groupBox)
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        layout.addWidget(line)

        tool_window._useTransformRadio = QtWidgets.QRadioButton(groupBox)
        tool_window._useTransformRadio.setText("Use transform")
        layout.addWidget(tool_window._useTransformRadio)

        verticalLayout.addWidget(groupBox)

        # ################################################################### #
        #                          Connections Panel                          #
        # ################################################################### #

        groupBox = QtWidgets.QGroupBox("Connections")
        layout = QtWidgets.QVBoxLayout(groupBox)

        tool_window._inMeshOutMeshRadio = QtWidgets.QRadioButton(
            "InMesh - OutMesh"
        )
        layout.addWidget(tool_window._inMeshOutMeshRadio)

        tool_window._blendshapeRadio = QtWidgets.QRadioButton(groupBox)
        tool_window._blendshapeRadio.setText("Blendshape")
        layout.addWidget(tool_window._blendshapeRadio)

        tool_window._wrapRadio = QtWidgets.QRadioButton(groupBox)
        tool_window._wrapRadio.setText("Wrap")
        layout.addWidget(tool_window._wrapRadio)

        tool_window._parentRadio = QtWidgets.QRadioButton(groupBox)
        tool_window._parentRadio.setText("Parent")
        layout.addWidget(tool_window._parentRadio)

        line = QtWidgets.QFrame(groupBox)
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        layout.addWidget(line)

        tool_window._visibilityCheck = QtWidgets.QCheckBox(groupBox)
        tool_window._visibilityCheck.setText("Visibility")
        layout.addWidget(tool_window._visibilityCheck)

        line = QtWidgets.QFrame(groupBox)
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        layout.addWidget(line)

        tool_window._inheritsTransformCheck = QtWidgets.QCheckBox(groupBox)
        tool_window._inheritsTransformCheck.setText("Inherits Transform")
        layout.addWidget(tool_window._inheritsTransformCheck)

        line = QtWidgets.QFrame(groupBox)
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        layout.addWidget(line)

        tool_window._allowMultiPairsCheck = QtWidgets.QCheckBox(groupBox)
        tool_window._allowMultiPairsCheck.setText("Allow multi pairs")
        layout.addWidget(tool_window._allowMultiPairsCheck)

        verticalLayout.addWidget(groupBox)
        verticalLayout.addStretch()

        # ################################################################### #
        #                       Connect / Close Buttons                       #
        # ################################################################### #

        main_layout.addLayout(verticalLayout)
        horizontalLayout_2 = QtWidgets.QHBoxLayout()

        tool_window._connectBtn = QtWidgets.QPushButton("Connect")
        horizontalLayout_2.addWidget(tool_window._connectBtn)

        tool_window._closeBtn = QtWidgets.QPushButton("Close")
        horizontalLayout_2.addWidget(tool_window._closeBtn)

        verticalLayout.addLayout(horizontalLayout_2)

        # ################################################################### #
        #                          Right Click Menus                          #
        # ################################################################### #

        tool_window._item_right_click_menu = RightClickMenu.itemRightClick(
            tool_window
        )
        tool_window._list_right_click_menu = RightClickMenu.listRightClick(
            tool_window
        )
