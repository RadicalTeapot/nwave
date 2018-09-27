# -*- coding: utf-8 -*-
"""UI of the Fenix Committer."""

from PySide2 import QtWidgets


class UI(object):
    """Class for the UI of the Fenix Committer."""

    @staticmethod
    def setup_ui(view):
        """Attach ui controls to given view.

        Parameters
        ----------
        view: PySide2.QtWidgets.QMainWindow
            The tool window.

        """
        view.setObjectName(view.object_name)
        view.setWindowTitle('Fenix Committer')
        view.resize(600, 400)

        central_widget = QtWidgets.QWidget()
        view.setCentralWidget(central_widget)

        main_layout = QtWidgets.QHBoxLayout(central_widget)

        layout = QtWidgets.QVBoxLayout()

        sub_layout = QtWidgets.QHBoxLayout()
        label = QtWidgets.QLabel()
        label.setText('Assets :')
        sub_layout.addWidget(label)
        sub_layout.addStretch()
        layout.addLayout(sub_layout)

        view.asset_list = QtWidgets.QListWidget()
        view.asset_list.setSelectionMode(
            QtWidgets.QAbstractItemView.SingleSelection
        )
        layout.addWidget(view.asset_list)

        sub_layout = QtWidgets.QHBoxLayout()
        sub_layout.addStretch()
        view.add_asset_button = QtWidgets.QPushButton()
        view.add_asset_button.setText('Add')
        sub_layout.addWidget(view.add_asset_button)
        view.remove_asset_button = QtWidgets.QPushButton()
        view.remove_asset_button.setText('Remove')
        sub_layout.addWidget(view.remove_asset_button)
        layout.addLayout(sub_layout)

        main_layout.addLayout(layout)

        vertical_layout_2 = QtWidgets.QVBoxLayout()
        view.commit_on_farm_check = QtWidgets.QCheckBox("Commit On Farm")
        view.commit_on_farm_check.setChecked(False)
        vertical_layout_2.addWidget(view.commit_on_farm_check)
        group_box = QtWidgets.QGroupBox()
        group_box.setTitle("Asset's geo group")
        horizontal_layout_6 = QtWidgets.QHBoxLayout(group_box)
        horizontal_layout_3 = QtWidgets.QHBoxLayout()
        view.commit_to_alembic_anim_check = QtWidgets.QCheckBox(group_box)
        view.commit_to_alembic_anim_check.setText(
            "Commit to Alembic Animation stage"
        )
        horizontal_layout_3.addWidget(view.commit_to_alembic_anim_check)
        horizontal_layout_3.addStretch()
        horizontal_layout_6.addLayout(horizontal_layout_3)
        vertical_layout_2.addWidget(group_box)
        group_box_2 = QtWidgets.QGroupBox()
        group_box_2.setTitle("Asset's effects group")
        vertical_layout = QtWidgets.QVBoxLayout(group_box_2)
        horizontal_layout_5 = QtWidgets.QHBoxLayout()
        view.commit_to_fx_cache_check = QtWidgets.QCheckBox(group_box_2)
        view.commit_to_fx_cache_check.setText("Commit to FX Cache stage")
        horizontal_layout_5.addWidget(view.commit_to_fx_cache_check)
        horizontal_layout_5.addStretch()
        vertical_layout.addLayout(horizontal_layout_5)
        horizontal_layout_4 = QtWidgets.QHBoxLayout()
        horizontal_layout_4.addStretch()
        view.generate_alembic_from_geo_check = QtWidgets.QCheckBox(group_box_2)
        view.generate_alembic_from_geo_check.setText(
            "Generate Alembic from geometries"
        )
        horizontal_layout_4.addWidget(view.generate_alembic_from_geo_check)
        horizontal_layout_4.addStretch()
        vertical_layout.addLayout(horizontal_layout_4)
        horizontal_layout_5 = QtWidgets.QHBoxLayout()
        horizontal_layout_5.addStretch()
        view.generate_local_space_alembic_check = QtWidgets.QCheckBox(
            group_box_2
        )
        view.generate_local_space_alembic_check.setText(
            "Use local space for the Alembic"
        )
        horizontal_layout_5.addWidget(view.generate_local_space_alembic_check)
        horizontal_layout_5.addStretch()
        vertical_layout.addLayout(horizontal_layout_5)
        vertical_layout_2.addWidget(group_box_2)
        label_2 = QtWidgets.QLabel()
        label_2.setText("Comments")
        vertical_layout_2.addWidget(label_2)
        view.commit_text_edit = QtWidgets.QTextEdit()
        vertical_layout_2.addWidget(view.commit_text_edit)
        horizontalLayout_2 = QtWidgets.QHBoxLayout()
        horizontalLayout_2.addStretch()
        view.commit_btn = QtWidgets.QPushButton()
        view.commit_btn.setText("Commit")
        horizontalLayout_2.addWidget(view.commit_btn)
        view.close_btn = QtWidgets.QPushButton()
        view.close_btn.setText("Close")
        horizontalLayout_2.addWidget(view.close_btn)
        vertical_layout_2.addLayout(horizontalLayout_2)

        main_layout.addLayout(vertical_layout_2)
