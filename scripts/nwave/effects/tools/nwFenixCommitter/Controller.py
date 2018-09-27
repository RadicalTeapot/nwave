# -*- coding: utf-8 -*-
"""Controller of the Fenix Committer."""

from nwave.effects.tools.nwFXTDTools.PipelineHelper import PipelineHelper
from nwave.effects.tools.nwFXTDTools.PipelineHelper import NotSetError

from nwave.effects.tools.nwFXTDTools import DisplayMayaDialog

import zefir
from zefir.settings import get_setting_value
from zefir.exceptions import AlreadyLockedError
from zefir.exceptions import NoAuthenticatedUserError

from fenix4maya.model.batch import Batch
from fenix4maya.model.maya_commit import MayaCommit
from fenix4maya.settings import MOTION_BLUR_SAMPLES_SETTING

from fenix.preferences import COMMIT_PROXY_CACHE
from fenix.preferences import COMMIT_WITH_RELATIVE_ANIMATION_OPTION
from fenix.preferences import COMMIT_WITHOUT_SIMULATION_OPTION
from fenix.preferences import CREATE_FROM_SOURCE_ASSET_OPTION
from fenix.preferences import EXPORT_ALL_NWOVERRIDE_SETS_OPTION
from fenix.preferences import KEEP_INVISIBLE_OBJECTS

import maya.cmds as mc
import maya.mel as mel

import os
from collections import Counter
from nwave.effects.tools.nwFenixCommitter.Settings import Settings


class AssetData(object):
    """Store data about an asset."""

    def __init__(self):
        """Initialize data storage."""
        self.asset = None
        self.item = None
        self.commit_on_farm = False
        self.commit_to_alembic_anim = False
        self.can_commit_to_fx_cache = True
        self.commit_to_fx_cache = False
        self.generate_alembic_from_geos = False
        self.use_local_space_for_alembic = False
        self.commit_text = ''


class Controller(object):
    """Class for the controller of the Fenix Committer."""

    def __init__(self, model, view):
        """Initialize the controller and connect the view/model methods.

        Parameters
        ----------
        model: Model
            The model of the Fenix Committer.
        view: View
            The view of the Fenix Committer.

        """
        self._model = model
        self._view = view

        self._connectModel()
        self._connectView()

        self.valid = True

        self._model.user = PipelineHelper.getCurrentUser()
        if self._model.user is None:
            DisplayMayaDialog.displayMayaDialog(
                'Not logged',
                'Please login in Fenix and try again.',
                severity=DisplayMayaDialog.SeverityTypes.CRITICAL
            )
            self.valid = False

    def _connectModel(self):
        """Connect the model methods to the controller internal methods."""
        pass

    def _connectView(self):
        """Connect the view methods to the controller internal methods."""
        self._view.select_asset = self.select_asset
        self._view.add_assets = self.add_assets
        self._view.remove_assets = self.remove_assets
        self._view.update_assets = self.update_assets
        self._view.commit = self.commit

    def select_asset(self, asset_names):
        """Update view data with model data from selected asset.

        Only the last selected asset is used for view data update.
        Parameters
        ----------
        asset_names: list of str
            The name of the assets to use for view data update.

        """
        self._view.reset_ui()
        if not asset_names:
            return

        if asset_names[-1] not in self._model.assets:
            raise KeyError(
                'Asset {} not found in asset list'.format(asset_names[-1])
            )
        asset = self._model.assets[asset_names[-1]]

        self._view.update_ui(
            asset.commit_on_farm,
            asset.commit_to_alembic_anim,
            asset.can_commit_to_fx_cache,
            asset.commit_to_fx_cache,
            asset.generate_alembic_from_geos,
            asset.use_local_space_for_alembic,
            asset.commit_text
        )

    def add_assets(self, assets=None):
        """Add assets to model and store their data.

        Parameters
        ----------
        assets: list of MayaAsset
            The assets to add to the model.

        """
        if assets is None:
            assets = PipelineHelper.getSelectedMayaAssets()

        assets = [
            asset
            for asset in assets
            if (
                asset.get_maya_commit().component.stage ==
                zefir.STAGES.FX_SIMULATION
            )
        ]

        for asset in assets:
            name = asset.name
            if name in self._model.assets:
                continue

            asset_data = AssetData()
            asset_data.asset = asset

            effects_node = str(asset.get_effects_node())
            if (
                mc.objExists(effects_node) and
                mc.listRelatives(effects_node) is not None
            ):
                asset_data.commit_to_fx_cache = True
            else:
                asset_data.can_commit_to_fx_cache = False
                asset_data.commit_to_fx_cache = False
                asset_data.generate_alembic_from_geos = False
                asset_data.use_local_space_for_alembic = False
                asset_data.commit_to_alembic_anim = True

            self._model.assets[name] = asset_data

        self._view.build_items(sorted(self._model.assets.keys()))

    def remove_assets(self, asset_names):
        """Remove assets from the model.

        Parameters
        ----------
        asset_names: list of str
            The name of the assets to remove.

        """
        for asset_name in asset_names:
            if asset_name not in self._model.assets:
                continue
            del self._model.assets[asset_name]
        self._view.build_items(sorted(self._model.assets.keys()))

    def update_assets(
        self, asset_names,
        commit_on_farm=None,
        commit_to_alembic_anim=None,
        can_commit_to_fx_cache=None,
        commit_to_fx_cache=None,
        generate_alembic_from_geos=None,
        use_local_space_for_alembic=None,
        commit_text=None
    ):
        """Update assets data in model.

        All keyword parameters are initialize to None. When set to None the
        corresponding original data value is left unchanged.
        Parameters
        ----------
        asset_names: list of str
            The list of asset for which to update the data.
        commit_on_farm: bool or None
            Data parameter to update.
        commit_to_alembic_anim: bool or None
            Data parameter to update.
        can_commit_to_fx_cache: bool or None
            Data parameter to update.
        commit_to_fx_cache: bool or None
            Data parameter to update.
        generate_alembic_from_geos: bool or None
            Data parameter to update.
        use_local_space_for_alembic: bool or None
            Data parameter to update.
        commit_text: str or None
            Data parameter to update.

        """
        for asset_name in asset_names:
            if asset_name not in self._model.assets:
                continue
            if commit_on_farm is not None:
                self._model.assets[asset_name].commit_on_farm = commit_on_farm
            if commit_to_alembic_anim is not None:
                self._model.assets[asset_name].commit_to_alembic_anim = \
                    commit_to_alembic_anim
            if can_commit_to_fx_cache is not None:
                self._model.assets[asset_name].can_commit_to_fx_cache = \
                    can_commit_to_fx_cache
            if commit_to_fx_cache is not None:
                self._model.assets[asset_name].commit_to_fx_cache = \
                    commit_to_fx_cache
            if generate_alembic_from_geos is not None:
                self._model.assets[asset_name].generate_alembic_from_geos = \
                    generate_alembic_from_geos
            if use_local_space_for_alembic is not None:
                self._model.assets[asset_name].use_local_space_for_alembic = \
                    use_local_space_for_alembic
            if commit_text is not None:
                self._model.assets[asset_name].commit_text = commit_text

    def get_alembic_from_geo_meshes(self, asset):
        """Return a list of meshes contained in given asset geo group.

        Parameters
        ----------
        asset: MayaAsset
            The asset containing the meshes.

        Returns
        -------
        list of str or None:
            The full path to the meshes contained in the geo group of the asset,
            returns None if no valid meshes where found.

        """
        # Get the effects group contained in the asset
        effects_node = PipelineHelper.getAssetEffectsNode(asset)

        nodes = mc.listRelatives(effects_node, ad=True, f=True)
        if not nodes:
            DisplayMayaDialog.displayMayaDialog(
                title='No shape found',
                message=(
                    "Couldn't find any shape to cache as an Alembic file.\n"
                    "Alembic generation skipped."
                ),
                severity=DisplayMayaDialog.SeverityTypes.WARNING
            )
            return
        # Check for shape deformed and warn the user in case some are found
        if nodes:
            shapes = [
                node
                for node in nodes
                if mc.nodeType(node) == 'mesh' and node.endswith('Deformed')
            ]

        if shapes:
            DisplayMayaDialog.displayMayaDialog(
                title='Shape deformed found',
                message=(
                    "Some shape deformed where found in the effects group, "
                    "clean your geometry and try again."
                ),
                severity=DisplayMayaDialog.SeverityTypes.CRITICAL
            )
            return

        # Find all the meshes under the effects group
        geo_nodes = [
            node
            for node in nodes
            if (
                mc.nodeType(node) == 'mesh' and
                'Orig' not in node and
                mc.getAttr("{0}.intermediateObject".format(node)) is False
            )
        ]

        # Skip the alembic generation if no meshes were found
        if len(geo_nodes) == 0:
            DisplayMayaDialog.displayMayaDialog(
                title='No shape found',
                message=(
                    "Couldn't find any shape to cache as an Alembic file.\n"
                    "Alembic generation skipped."
                ),
                severity=DisplayMayaDialog.SeverityTypes.WARNING
            )
            return
        return geo_nodes

    def get_render_attributes(self, nodes):
        """Return render attributes for given nodes.

        The message type attributes are filtered out as they don't have a value.
        Parameters
        ----------
        nodes: list of str
            The nodes used to extract the render attributes.

        Returns
        -------
        list of dict
            A dict with attribute names as keys and attribute values as values
            for each passed node, can be empty if no attributes were found.

        """
        render_attributes = []
        for node in nodes:
            # Select only the attributes from arnold that aren't plugged into
            # the message attribute
            attribute_list = mc.listAttr(node, fromPlugin=True)
            if attribute_list is None:
                attribute_list = []

            # Get attribute names
            attrs = [
                attribute
                for attribute in attribute_list
                if (
                    'arnold' in mc.attributeQuery(
                        attribute, node=node, categories=True
                    ) and
                    'message' not in mc.getAttr(
                        "{0}.{1}".format(node, attribute), typ=True
                    )
                )
            ]

            # Get attribute values
            values = [
                mc.getAttr("{0}.{1}".format(node, attr)) for attr in attrs
            ]
            # Fill the render attribute var with a dict of
            # attribute name and value pairs
            render_attributes.append(dict(zip(attrs, values)))
        return render_attributes

    def get_shaders(self, nodes):
        """Return a list of shaders assigned to given nodes.

        Parameters
        ----------
        nodes: list of str
            The nodes used to query shaders.

        Returns
        -------
        list of list of str
            A shader list (or an empty list if no shader were found) for each
            node.

        """
        shaders = []
        # Fill the assigned shader list
        for node in nodes:
            shader = mc.listConnections("{0}.instObjGroups[0]".format(node))
            if shader is not None:
                shaders.append(shader)
            else:
                shaders.append([])
        return shaders

    def get_parents(self, nodes):
        """Return a list of parents for given nodes.

        Parameters
        ----------
        nodes: list of str
            The nodes used to get parents.

        Returns
        -------
        list of str
            A full path to parent node for each node or None if no parent can
            be found.

        """
        parents = []
        # Fill the parent info list
        for node in nodes:
            if mc.nodeType(node) != 'transform':
                node = mc.listRelatives(node, parent=True, fullPath=True)[0]
            parent = mc.listRelatives(node, parent=True, fullPath=True)
            parents.append(parent[0] if parent else None)
        return parents

    def get_visibility_curves(self, nodes):
        """Return a list of curves connected to given nodes visbility attribute.

        Parameters
        ----------
        nodes: list of str
            The nodes used to get visibility curves.

        Returns
        -------
        list of list of str
            A list of animation curves for each node or None if no curves can
            be found.

        """
        curves = []
        for node in nodes:
            if mc.nodeType(node) != 'transform':
                node = mc.listRelatives(node, parent=True, fullPath=True)[0]
            # Check if a anim curve is connected to the visibility attribute
            if mc.listConnections("{0}.visibility".format(node)):
                animCurves = filter(
                    lambda connection: 'animCurve' in mc.nodeType(connection),
                    mc.listConnections("{0}.visibility".format(node))
                )
                # Unplug the anim curve (to avoid it being deleted when the
                # object will be) and store a ref to it in the anim curve list
                if animCurves:
                    mc.disconnectAttr(
                        "{0}.output".format(animCurves[0]),
                        "{0}.visibility".format(node)
                    )
                    curves.append(animCurves[0])
                else:
                    curves.append(None)
            else:
                curves.append(None)
        return curves

    def get_visibility_values(self, nodes):
        """Return a list of visbility values for given nodes.

        Parameters
        ----------
        nodes: list of str
            The nodes used to get visibility values.

        Returns
        -------
        list of bool
            The visibility value for each node.

        """
        values = []
        for node in nodes:
            if mc.nodeType(node) != 'transform':
                node = mc.listRelatives(node, parent=True, fullPath=True)[0]
            # Store the visibility attr state in the list
            values.append(mc.getAttr("{0}.visibility".format(node)))
        return values

    def get_alembic_effect_attributes(self, geo_nodes):
        """Return a dict containing data about give nodes.

        Parameters
        ----------
        geo_nodes: list of str
            The nodes used to gather data.

        Returns
        -------
        dict:
            The data for given nodes.

        """
        return {
            'render_attrs': self.get_render_attributes(geo_nodes),
            'shaders': self.get_shaders(geo_nodes),
            'parents': self.get_parents(geo_nodes),
            'visibility_curves': self.get_visibility_curves(geo_nodes),
            'visibility_values': self.get_visibility_values(geo_nodes),
        }

    def set_alembic_effect_attributes(self, geo_nodes, attribute_data):
        """Set attribute data on given nodes.

        Parameters
        ----------
        geo_nodes: list of str
            The node on which to set the attributes values.
        attribute_data: dict
            A dictonnary containing attribute values for the nodes.

        """
        data = zip(
            geo_nodes,
            attribute_data['render_attrs'],
            attribute_data['shaders'],
            attribute_data['parents'],
            attribute_data['visibility_curves'],
            attribute_data['visibility_values'],
        )
        for node, render_attr, shader, parent, vis_curve, vis_value in data:
            # Get transform node for parenting and setting visibility
            transform = node
            if mc.nodeType(transform) != 'transform':
                transform = mc.listRelatives(
                    node, parent=True, fullPath=True
                )[0]

            # Set visbility value
            mc.setAttr('{}.visibility'.format(transform), vis_value)
            # Attach visibility curve
            if vis_curve is not None:
                mc.connectAttr(
                    '{}.output'.format(vis_curve),
                    '{}.visibility'.format(transform)
                )

            # Set attribute values
            errors = []
            for attribute, value in render_attr.items():
                if not self.set_attribute(node, attribute, value):
                    errors.append(
                        "Couldn't set the attribute {} on {}".format(
                            attribute, node
                        )
                    )
            if errors:
                DisplayMayaDialog.displayMayaDialog(
                    'Error setting attributes',
                    '\n'.join(errors),
                    severity=DisplayMayaDialog.SeverityTypes.WARNING
                )

            # Set shader
            if len(shader):
                mc.sets(node, e=True, forceElement=shader[0])

            # Parent node (done at the end to avoid naming problems caused by
            # changing hierarchy)
            mc.parent(transform, parent)[0]

    def set_attribute(self, node, attribute, value):
        """Set given attribute value to given value on given node.

        Parameters
        ----------
        node: str
            Name/path to node
        attribute: str
            Name of attribute
        value:
            Value to set attribute to.

        Returns
        -------
        bool
            False if attribute value could not be set, True otherwise.

        """
        name = '{}.{}'.format(node, attribute)
        try:
            attr_type = mc.getAttr(name, typ=True)
            if 'string' in attr_type:
                mc.setAttr(name, value, typ='string')
            elif 'float3' in attr_type:
                mc.setAttr(
                    name, value[0][0], value[0][1], value[0][2], typ='float3'
                )
            else:
                mc.setAttr(name, value)
        except Exception:
            return False
        return True

    def import_alembic(self, path):
        """Import the alembic file at given path in the scene.

        Parameters
        ----------
        path: str
            The path to the alembic file.

        Returns
        -------
        list of str
            The list of long names of imported geometries.

        Raises
        ------
        RuntimeError
            If provided path doesn't exist.

        """
        if not os.path.exists(path):
            raise RuntimeError('Invalid path {}'.format(path))

        # As alembic import command doesn't list importerd geos, use an empty
        # to group to temporarily group under as a way to list nodes
        null_node = mc.group(empty=True)
        mc.AbcImport(path, reparent=null_node)

        nodes = []
        for node in mc.listRelatives(null_node, fullPath=True):
            node = mc.parent(node, world=True)[0]
            nodes.append(mc.ls(node, long=True)[0])

        mc.delete(null_node)

        return nodes

    def export_alembic(self, path, geo_nodes, use_local_space=False):
        """Export an alembic file of geo nodes to given path.

        Parameters
        ----------
        path: str
            The path to the alembic file at.
        geo_nodes: list of str
            The list of nodes to export in the alembic.
        use_local_space: bool
            Whether to use local space when exporting the alembic.

        Raises
        ------
        RuntimeError
            If provided path already exists.

        """
        if os.path.exists(path):
            raise RuntimeError('Given path aleady exist: {}'.format(path))

        export_space = '' if use_local_space else '-worldSpace'
        args = [
            '-uv',
            export_space,
            '-frameRange', str(self._model.frame_in - 1),
            str(self._model.frame_out + 1),
            '-frameRelativeSample', str(self._model.motion_blur_in),
            '-frameRelativeSample', '0',
            '-frameRelativeSample', str(self._model.motion_blur_out),
            '-file', path,
        ]
        for node in geo_nodes:
            if mc.nodeType(node) != 'transform':
                node = mc.listRelatives(node, parent=True, fullPath=True)[0]
            args.extend([
                '-root', node
            ])

        mc.AbcExport(jobArg=[' '.join(args)])

    def remove_alembic_file(self, file_path):
        """Attempt to remove given file from the network.

        Parameters
        ----------
        file_path: str
            The path to the file to remove.

        Returns
        -------
        bool
            Whether the operation was successful.

        """
        try:
            # Try simply removing the file from the network
            os.remove(file_path)
            return True
        except Exception:
            # In case the file is not removable, try to rename it first and
            # remove it after
            try:
                os.rename(file_path, file_path + '.old')
            except Exception:
                DisplayMayaDialog.displayMayaDialog(
                    "Can't overwrite alembic file.",
                    (
                        "Windows is preventing the overwrite of the "
                        "alembic file. Try deleting it by hand "
                        "and try again.",
                    ),
                    severity=DisplayMayaDialog.SeverityTypes.CRITICAL
                )
                return False

            try:
                os.remove(file_path + '.old')
            except Exception:
                pass
            return True

    def update_geometries(self, geo_nodes, attribute_data, alembic_path):
        """Remove geos, re-import them from alembic file and apply attributes.

        Parameters
        ----------
        geo_nodes: list of str
            Nodes to remove
        attribute_data: dict
            Attributes to apply to re-imported nodes.
        alembic_path: str
            Path to alembic file containing geos to import.

        """
        mc.delete([
            mc.listRelatives(node, parent=True)[0]
            for node in geo_nodes
        ])
        geo_nodes = self.import_alembic(alembic_path)
        self.set_alembic_effect_attributes(geo_nodes, attribute_data)

    def clean_geometries(self, geo_nodes):
        """Clean given geo nodes geometry.

        In an effort to clean the given geometry, a new geo is created, it's
        in mesh attribute is attached to the base geo and blendshaped to it.
        The base geo is renamed and unparented while the new geo is named after
        the base one and parented under the base geo parent.

        Parameters
        ----------
        geo_nodes: list of str
            The nodes to clean.

        """
        for node in geo_nodes:
            if mc.nodeType(node) != 'mesh':
                node = mc.listRelatives(node, shapes=True, fullPath=True)[0]

            # Do the in mesh out mesh connection and the blendshape between
            # a cube and the original geometry
            cube = mc.polyCube()[0]
            cubeShape = mc.listRelatives(cube, s=True)[0]
            mc.connectAttr(
                "{0}.outMesh".format(node),
                "{0}.inMesh".format(cubeShape),
                f=True
            )
            mc.blendShape(node, cubeShape, w=(0, 1), o='world')

            # Rename the old object and all of it's shapes
            # This is a workaround to rename the shapeDeformed as well
            transform = mc.listRelatives(node, parent=True, fullPath=True)[0]
            renamed = mc.rename(
                transform,
                "{0}_OM".format(transform.split('|')[-1]),
                ignoreShape=True
            )
            for shape in mc.listRelatives(renamed, s=True, f=True):
                mc.rename(shape, "{0}_OM".format(shape.split('|')[-1]))

            # Rename the cube and it's shapes to orignial geo name
            new_node = mc.rename(
                cube,
                transform.split('|')[-1],
                ignoreShape=True
            )
            mc.rename(
                mc.listRelatives(new_node, s=True)[0],
                node.split('|')[-1]
            )

            # Unparent the old object and parent the new one
            parent = mc.listRelatives(renamed, parent=True, fullPath=True)
            if parent is not None:
                mc.parent(new_node, parent[0])
                mc.parent(renamed, world=True)

    def cache_geometries(self, geo_nodes):
        """Generate and attach a geocache to copies of given geo nodes.

        Parameters
        ----------
        geo_nodes: list of str
            The nodes to clean.

        """
        # Create the geocache file command
        cache_cmd = [
            'string $switch = "";',
            'string $cacheFiles[] = `cacheFile',
            '-fileName "tmpCache"',
            '-directory', '"{}"'.format(Settings.TEMP_DIR),
            '-startTime', str(self._model.frame_in - 1),
            '-endTime', str(self._model.frame_out + 1),
            '-worldSpace',
            '-singleCache',
        ]
        switch_cmd = []
        for node in geo_nodes:
            if mc.nodeType(node) != 'mesh':
                node = mc.listRelatives(node, shapes=True, fullPath=True)[0]

            # Add the newly created geo to the geocache command
            cache_cmd.extend(['-points', node])
            # Create the code to attach the geocache to the created geo
            switch_cmd.extend([
                '$switch = createHistorySwitch("{}", false);'.format(node),
                'cacheFile',
                '-attachFile',
                '-fileName $cacheFiles[0]'
                '-directory', '"{}"'.format(Settings.TEMP_DIR),
                '-channelName', '"{}"'.format(node),
                '-inAttr ($switch+".inp[0]");',
                'setAttr ($switch+".playFromCache") true;'
            ])

        # Concatenate both commands
        cache_cmd = ' '.join(cache_cmd) + "`;" + ' '.join(switch_cmd)

        # Clean the geometries before making the cache
        self.clean_geometries(geo_nodes)
        # Make a geocache of the created geometries and attach it
        mel.eval(cache_cmd)

    def generate_effect_alembic(self, data):
        """Convert geometries of given asset to alembic file.

        Parameters
        ----------
        data: AssetData
            AssetData for asset containing geometries.

        Returns
        -------
        bool
            Whether the operation was successful.

        """
        try:
            # Extract the seq and shot number for the shot object
            seq, shot = PipelineHelper.getCurrentSeqShot()
        except NotSetError:
            DisplayMayaDialog.displayMayaDialog(
                'Shot not set',
                'Please set you current shot in Fenix and try again.',
                severity=DisplayMayaDialog.SeverityTypes.CRITICAL
            )
            return

        # Get the frame in and frame out for the current shot from fenix
        fr_in, fr_out = PipelineHelper.getShotFrameRange(seq, shot)
        self._model.frame_in, self._model.frame_out = fr_in, fr_out

        # Get the motion blur steps from fenix
        mo_blur_in, mo_blur_out = get_setting_value(
            MOTION_BLUR_SAMPLES_SETTING,
            data.asset.get_maya_commit()
        )
        self._model.motion_blur_in = mo_blur_in
        self._model.motion_blur_out = mo_blur_out

        # Get the name of the asset and build
        # the name of the alembic file from it
        asset_name = data.asset.name
        file_name = asset_name[:asset_name.find(':')]

        # Get nodes in the effects group
        geo_nodes = self.get_alembic_from_geo_meshes(data.asset)
        # Skip the alembic generation if no meshes were found
        if geo_nodes is None:
            DisplayMayaDialog.displayMayaDialog(
                title='No shape found',
                message=(
                    "Couldn't find any shape to cache as an Alembic file.\n"
                    "Alembic generation skipped."
                ),
                severity=DisplayMayaDialog.SeverityTypes.WARNING
            )
            return True

        # Get attribute data for nodes
        attribute_data = self.get_alembic_effect_attributes(geo_nodes)

        # Get the export folder path and create it if necessary
        cache_folder = PipelineHelper.getCachePath(seq, shot)
        out_folder = os.path.join(cache_folder, 'alembic', file_name)
        if not os.path.exists(out_folder):
            os.makedirs(out_folder)

        # Build the finale path name
        final_path = os.path.join(out_folder, "{}.abc".format(file_name))

        # Take action if the alembic file already exists
        if os.path.exists(final_path):
            answer = self._view.dialog(
                "Alembic already exists.",
                (
                    "An alembic file for this asset already exists.\n"
                    "What do you want to do ?"
                ),
                [("Re-use", True), ("Overwrite", True), ("Cancel", False)]
            )
            if answer == 'Re-use':
                # Remove existing geos, import alembic file and apply attributes
                self.update_geometries(geo_nodes, attribute_data, final_path)
                return True
            elif answer == 'Overwrite':
                # Remove alembic file and continue
                self.remove_alembic_file(final_path)
            else:
                return False

        # Clean geos and export to alembic
        self.cache_geometries(geo_nodes)
        self.export_alembic(
            final_path, geo_nodes, data.use_local_space_for_alembic
        )
        # Remove existing geos, import alembic file and apply attributes
        self.update_geometries(geo_nodes, attribute_data, final_path)
        return True

    def commit_sanity_check(self, data):
        """Check validity of given asset data for commit.

        Parameters
        ----------
        data: AssetData
            AssetData to check for commit validity.

        Returns
        -------
        bool
            Whether commit data is valid.

        """
        try:
            effects_node = PipelineHelper.getAssetEffectsNode(data.asset)
        except ValueError:
            mc.warning(' '.join([
                'No effects group.',
                "Can't find the effects group for the asset",
                data.asset.name
            ]))
            return False

        # Check for duplicates in nodes parented under effects node as
        # those would prevent a proper commit
        relatives = mc.listRelatives(effects_node, ad=True)
        if relatives is not None and Counter(relatives).most_common()[0][1] > 1:
            mc.warning(' '.join([
                'Commit failed.',
                "Two objects or more share the same name!"
                "Rename and retry."
            ]))
            return False

        # Find fx cache and animation alembic components assigned to the
        # current asset
        maya_commit = data.asset.get_maya_commit()
        fx_simulation_component = maya_commit.component

        context = PipelineHelper.getContext()
        fx_cache_component = context.find_shot_instance_component(
            shot_instance=fx_simulation_component.shot_instance,
            stage=zefir.STAGES.FX_CACHE
        )

        animation_cache_component = context.find_shot_instance_component(
            shot_instance=fx_simulation_component.shot_instance,
            stage=zefir.STAGES.ANIMATION_ALEMBIC
        )
        # Stop if the current asset has neither a fx cache nor a animation
        # alembic component
        if fx_cache_component is None and animation_cache_component is None:
            return False

        return True

    def commit(self):
        """Commit loaded assets."""
        successful = []
        failed = []
        for name, item in self._model.assets.items():
            # Check the asset data for error before committing
            if not self.commit_sanity_check(item):
                mc.warning('Cannot commit {}, skipping.'.format(name))
                continue

            # Clean geo if necessary before committing
            if item.generate_alembic_from_geos:
                if not self.generate_effect_alembic(item):
                    mc.warning(
                        'Cannot generate alembic for {}, skipping.'.format(name)
                    )
                    continue

            if item.commit_on_farm:
                self.remote_commit(item)
            else:
                success = self.commit_locally(item)
                (successful if success else failed).append(name)
        if successful or failed:
            msg = ''
            if successful:
                msg += ' '.join([
                    ','.join(successful),
                    'have been committed successfully.'
                ])
            if failed:
                msg += ' '.join([
                    ','.join(failed),
                    'haven\'t been committed.'
                ])
            if msg:
                DisplayMayaDialog.displayMayaDialog(
                    'Commit done', msg,
                    severity=DisplayMayaDialog.SeverityTypes.INFORMATION
                )

    def commit_locally(self, data):
        """Commit given asset data locally.

        Parameters
        ----------
        data: AssetData
            Data for the asset to commit locally.

        Returns
        -------
        bool
            Whether commit was successfull.

        """
        return self.commit_asset(
            data.asset.name,
            self._model.user.code,
            data.commit_text,
            data.commit_to_fx_cache,
            data.commit_to_alembic_anim
        )

    def remote_commit(self, data):
        """Commit given asset data on the farm.

        Parameters
        ----------
        data: AssetData
            Data for the asset to commit on the farm.

        """
        scene_name = mc.file(q=True, sn=True)
        new_scene_name = mc.file(
            "{0}_farm.ma".format(os.path.splitext(scene_name)[0]),
            exportAll=True,
            type="mayaAscii"
        )

        cmd = (
            "from nwave.effects.tools.nwFenixCommitter.Controller "
            "import Controller\nController.commit_asset"
            "(\"{0}\", \"{1}\", \"{2}\", {3}, {4})"
        )
        cmd = cmd.format(
            data.asset.name,
            self._model.user.code,
            data.commit_text,
            data.commit_to_fx_cache,
            data.commit_to_alembic_anim
        )

        batch = Batch(
            PipelineHelper.getContext(),
            Settings.MUSTER_FOLDER,
            "commit_{0}".format(data.asset.name.replace(':', '_')),
            maya_scene_file=new_scene_name
        )
        batch.add_job(cmd)
        batch.launch()

        DisplayMayaDialog.displayMayaDialog(
            'Commit on Farm',
            (
                "The job to commit the asset {0} has created on the Farm."
            ).format(data.asset.name),
            severity=DisplayMayaDialog.SeverityTypes.INFORMATION
        )

    @staticmethod
    def commit_asset(
        asset_name, user_code, commit_text, commit_to_fx_cache,
        commit_to_alembic_anim
    ):
        """Commit the given asset.

        Parameters
        ----------
        asset_name: str
            The name of the asset to commit.
        commit_text: str
            The comment given to the commit.
        commit_to_fx_cache: bool
            Whether to commit to fx cache stage.
        commit_to_alembic_anim: bool
            Whether to commit to alembic anim stage.

        Returns
        -------
        bool
            Whether the commit was successful.

        """
        mc.select(asset_name, r=True)

        maya_asset = PipelineHelper.getSelectedMayaAssets()[0]

        # Find fx cache and animation alembic components assigned to the
        # current asset
        maya_commit = maya_asset.get_maya_commit()
        fx_simulation_component = maya_commit.component

        context = PipelineHelper.getContext()
        fx_cache_component = context.find_shot_instance_component(
            shot_instance=fx_simulation_component.shot_instance,
            stage=zefir.STAGES.FX_CACHE
        )
        if fx_cache_component is None:
            mc.warning("No FX cache asset assigned to this shot!")

        animation_cache_component = context.find_shot_instance_component(
            shot_instance=fx_simulation_component.shot_instance,
            stage=zefir.STAGES.ANIMATION_ALEMBIC
        )

        if animation_cache_component is None:
            mc.warning(
                "No alembic animation cache asset assigned to this shot!"
            )

        if commit_to_fx_cache and fx_cache_component is not None:
            if (
                fx_cache_component.is_locked and
                fx_cache_component.locking_user.code is not user_code
            ):
                mc.warning(' '.join([
                    'Locked asset',
                    'Asset is already locked by',
                    fx_cache_component.locking_user.common_name,
                    'cannot commit.'
                ]))
                return False

            fx_cache_commit = \
                fx_cache_component.get_latest_or_new_commit_revising()
            fx_cache_maya_commit = MayaCommit(fx_cache_commit)

            if fx_cache_maya_commit.exists:
                fx_cache_maya_commit = \
                    fx_cache_maya_commit.create_new_revision()
            fx_cache_maya_commit.message = commit_text
            fx_cache_maya_commit.commit(
                options={
                    COMMIT_WITHOUT_SIMULATION_OPTION: True,
                    CREATE_FROM_SOURCE_ASSET_OPTION: True,
                    EXPORT_ALL_NWOVERRIDE_SETS_OPTION: True
                }
            )

            try:
                fx_cache_component.lock()
            except (NoAuthenticatedUserError, AlreadyLockedError) as error:
                mc.warning(
                    'Could not lock the asset: {0}'.format(error.message)
                )

        if (
            commit_to_alembic_anim and
            animation_cache_component is not None
        ):
            alembic_animation_commit = \
                animation_cache_component.get_latest_or_new_commit_revising()
            abc_cache_maya_commit = MayaCommit(alembic_animation_commit)

            if abc_cache_maya_commit.exists:
                abc_cache_maya_commit = \
                    abc_cache_maya_commit.create_new_revision()
            abc_cache_maya_commit.message = commit_text
            abc_cache_maya_commit.commit(
                options={
                    COMMIT_WITH_RELATIVE_ANIMATION_OPTION: False,
                    KEEP_INVISIBLE_OBJECTS: True,
                    COMMIT_PROXY_CACHE: False
                }
            )

            try:
                animation_cache_component.lock()
            except (NoAuthenticatedUserError, AlreadyLockedError) as error:
                mc.warning(
                    'Could not lock the asset: {0}'.format(error.message)
                )

        print ' '.join([
            'Commit successful',
            'The asset',
            asset_name,
            'has been sucessfully committed.'
        ])
        return True
