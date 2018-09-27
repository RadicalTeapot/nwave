# -*- coding: utf-8 -*-
"""View of the Fenix Committer."""

from PySide2 import QtWidgets
from ui import UI


class View(QtWidgets.QMainWindow):
    """Class for the view of the Fenix Committer.

    Attributes
    ----------

    objectName: str
        The name of the tool.

    """

    object_name = 'fenix_commiter_window'

    def __init__(self, parent=None):
        """Initialize the view, setup the ui and the methods."""
        super(View, self).__init__(parent)

        UI.setup_ui(self)
        self._setup_methods()
        self._connect_signals()

        self.reset_ui()

    def _setup_methods(self):
        """Create the methods to be called when an ui event is called."""
        self.select_asset = lambda item_names: None
        self.add_assets = lambda: None
        self.remove_assets = lambda item_names: None
        self.update_assets = lambda: None
        self.commit = lambda: None

    def _connect_signals(self):
        """Connect qt object signals to internal methods."""
        self.asset_list.itemSelectionChanged.connect(self._select_asset)

        self.add_asset_button.clicked.connect(self._add_assets)
        self.remove_asset_button.clicked.connect(self._remove_assets)

        self.commit_on_farm_check.stateChanged.connect(self._commit_on_farm)
        self.commit_to_alembic_anim_check.stateChanged.connect(
            self._commit_to_alembic_anim
        )
        self.commit_to_fx_cache_check.stateChanged.connect(
            self._commit_to_fx_cache
        )
        self.generate_alembic_from_geo_check.stateChanged.connect(
            self._generate_alembic_from_geo
        )
        self.generate_local_space_alembic_check.stateChanged.connect(
            self._generate_local_space_alembic
        )
        self.commit_text_edit.textChanged.connect(self._commit_text)

        self.commit_btn.clicked.connect(self._commit)
        self.close_btn.clicked.connect(self.close)

    def _block_signals(self, state):
        """Block or unblock signals coming from ui controls.

        Parameters
        ----------
        state: bool
            Whether to block or unblock signals.

        """
        self.commit_on_farm_check.blockSignals(state)
        self.commit_to_alembic_anim_check.blockSignals(state)
        self.commit_to_fx_cache_check.blockSignals(state)
        self.generate_alembic_from_geo_check.blockSignals(state)
        self.generate_local_space_alembic_check.blockSignals(state)
        self.commit_text_edit.blockSignals(state)

    def reset_ui(self):
        """Reset the ui to it's neutral state."""
        self._block_signals(True)
        self.commit_on_farm_check.setEnabled(False)
        self.commit_on_farm_check.setChecked(False)
        self.commit_to_alembic_anim_check.setEnabled(False)
        self.commit_to_alembic_anim_check.setChecked(False)
        self.commit_to_fx_cache_check.setEnabled(False)
        self.commit_to_fx_cache_check.setChecked(False)
        self.generate_alembic_from_geo_check.setEnabled(False)
        self.generate_alembic_from_geo_check.setChecked(False)
        self.generate_local_space_alembic_check.setEnabled(False)
        self.generate_local_space_alembic_check.setChecked(False)
        self.commit_text_edit.setEnabled(False)
        self.commit_text_edit.setText('')
        self._block_signals(False)

    def update_ui(
        self,
        commit_on_farm=False,
        commit_to_alembic_anim=False,
        can_commit_to_fx_cache=False,
        commit_to_fx_cache=False,
        generate_alembic_from_geos=False,
        use_local_space_for_alembic=False,
        comments=''
    ):
        """Update specified ui controls.

        Parameters
        -----------
        commit_on_farm: bool
            Checked state of this control.
        commit_to_alembic_anim: bool
            Checked state of this control.
        can_commit_to_fx_cache: bool
            Whether the current asset can be commited to fx cache.
        commit_to_fx_cache: bool
            Checked state of this control.
        generate_alembic_from_geos: bool
            Checked state of this control.
        use_local_space_for_alembic: bool
            Checked state of this control.
        comments: str
            The comments for the commit.

        """
        self._block_signals(True)

        self.commit_on_farm_check.setEnabled(True)
        self.commit_on_farm_check.setChecked(commit_on_farm)
        self.commit_to_alembic_anim_check.setEnabled(True)
        self.commit_to_alembic_anim_check.setChecked(commit_to_alembic_anim)
        self.commit_text_edit.setEnabled(True)
        self.commit_text_edit.setText(comments)

        if not can_commit_to_fx_cache:
            self.commit_to_fx_cache_check.setEnabled(False)
            self.commit_to_fx_cache_check.setChecked(False)
            self.generate_alembic_from_geo_check.setEnabled(False)
            self.generate_alembic_from_geo_check.setChecked(False)
            self.generate_local_space_alembic_check.setEnabled(False)
            self.generate_local_space_alembic_check.setChecked(False)
        else:
            self.commit_to_fx_cache_check.setEnabled(True)
            self.commit_to_fx_cache_check.setChecked(commit_to_fx_cache)
            self.generate_alembic_from_geo_check.setEnabled(True)
            self.generate_alembic_from_geo_check.setChecked(
                generate_alembic_from_geos
            )
            self.generate_local_space_alembic_check.setEnabled(True)
            self.generate_local_space_alembic_check.setChecked(
                use_local_space_for_alembic
            )

        self._block_signals(False)

    def build_items(self, item_names):
        """Rebuild asset list with given item names.

        Parameters
        ----------
        item_names: list of str
            The name of the items to display in the list.

        """
        self.asset_list.clear()
        for item_name in item_names:
            self.asset_list.addItem(item_name)

    def _get_selected_assets(self):
        """Return selected item in ui asset list."""
        return [str(item.text()) for item in self.asset_list.selectedItems()]

    def _select_asset(self):
        """Callback method when an asset is selected in ui."""
        self.select_asset(self._get_selected_assets())

    def _add_assets(self):
        """Callback method when add button is clicked."""
        self.add_assets()

    def _remove_assets(self):
        """Callback method when remove button is clicked."""
        self.remove_assets(self._get_selected_assets())

    def _commit_on_farm(self):
        """Callback method when commit on farm control is checked."""
        self.update_assets(
            self._get_selected_assets(),
            commit_on_farm=self.commit_on_farm_check.isChecked()
        )

    def _commit_to_alembic_anim(self):
        """Callback method when commit to alembic anim control is checked."""
        self.update_assets(
            self._get_selected_assets(),
            commit_to_alembic_anim=self.commit_to_alembic_anim_check.isChecked()
        )

    def _commit_to_fx_cache(self):
        """Callback method when commit to fx cache control is checked."""
        self.update_assets(
            self._get_selected_assets(),
            commit_to_fx_cache=self.commit_to_fx_cache_check.isChecked()
        )

    def _generate_alembic_from_geo(self):
        """Callback method when generate alembic from geo control is checked."""
        state = self.generate_alembic_from_geo_check.isChecked()
        self.update_assets(
            self._get_selected_assets(),
            generate_alembic_from_geos=state
        )

    def _generate_local_space_alembic(self):
        """Callback method when generate local space control is checked."""
        state = self.generate_local_space_alembic_check.isChecked()
        self.update_assets(
            self._get_selected_assets(),
            use_local_space_for_alembic=state
        )

    def _commit_text(self):
        """Callback method when commit text is changed."""
        self.update_assets(
            self._get_selected_assets(),
            commit_text=self.commit_text_edit.toPlainText()
        )

    def _commit(self):
        """Callback method when commit button is clicked."""
        self.commit()

    def dialog(self, title, message, buttons):
        """Display a dialog with given buttons, title and message.

        The text of the clicked button is returned.

        Parameters
        ----------
        title: str
            The title of the dialog.
        message: str
            The message of the dialog.
        buttons: list of (str, bool) tuple
            The text for each button of the dialog box and whether the button
            has an accept role or a reject role (returned when hitting escape
            or dimissing the dialog).

        Returns
        str
            The selected button text.

        """
        msgBox = QtWidgets.QMessageBox()
        msgBox.setText(title)
        msgBox.setInformativeText(message)
        for button, positive in buttons:
            role = QtWidgets.QMessageBox.AcceptRole
            if not positive:
                role = QtWidgets.QMessageBox.RejectRole
            msgBox.addButton(button, role)
        msgBox.exec_()

        return str(msgBox.clickedButton().text())
