# -*- coding: utf-8 -*-
"""The view of the mail generator."""

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5 import QtWebEngineWidgets

from Settings import Settings

import os


class TreeWidget(QtWidgets.QTreeWidget):
    """QTreeWidget with drop events and auto-header setup.

    Attributes
    ----------
    itemDropped: QtCore.pyqtSignal
        Signal emitted when an item is dropped.

    """

    itemDropped = QtCore.pyqtSignal()

    def __init__(self, parent=None, header_data=None):
        """Initialize the tree widget, setup the headers and column count.

        Parameters
        ----------
        parent: QObject
            Any QObject to be used as a parent for the tree widget.
        header_data: dict
            A dictionnary of the form {column_label, id}.

        """
        super(TreeWidget, self).__init__(parent)
        # Disable sorting as this will be done though drag and drop
        self.setSortingEnabled(False)
        # Set drag and drop mode
        self.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        # Set headers and column count
        if header_data:
            if not isinstance(header_data, dict):
                raise ValueError(
                    'Expected dict, got {0} instead.'.format(type(header_data))
                )
            self.setColumnCount(len(header_data))
            headers = sorted(
                header_data.items(),
                key=lambda item: item[1]
            )
            self.setHeaderLabels([
                key.capitalize()
                for key, __ in headers
            ])

    def dropEvent(self, event):
        """Trigger the itemDropped event."""
        super(TreeWidget, self).dropEvent(event)
        self.itemDropped.emit()


class TreeItem(QtWidgets.QTreeWidgetItem):
    """QTreeWidgetItem with path attribute and flag setup."""

    def __init__(self, parent=None, path=None):
        """Initialize the item, set it's path and flags."""
        super(TreeItem, self).__init__(parent)

        self.update(path)
        self.setIcon(View.MOVIES_DATA['delete'], QtGui.QIcon(View._TRASH_ICON))

        self.setFlags(
            QtCore.Qt.ItemIsSelectable |
            QtCore.Qt.ItemIsEnabled |
            QtCore.Qt.ItemIsDragEnabled |
            QtCore.Qt.ItemNeverHasChildren
        )

    def update(self, path):
        """Set the item path, text and trash icon."""
        self.path = path
        self.setText(View.MOVIES_DATA['name'], os.path.split(self.path)[-1])
        self.setToolTip(View.MOVIES_DATA['name'], self.path)


class View(QtWidgets.QMainWindow):
    """Class for the View of the mail generator.

    Attributes
    ----------
    objectName: str
        The name of the QMainWindow
    RECIPIENTS_DATA: dict
        Recipients tree header ids and names.
    MOVIES_DATA: dict
        Movies tree header ids and names.
    IMAGES_DATA: dict
        Image tree header ids and names.

    FILE_FILTER: dict
        File filters for movie and image loading file browsers.
    _TOOL_ICON: str
        Path to the QMainWindow icon.
    _TRASH_ICON: str
        Path to the the trash bin icon.

    """

    objectName = 'MailGenerator'

    RECIPIENTS_DATA = dict([
        ('address', 0),
        ('delete', 1)
    ])
    MOVIES_DATA = dict([
        ('name', 0),
        ('delete', 1)
    ])
    IMAGES_DATA = dict([
        ('name', 0),
        ('delete', 1)
    ])

    FILE_FILTER = dict([
        ('movie', 'Movies ({0})'.format(' '.join(Settings.MOVIE_TYPES))),
        ('image', 'Images ({0})'.format(' '.join(Settings.IMAGE_TYPES)))
    ])

    _TOOL_ICON = os.path.join(
        os.path.split(__file__)[0],
        'icons',
        'mail.png'
    )

    _TRASH_ICON = os.path.join(
        os.path.split(__file__)[0],
        'icons',
        'trash.png'
    )

    def __init__(self, parent=None):
        """Initialize the class, the ui and connect the signals."""
        super(View, self).__init__(parent)

        # Vars to store the folder of the last loaded movie and image
        self.last_movie_folder = "//nwave/projects/CORGI/PROD/SEQ"
        self.last_image_folder = "//nwave/projects/CORGI/PROD/SEQ"

        self._setupUi()
        self._setupMethods()
        self._connectSignals()

    def _setupUi(self):
        self.setObjectName(View.objectName)
        self.setWindowTitle(Settings.WINDOW_TITLE)
        self.setWindowIcon(QtGui.QIcon(View._TOOL_ICON))
        self.resize(Settings.WIDTH, Settings.HEIGHT)

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QtWidgets.QVBoxLayout(central_widget)

        splitter = QtWidgets.QSplitter(central_widget)
        main_layout.addWidget(splitter)

        self._html_viewer = QtWebEngineWidgets.QWebEngineView()
        splitter.addWidget(self._html_viewer)

        settings_widget = QtWidgets.QWidget()
        splitter.addWidget(settings_widget)

        splitter.setSizes([1, 1])

        settings_layout = QtWidgets.QVBoxLayout(settings_widget)

        settings_layout.addWidget(QtWidgets.QLabel('Mail Recipients'))
        self._recipients_list = TreeWidget(header_data=View.RECIPIENTS_DATA)
        settings_layout.addWidget(self._recipients_list)
        layout = QtWidgets.QHBoxLayout()
        settings_layout.addLayout(layout)
        layout.addWidget(QtWidgets.QLabel('New address :'))
        self._new_recipient_line = QtWidgets.QLineEdit()
        layout.addWidget(self._new_recipient_line)

        layout = QtWidgets.QHBoxLayout()
        settings_layout.addLayout(layout)

        layout.addWidget(QtWidgets.QLabel('Sequence : '))
        self._sequence_line = QtWidgets.QSpinBox()
        self._sequence_line.setButtonSymbols(
            QtWidgets.QAbstractSpinBox.NoButtons
        )
        self._sequence_line.setRange(0, 999)
        layout.addWidget(self._sequence_line)

        layout.addWidget(QtWidgets.QLabel('Shot : '))
        self._shot_line = QtWidgets.QSpinBox()
        self._shot_line.setButtonSymbols(
            QtWidgets.QAbstractSpinBox.NoButtons
        )
        self._shot_line.setRange(0, 999)
        layout.addWidget(self._shot_line)

        # layout.addStretch(1)

        layout = QtWidgets.QHBoxLayout()
        settings_layout.addLayout(layout)
        layout.addStretch(1)

        sub_layout = QtWidgets.QVBoxLayout()
        sub_layout.addWidget(QtWidgets.QLabel('FX Assets :'))
        self._fx_asset_list = QtWidgets.QListWidget()
        sub_layout.addWidget(self._fx_asset_list)
        layout.addLayout(sub_layout)
        layout.addStretch(1)

        sub_layout = QtWidgets.QVBoxLayout()
        sub_layout.addWidget(QtWidgets.QLabel('FX Tasks :'))
        self._fx_tasks_list = QtWidgets.QListWidget()
        sub_layout.addWidget(self._fx_tasks_list)
        layout.addLayout(sub_layout)

        layout.addStretch(1)

        settings_layout.addWidget(QtWidgets.QLabel('Movies'))
        self._movies_list = TreeWidget(header_data=View.MOVIES_DATA)
        settings_layout.addWidget(self._movies_list)
        layout = QtWidgets.QHBoxLayout()
        settings_layout.addLayout(layout)
        layout.addStretch(1)
        self._add_movie_button = QtWidgets.QPushButton('Add movie')
        layout.addWidget(self._add_movie_button)

        settings_layout.addWidget(QtWidgets.QLabel('Images'))
        self._images_list = TreeWidget(header_data=View.IMAGES_DATA)
        settings_layout.addWidget(self._images_list)
        layout = QtWidgets.QHBoxLayout()
        settings_layout.addLayout(layout)
        layout.addStretch(1)
        self._add_images_button = QtWidgets.QPushButton('Add image')
        layout.addWidget(self._add_images_button)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(QtWidgets.QLabel('Remarks'))
        self._remarks_edit = QtWidgets.QPlainTextEdit()
        layout.addWidget(self._remarks_edit)
        sub_layout = QtWidgets.QHBoxLayout()
        sub_layout.addStretch(1)
        self._volume_data = QtWidgets.QPushButton('Add Volume Data')
        sub_layout.addWidget(self._volume_data)
        layout.addLayout(sub_layout)
        settings_layout.addLayout(layout)

        layout = QtWidgets.QHBoxLayout()
        self._preview_button = QtWidgets.QPushButton('Preview')
        layout.addWidget(self._preview_button)
        layout.addStretch(1)
        self._send_button = QtWidgets.QPushButton('Send')
        layout.addWidget(self._send_button)
        self._close_button = QtWidgets.QPushButton('Close')
        layout.addWidget(self._close_button)

        settings_layout.addLayout(layout)

    def _setupMethods(self):
        self.preview = lambda: None
        self.send = lambda: None
        self.closeTool = lambda: None
        self.sequenceChanged = lambda: None
        self.shotChanged = lambda: None
        self.setRemark = lambda: None
        self.addVolumeData = lambda: None

        self.recipientAdded = lambda: None
        self.recipientChanged = lambda: None
        self.recipientDeleted = lambda: None
        self.recipientRenamed = lambda old_name, new_name: None

        self.movieAdded = lambda: None
        self.movieChanged = lambda: None
        self.movieDeleted = lambda: None

        self.imageAdded = lambda: None
        self.imageChanged = lambda: None
        self.imageDeleted = lambda: None

        self.assetChecked = lambda: None
        self.taskChecked = lambda: None

    def _connectSignals(self):
        self._preview_button.clicked.connect(self._preview)
        self._send_button.clicked.connect(self._send)
        self._close_button.clicked.connect(self._closeTool)
        self._sequence_line.editingFinished.connect(self._sequenceChanged)
        self._shot_line.editingFinished.connect(self._shotChanged)
        self._remarks_edit.textChanged.connect(self._setRemark)
        self._volume_data.clicked.connect(self._addVolumeData)

        self._new_recipient_line.returnPressed.connect(self._recipientAdded)
        self._recipients_list.itemChanged.connect(self._recipientChanged)
        self._recipients_list.itemDropped.connect(self._recipientChanged)
        self._recipients_list.itemClicked.connect(self._recipientDeleted)
        self._recipients_list.itemDoubleClicked.connect(self._recipientRenamed)

        self._add_movie_button.clicked.connect(self._movieAdded)
        self._movies_list.itemDoubleClicked.connect(self._setMoviePath)
        self._movies_list.itemDropped.connect(self._movieChanged)
        self._movies_list.itemClicked.connect(self._movieDeleted)

        self._add_images_button.clicked.connect(self._imageAdded)
        self._images_list.itemDoubleClicked.connect(self._setImagePath)
        self._images_list.itemDropped.connect(self._imageChanged)
        self._images_list.itemClicked.connect(self._imageDeleted)

        self._fx_asset_list.itemChanged.connect(self._assetChecked)
        self._fx_tasks_list.itemChanged.connect(self._taskChecked)

    # ####################################################################### #
    #                            Internal Methods                             #
    # ####################################################################### #

    def _preview(self):
        self.preview()

    def _send(self):
        success = self.send()

        if success:
            msg = QtWidgets.QMessageBox(self)
            msg.setText('Email successfully sent.')
            msg.exec_()

    def _closeTool(self):
        self.closeTool()

    def _sequenceChanged(self):
        self.sequenceChanged()

    def _shotChanged(self):
        self.shotChanged()

    def _setRemark(self):
        self.setRemark()

    def _addVolumeData(self):
        self.addVolumeData()

    def _getFilePaths(self, mode, folder):
        return QtWidgets.QFileDialog.getOpenFileNames(
            self,
            "Select one or more files to load",
            folder,
            View.FILE_FILTER[mode]
        )[0]

    # ####################################################################### #
    #                                Recipient                                #
    # ####################################################################### #

    def _recipientAdded(self):
        self.recipientAdded()

    def _recipientChanged(self):
        self.recipientChanged()

    def _recipientDeleted(self, item, column):
        if column != View.RECIPIENTS_DATA['delete']:
            return
        index = self._recipients_list.indexOfTopLevelItem(item)
        self._recipients_list.takeTopLevelItem(index)
        self.recipientDeleted()

    def _recipientRenamed(self, item, column):
        if column != View.RECIPIENTS_DATA['address']:
            return
        old_name = item.text(View.RECIPIENTS_DATA['address'])
        self.renameRecipient(old_name)

    @property
    def recipients(self):
        return [
            self._recipients_list.topLevelItem(index).text(
                View.RECIPIENTS_DATA['address']
            )
            for index in range(self._recipients_list.topLevelItemCount())
        ]

    @recipients.setter
    def recipients(self, value):
        if not isinstance(value, list):
            raise ValueError('Wrong data type {0}'.format(type(value)))

        self._recipients_list.clear()

        for recipient in value:
            # item = MailItem(self._recipients_list)
            item = QtWidgets.QTreeWidgetItem()
            item.setText(View.RECIPIENTS_DATA['address'], recipient)
            item.setIcon(
                View.RECIPIENTS_DATA['delete'],
                QtGui.QIcon(View._TRASH_ICON)
            )

            item.setFlags(
                QtCore.Qt.ItemIsSelectable |
                QtCore.Qt.ItemIsEnabled |
                QtCore.Qt.ItemIsDragEnabled |
                QtCore.Qt.ItemNeverHasChildren
            )

            self._recipients_list.addTopLevelItem(item)
        self._recipients_list.resizeColumnToContents(
            View.RECIPIENTS_DATA['address']
        )

    @property
    def new_recipient(self):
        return self._new_recipient_line.text()

    # ####################################################################### #
    #                                  Movie                                  #
    # ####################################################################### #

    def _movieAdded(self):
        paths = self._getFilePaths('movie', self.last_movie_folder)
        if not paths:
            return

        for path in paths:
            if path in self.movies:
                continue
            self._movies_list.addTopLevelItem(TreeItem(path=path))

        self.last_movie_folder = os.path.split(paths[-1])[0]

        self.movieAdded()

    def _setMoviePath(self, item, column):
        if column != View.MOVIES_DATA['name']:
            return
        new_file, __ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Select a new file",
            item.path,
            View.FILE_FILTER['movie']
        )
        if not new_file:
            return

        item.update(new_file)
        self.movieChanged()

    def _movieChanged(self):
        self.movieChanged()

    def _movieDeleted(self, item, column):
        if column != View.MOVIES_DATA['delete']:
            return
        index = self._movies_list.indexOfTopLevelItem(item)
        self._movies_list.takeTopLevelItem(index)
        self.movieDeleted()

    @property
    def movies(self):
        return[
            self._movies_list.topLevelItem(index).path
            for index in range(self._movies_list.topLevelItemCount())
        ]

    @movies.setter
    def movies(self, value):
        if not isinstance(value, list):
            raise ValueError('Wrong data type {0}'.format(type(value)))

        self._movies_list.clear()

        for path in value:
            self._movies_list.addTopLevelItem(TreeItem(path=path))

        self._movies_list.resizeColumnToContents(View.MOVIES_DATA['name'])

    # ####################################################################### #
    #                                  Image                                  #
    # ####################################################################### #

    def _imageAdded(self):
        paths = self._getFilePaths('image', self.last_image_folder)
        if not paths:
            return

        for path in paths:
            if path in self.images:
                continue
            self._images_list.addTopLevelItem(TreeItem(path=path))

        self.last_image_folder = os.path.split(paths[-1])[0]

        self.imageAdded()

    def _setImagePath(self, item, column):
        if column != View.IMAGES_DATA['name']:
            return
        new_file, __ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Select a new file",
            item.path,
            View.FILE_FILTER['image']
        )
        if not new_file:
            return

        item.update(new_file)
        self.imageChanged()

    def _imageChanged(self):
        self.imageChanged()

    def _imageDeleted(self, item, column):
        if column != View.IMAGES_DATA['delete']:
            return
        index = self._images_list.indexOfTopLevelItem(item)
        self._images_list.takeTopLevelItem(index)
        self.imageDeleted()

    @property
    def images(self):
        return[
            self._images_list.topLevelItem(index).path
            for index in range(self._images_list.topLevelItemCount())
        ]

    @images.setter
    def images(self, value):
        if not isinstance(value, list):
            raise ValueError('Wrong data type {0}'.format(type(value)))

        self._images_list.clear()

        for path in value:
            self._images_list.addTopLevelItem(TreeItem(path=path))

        self._images_list.resizeColumnToContents(View.MOVIES_DATA['name'])

    # ####################################################################### #
    #                                 Assets                                  #
    # ####################################################################### #

    def _assetChecked(self):
        self.assetChecked()

    @property
    def assets(self):
        return [
            self._fx_asset_list.item(index).text()
            for index in range(self._fx_asset_list.count())
        ]

    def getCheckedAsset(self):
        return [
            self._fx_asset_list.item(index).text()
            for index in range(self._fx_asset_list.count())
            if (
                self._fx_asset_list.item(index).checkState()
                == QtCore.Qt.Checked
            )
        ]

    @assets.setter
    def assets(self, value):
        if not isinstance(value, list):
            raise ValueError('Wrong data type {0}'.format(type(value)))

        self._fx_asset_list.clear()
        for asset in sorted(value):
            item = QtWidgets.QListWidgetItem()
            item.setFlags(
                QtCore.Qt.ItemIsEnabled |
                QtCore.Qt.ItemIsUserCheckable
            )
            item.setCheckState(QtCore.Qt.Unchecked)
            item.setText(asset)
            self._fx_asset_list.addItem(item)

    # ####################################################################### #
    #                                  Tasks                                  #
    # ####################################################################### #

    def _taskChecked(self):
        self.taskChecked()

    @property
    def tasks(self):
        return [
            self._fx_tasks_list.item(index).text()
            for index in range(self._fx_tasks_list.count())
            if (
                self._fx_tasks_list.item(index).checkState() ==
                QtCore.Qt.Checked
            )
        ]

    @tasks.setter
    def tasks(self, value):
        if not isinstance(value, list):
            raise ValueError('Wrong data type {0}'.format(type(value)))

        self._fx_tasks_list.clear()
        for asset in sorted(value):
            item = QtWidgets.QListWidgetItem()
            item.setFlags(
                QtCore.Qt.ItemIsEnabled |
                QtCore.Qt.ItemIsUserCheckable
            )
            item.setCheckState(QtCore.Qt.Unchecked)
            item.setText(asset)
            self._fx_tasks_list.addItem(item)

    # ####################################################################### #
    #                            Getters / Setters                            #
    # ####################################################################### #

    @property
    def remark(self):
        return self._remarks_edit.toPlainText()

    @remark.setter
    def remark(self, value):
        if not isinstance(value, str):
            raise ValueError('Wrong data type {0}'.format(type(value)))
        self._remarks_edit.setPlainText(value)

    @property
    def sequence(self):
        return int(self._sequence_line.value())

    @property
    def shot(self):
        return int(self._shot_line.value())

    # ####################################################################### #
    #                             Regular Methods                             #
    # ####################################################################### #

    def renameRecipient(self, old_name):
        new_name, success = QtWidgets.QInputDialog.getText(
            self,
            'New email address',
            'Enter new email address',
            text=old_name
        )
        if not success:
            return
        self.recipientRenamed(old_name, new_name)

    def setHtml(self, html):
        self._html_viewer.setHtml(html)

    def displayWarning(self, title, text):
        return QtWidgets.QMessageBox.warning(
            self,
            title,
            text
        )
