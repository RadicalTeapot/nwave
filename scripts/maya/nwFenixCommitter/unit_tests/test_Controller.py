# -*- coding: utf-8 -*-
"""Unit tests for the Fenix Committer."""

from nwave.effects.tools.nwFXTDTools.PipelineHelper import PipelineHelper

import zefir
from zefir.settings import get_setting_value
from fenix4maya.settings import MOTION_BLUR_SAMPLES_SETTING

import pytest
import maya.cmds as mc
import maya.mel

import os

from nwave.effects.tools.nwFenixCommitter.Settings import Settings


class TestFenixCommitter(object):

    def test_init(self, mvc):
        """Test tool initialization."""
        model, _, controller = mvc

        assert model.assets == {}
        assert model.user == PipelineHelper.getCurrentUser()
        assert controller.valid

    def test_add_remove_assets(self, mvc, scene):
        """Test adding and removing assets."""
        model, _, controller = mvc

        controller.add_assets([])
        # Test add empty
        assert not len(model.assets)

        controller.add_assets(scene.assets)
        # Test add assets
        assert len(model.assets) == len(scene.assets)

        # Test add non fx sim asset
        camera = PipelineHelper.getAsset(
            'camera',
            zefir.STAGES.CAMERA_ANIMATION_DATA,
            '635', '0170'
        )
        controller.add_assets([camera])
        assert len(model.assets) == len(scene.assets)

        controller.remove_assets([])
        # Test removing no assets
        assert len(model.assets) == len(scene.assets)

        controller.remove_assets([asset.name for asset in scene.assets[:1]])
        # Test removing one asset
        assert len(model.assets) == len(scene.assets[1:])

        controller.remove_assets([asset.name for asset in scene.assets[1:]])
        # Test removing all assets
        assert len(model.assets) == 0

        controller.remove_assets(scene.assets)
        # Test removing non loaded assets
        assert len(model.assets) == 0

    def test_udpate_asset(self, mvc, scene):
        """Test updating asset data."""
        model, _, controller = mvc

        controller.add_assets(scene.assets)
        name = scene.assets[0].name
        asset = model.assets[name]

        # Test wrong asset name failing silently
        controller.update_assets(['test'], commit_on_farm=False)

        controller.update_assets([name], commit_on_farm=False)
        assert not asset.commit_on_farm
        controller.update_assets([name], commit_on_farm=True)
        assert asset.commit_on_farm

        controller.update_assets([name], commit_to_alembic_anim=False)
        assert not asset.commit_to_alembic_anim
        controller.update_assets([name], commit_to_alembic_anim=True)
        assert asset.commit_to_alembic_anim

        controller.update_assets([name], can_commit_to_fx_cache=False)
        assert not asset.can_commit_to_fx_cache
        controller.update_assets([name], can_commit_to_fx_cache=True)
        assert asset.can_commit_to_fx_cache

        controller.update_assets([name], commit_to_fx_cache=False)
        assert not asset.commit_to_fx_cache
        controller.update_assets([name], commit_to_fx_cache=True)
        assert asset.commit_to_fx_cache

        controller.update_assets([name], generate_alembic_from_geos=False)
        assert not asset.generate_alembic_from_geos
        controller.update_assets([name], generate_alembic_from_geos=True)
        assert asset.generate_alembic_from_geos

        controller.update_assets([name], use_local_space_for_alembic=False)
        assert not asset.use_local_space_for_alembic
        controller.update_assets([name], use_local_space_for_alembic=True)
        assert asset.use_local_space_for_alembic

        commit_text = 'test'
        controller.update_assets([name], commit_text=commit_text)
        assert asset.commit_text == commit_text
        commit_text = ''
        controller.update_assets([name], commit_text=commit_text)
        assert asset.commit_text == commit_text

        # Test setting all
        controller.update_assets(
            [scene_asset.name for scene_asset in scene.assets],
            can_commit_to_fx_cache=True
        )
        assert all(
            asset.can_commit_to_fx_cache
            for asset in model.assets.values()
        )
        controller.update_assets(
            [scene_asset.name for scene_asset in scene.assets],
            can_commit_to_fx_cache=False
        )
        assert all(
            not asset.can_commit_to_fx_cache
            for asset in model.assets.values()
        )

    def test_get_alembic_effect_meshes(self, mvc, scene):
        """Test getting meshes in effects group."""
        _, _, controller = mvc

        # Test add non fx sim asset
        camera = PipelineHelper.getAsset(
            'camera',
            zefir.STAGES.CAMERA_ANIMATION_DATA,
            '635', '0170'
        )
        with pytest.raises(ValueError):
            controller.get_alembic_from_geo_meshes(camera)

        # Test error when no effects node
        scene.assets[0].import_from_reference()
        effects_node = scene.assets[0].get_effects_node()
        mc.delete(effects_node.longName())
        with pytest.raises(ValueError):
            controller.get_alembic_from_geo_meshes(scene.assets[0])

        # Test reporting of shape deform
        scene.assets[1].import_from_reference()
        box = mc.polyCube()[0]
        mc.rename(mc.listRelatives(box, shapes=True)[0], 'boxShapeDeformed')
        effects_node = scene.assets[1].get_effects_node()
        mc.parent(box, str(effects_node))
        assert controller.get_alembic_from_geo_meshes(scene.assets[1]) is None

        # Test no geo nodes
        scene.assets[2].import_from_reference()
        assert controller.get_alembic_from_geo_meshes(scene.assets[2]) is None

        # Test geo nodes
        effects_node = scene.assets[2].get_effects_node()
        nodes = [mc.polyCube()[0], mc.polySphere()[0]]
        mc.parent(nodes, str(effects_node))
        assert controller.get_alembic_from_geo_meshes(scene.assets[2]) == [
            mc.listRelatives(node, shapes=True, fullPath=True)[0]
            for node in nodes
        ]

    def test_get_alembic_effect_attributes(self, mvc):
        """Test getting mesh render attributes."""
        _, _, controller = mvc

        transform = mc.createNode('transform')
        box = mc.polyCube()[0]
        box = mc.parent(box, transform)[0]
        shape = mc.listRelatives(box, shapes=True)[0]

        # Test return type
        attributes = controller.get_render_attributes([transform])[0]
        assert isinstance(attributes, dict)
        # Test no render attributes
        assert attributes.keys() == []
        assert attributes.values() == []

        attributes = controller.get_render_attributes([shape])[0].keys()
        # Test arnold attributes
        assert all(
            'arnold' in mc.attributeQuery(
                attribute, node=shape, categories=True
            )
            for attribute in attributes
        )
        # Test no message type attributes
        assert not any(
            'message' in mc.getAttr('{}.{}'.format(shape, attribute), typ=True)
            for attribute in attributes
        )

        # Test no shader
        shaders = controller.get_shaders([transform])[0]
        assert shaders == []

        # Test shader
        shaders = controller.get_shaders([shape])[0]
        assert shaders == ['initialShadingGroup']

        # Test no parent
        parents = controller.get_parents([transform])[0]
        assert parents is None

        # Test parent with mesh
        parents = controller.get_parents([shape])[0]
        assert transform in parents

        # Test parent with transform
        parents = controller.get_parents([box])[0]
        assert transform in parents

        # Test visibility on
        mc.setAttr('{}.visibility'.format(box), 1)
        value = controller.get_visibility_values([shape])[0]
        assert value

        # Test visibility off
        mc.setAttr('{}.visibility'.format(box), 0)
        value = controller.get_visibility_values([shape])[0]
        assert not value

        # Test no anim curve
        curves = controller.get_visibility_curves([shape])[0]
        assert curves is None

        # Create a anim curve
        mc.setKeyframe(box, at='visibility', v=1)
        curves = controller.get_visibility_curves([shape])[0]
        assert curves

    def test_export_alembic(self, mvc, tmpdir, mocker):
        """Test exporting geometries to alembic."""
        model, _, controller = mvc

        model.frame_in = 1
        model.frame_out = 3
        model.motion_blur_in = -.25
        model.motion_blur_out = .25

        mocker.spy(mc, 'AbcExport')

        path = tmpdir.join('cube.abc')
        cube = mc.polyCube()[0]
        controller.export_alembic(str(path), [cube])

        # Test function call
        assert mc.AbcExport.called
        # Test call keyword arguments
        args = mc.AbcExport.call_args[1]
        job = args['jobArg'][0]
        assert '-uv' in job
        frame_range = '-frameRange {} {}'.format(
            model.frame_in - 1, model.frame_out + 1
        )
        assert frame_range in job
        assert '-frameRelativeSample {}'.format(model.motion_blur_in) in job
        assert '-frameRelativeSample {}'.format(model.motion_blur_out) in job
        assert '-file {}'.format(path) in job
        assert '-root {}'.format(cube) in job

    def test_import_alembic(self, mvc, tmpdir, mocker):
        """Test importing geometries from alembic."""
        model, _, controller = mvc

        path = '/home/mathiasc/tmp/invalid.abc'
        if os.path.exists(path):
            os.remove(path)

        # Test wrong path
        with pytest.raises(RuntimeError):
            controller.import_alembic(path)

        path = tmpdir.join('cube.abc')
        cube = mc.polyCube()[0]
        model.frame_in = 1
        model.frame_out = 3
        model.motion_blur_in = -.25
        model.motion_blur_out = .25
        controller.export_alembic(str(path), [cube])

        mocker.spy(mc, 'AbcImport')
        objects = controller.import_alembic(str(path))

        # Test import
        assert mc.AbcImport.called
        args = mc.AbcImport.call_args
        # Test correct path in call arguments
        assert str(path) in args[0]
        # Test reparent flag in call keyword arguments
        assert 'reparent' in args[1]
        # Test retruned geo
        assert len(objects) == 1
        # Test long path
        assert '|' in objects[0]

    def test_set_alembic_effect_attributes(self, mvc):
        """Test settings render attributes on mesh."""
        _, _, controller = mvc

        transform = mc.createNode('transform')
        shader = mc.shadingNode('lambert', asShader=True)
        mc.select(cl=True)
        shading_engine = mc.sets(renderable=True, noSurfaceShader=True)
        mc.connectAttr(
            '{}.outColor'.format(shader),
            '{}.surfaceShader'.format(shading_engine)
        )

        box = mc.polyCube()[0]
        box = mc.parent(box, transform)[0]
        shape = mc.listRelatives(box, shapes=True, fullPath=True)[0]
        mc.setAttr('{}.visibility'.format(box), False)
        mc.sets(shape, e=True, forceElement=shading_engine)
        shape = mc.listRelatives(box, shapes=True)[0]

        attribute_data = controller.get_alembic_effect_attributes([shape])

        # Remove old geometries and create new ones on which to apply attrs
        mc.delete(box)

        box = mc.polyCube()[0]
        shape = mc.listRelatives(box, shapes=True, fullPath=True)[0]
        controller.set_alembic_effect_attributes([shape], attribute_data)
        shape = mc.listRelatives(box, shapes=True, fullPath=True)[0]

        # Test proper parenting
        assert mc.listRelatives(box, p=True, fullPath=True)[0] == \
            attribute_data['parents'][0]
        # Test visibility value
        assert mc.getAttr('{}.visibility'.format(box)) == \
            attribute_data['visibility_values'][0]
        # Test assigning shader
        assert mc.listConnections('{}.instObjGroups[0]'.format(shape)) == \
            attribute_data['shaders'][0]

        mc.delete(box)

        box = mc.polyCube()[0]
        box = mc.parent(box, transform)[0]
        shape = mc.listRelatives(box, shapes=True, fullPath=True)[0]
        # TODO test render attributes settings
        mc.setAttr('{}.aiOpaque'.format(shape), 0)
        mc.setKeyframe(box, at='visibility', v=1)

        attribute_data = controller.get_alembic_effect_attributes([shape])
        # Remove old geometries and create new ones on which to apply attrs
        mc.delete(box)

        box = mc.polyCube()[0]
        shape = mc.listRelatives(box, shapes=True, fullPath=True)[0]
        controller.set_alembic_effect_attributes([shape], attribute_data)
        shape = mc.listRelatives(box, shapes=True, fullPath=True)[0]

        assert attribute_data['visibility_curves'][0] in \
            mc.listConnections('{}.visibility'.format(box))
        assert 'aiOpaque' in attribute_data['render_attrs'][0]
        assert attribute_data['render_attrs'][0]['aiOpaque'] == 0

    def test_clean_geometries(self, mvc):
        """Test cleaning geometries."""
        _, _, controller = mvc

        transform = mc.createNode('transform')
        box = mc.polyCube()[0]
        box = mc.parent(box, transform)[0]
        shape = mc.listRelatives(box, shapes=True, fullPath=True)[0]

        controller.clean_geometries([shape])

        # Test in mesh connection
        # Test blendshape connection
        connection = mc.listConnections('{}.inMesh'.format(shape))
        assert connection
        assert 'blendShape' in mc.nodeType(connection[0])
        # Test renaming
        previous_shape = shape.split('|')[-1]
        assert mc.objExists('{}_OM'.format(box))
        assert mc.objExists('{}_OM'.format(previous_shape))
        # Test parenting under original node parent
        assert mc.listRelatives(
            mc.listRelatives(shape, parent=True, fullPath=True)[0],
            parent=True, fullPath=True
        )[0] == '|{}'.format(transform)

    def test_cache_geometries(self, mvc, mocker):
        """Test geocaching geometries."""
        model, _, controller = mvc

        mocker.spy(controller, 'cache_geometries')
        mocker.spy(maya.mel, 'eval')

        model.frame_in = 10
        model.frame_out = 20

        box = mc.polyCube()[0]
        shape = mc.listRelatives(box, shapes=True, fullPath=True)[0]

        controller.cache_geometries([shape])
        # Test geo cleaned before making cache
        assert controller.cache_geometries.called
        assert controller.cache_geometries.call_args[0] == ([shape],)

        # Test geocache method
        assert maya.mel.eval.called
        args = maya.mel.eval.call_args[0][0]
        assert 'cacheFile' in args
        assert '-directory "{}"'.format(Settings.TEMP_DIR) in args
        assert '-startTime {}'.format(model.frame_in - 1)
        assert '-endTime {}'.format(model.frame_out + 1)
        assert '-worldSpace'
        assert '-singleCache'
        assert '-attachFile'

    def test_generate_effect_alembic(self, mvc, scene, mocker):
        """Test generating clean geometries via an alembic cache."""
        model, view, controller = mvc

        seq, shot = 999, 10
        mocker.patch.object(
            PipelineHelper, 'getCurrentSeqShot',
            mocker.MagicMock(return_value=(seq, shot))
        )

        frame_in, frame_out = 10, 20
        mocker.patch.object(
            PipelineHelper, 'getShotFrameRange',
            mocker.MagicMock(return_value=(frame_in, frame_out))
        )

        existing_alembic_mock = mocker.MagicMock(return_value="Overwrite")
        mocker.patch.object(view, 'dialog', existing_alembic_mock)

        mocker.spy(controller, 'cache_geometries')
        mocker.spy(controller, 'export_alembic')
        mocker.spy(controller, 'update_geometries')
        mocker.spy(controller, 'remove_alembic_file')

        controller.add_assets([scene.assets[0]])
        asset = model.assets[scene.assets[0].name]
        controller.generate_effect_alembic(asset)

        # Test cache command frame range
        assert model.frame_in == frame_in
        assert model.frame_out == frame_out
        mo_blur_in, mo_blur_out = get_setting_value(
            MOTION_BLUR_SAMPLES_SETTING,
            asset.asset.get_maya_commit()
        )
        assert model.motion_blur_in == mo_blur_in
        assert model.motion_blur_out == mo_blur_out
        # test no geo in in effects group
        assert not controller.export_alembic.called

        effects_node = PipelineHelper.getAssetEffectsNode(scene.assets[0])
        box = mc.polyCube()[0]
        box = mc.parent(box, effects_node)
        controller.generate_effect_alembic(asset)

        # test alembic export
        assert controller.export_alembic.called
        args = controller.export_alembic.call_args[0]
        assert len(args) == 3
        path, nodes, local_space = args
        # Test output path
        assert PipelineHelper.getCachePath(seq, shot) in path
        assert 'alembic' in path
        assert asset.asset.name[:asset.asset.name.find(':')] in path
        # Test geo nodes
        assert mc.listRelatives(box, shapes=True, fullPath=True)[0] in nodes
        # Test local space
        assert asset.use_local_space_for_alembic == local_space

        # Test alembic import
        assert controller.update_geometries.called
        # Test cache geo
        assert controller.cache_geometries.called

        # test exisiting alembic options
        existing_alembic_mock.return_value = 'Re-use'
        controller.export_alembic.reset_mock()
        controller.update_geometries.reset_mock()
        controller.cache_geometries.reset_mock()
        assert controller.generate_effect_alembic(asset)
        assert not controller.export_alembic.called
        assert not controller.cache_geometries.called
        assert controller.update_geometries.called

        existing_alembic_mock.return_value = 'Overwrite'
        controller.export_alembic.reset_mock()
        controller.update_geometries.reset_mock()
        controller.remove_alembic_file.reset_mock()
        controller.cache_geometries.reset_mock()
        assert controller.generate_effect_alembic(asset)
        assert controller.export_alembic.called
        assert controller.update_geometries.called
        assert controller.remove_alembic_file.called
        assert controller.cache_geometries.called

        existing_alembic_mock.return_value = 'Cancel'
        controller.export_alembic.reset_mock()
        controller.update_geometries.reset_mock()
        controller.remove_alembic_file.reset_mock()
        controller.cache_geometries.reset_mock()
        assert not controller.generate_effect_alembic(asset)
        assert not controller.export_alembic.called
        assert not controller.update_geometries.called
        assert not controller.remove_alembic_file.called
        assert not controller.cache_geometries.called

        existing_alembic_mock.return_value = ''
        controller.export_alembic.reset_mock()
        controller.update_geometries.reset_mock()
        controller.remove_alembic_file.reset_mock()
        controller.cache_geometries.reset_mock()
        assert not controller.generate_effect_alembic(asset)
        assert not controller.export_alembic.called
        assert not controller.update_geometries.called
        assert not controller.remove_alembic_file.called
        assert not controller.cache_geometries.called

    def test_commit_locally(self, mvc, scene, mocker):
        """Test committing data locally."""
        model, view, controller = mvc

        controller.add_assets([scene.assets[0]])
        asset_name = scene.assets[0].name
        data = model.assets[asset_name]
        data.commit_to_fx_cache = True
        data.generate_alembic_from_geos = True

        seq, shot = 999, 10
        mocker.patch.object(
            PipelineHelper, 'getCurrentSeqShot',
            mocker.MagicMock(return_value=(seq, shot))
        )

        frame_in, frame_out = 10, 20
        mocker.patch.object(
            PipelineHelper, 'getShotFrameRange',
            mocker.MagicMock(return_value=(frame_in, frame_out))
        )

        cache_path = '/home/mathiasc/tmp'
        mocker.patch.object(
            PipelineHelper, 'getCachePath',
            mocker.MagicMock(return_value=cache_path)
        )

        existing_alembic_mock = mocker.MagicMock(return_value="Overwrite")
        mocker.patch.object(view, 'dialog', existing_alembic_mock)

        context_mock = mocker.MagicMock()
        mocker.patch.object(
            PipelineHelper, 'getContext',
            mocker.MagicMock(return_value=context_mock)
        )

        maya_commit_mock = mocker.MagicMock()
        maya_commit_mock.create_new_revision = mocker.MagicMock(
            return_value=maya_commit_mock
        )
        mocker.patch(
            'nwave.effects.tools.nwFenixCommitter.Controller.MayaCommit',
            new=mocker.MagicMock(return_value=maya_commit_mock)
        )

        component_mock = mocker.MagicMock()
        context_mock.find_shot_instance_component.return_value = component_mock
        # Test locked fx cache component
        component_mock.is_locked = True
        component_mock.locking_user = mocker.MagicMock(common_name='nobody')
        assert not controller.commit_locally(data)

        component_mock.is_locked = False
        box = mc.polyCube()[0]
        box = mc.parent(
            box, PipelineHelper.getAssetEffectsNode(scene.assets[0])
        )

        maya_commit_mock.reset_mock()
        assert controller.commit_locally(data)
        #  Test commit to fx_cache and alembic_anim
        assert maya_commit_mock.commit.call_count == 2

    def test_commit_sanity_no_component(self, mvc, scene, mocker):
        """Test data verfication prior to committing."""
        model, _, controller = mvc

        controller.add_assets([scene.assets[0]])
        asset_name = scene.assets[0].name
        data = model.assets[asset_name]

        context_mock = mocker.MagicMock()
        mocker.patch.object(
            PipelineHelper, 'getContext',
            mocker.MagicMock(return_value=context_mock)
        )
        context_mock.find_shot_instance_component.return_value = None
        # Test no fx cache component and no alembic anim cache component
        assert not controller.commit_sanity_check(data)

    def test_commit_sanity_duplicate_name(self, mvc, scene, mocker):
        """Test data verfication prior to committing."""
        model, _, controller = mvc

        controller.add_assets([scene.assets[0]])
        asset_name = scene.assets[0].name
        data = model.assets[asset_name]
        # Test duplicate node names (create 2 boxes with same name in different
        # groups, parent groups under effect node, run method)
        top_parent = mc.group(em=True)
        sub_parent_1 = mc.group(em=True)
        sub_parent_1 = mc.parent(sub_parent_1, top_parent)
        sub_parent_2 = mc.group(em=True)
        sub_parent_2 = mc.parent(sub_parent_2, top_parent)
        box_1 = mc.polyCube()[0]
        box_1 = mc.parent(box_1, sub_parent_1)
        box_1 = mc.rename(box_1, 'pCube1')
        box_2 = mc.polyCube()[0]
        box_2 = mc.parent(box_2, sub_parent_2)
        box_2 = mc.rename(box_2, 'pCube1')
        effects_node = PipelineHelper.getAssetEffectsNode(data.asset)
        mc.parent(top_parent, effects_node)
        assert not controller.commit_sanity_check(data)

    def test_commit_sanity_no_effects_node(self, mvc, scene, mocker):
        """Test data verfication prior to committing."""
        model, _, controller = mvc

        controller.add_assets([scene.assets[0]])
        asset_name = scene.assets[0].name
        data = model.assets[asset_name]
        # Test no effect node (import asset, delete effect node, run method)
        effects_node = PipelineHelper.getAssetEffectsNode(data.asset)
        ref_file = mc.referenceQuery(effects_node, f=True)
        mc.file(ref_file, importReference=True)
        mc.delete(effects_node)
        assert not controller.commit_sanity_check(data)

    def test_commit(self, mvc, scene, mocker):
        """Test committing data."""
        _, _, controller = mvc

        mocker.spy(controller, 'commit_sanity_check')
        farm_mock = mocker.patch.object(controller, 'remote_commit')
        local_mock = mocker.patch.object(controller, 'commit_locally')
        generate_mock = mocker.patch.object(
            controller, 'generate_effect_alembic'
        )

        controller.add_assets([scene.assets[0]])
        controller.update_assets(
            [scene.assets[0].name],
            generate_alembic_from_geos=False,
            commit_on_farm=False
        )
        controller.commit()
        assert controller.commit_sanity_check.called
        assert local_mock.called
        assert not farm_mock.called

        controller.update_assets(
            [scene.assets[0].name],
            commit_on_farm=True
        )
        farm_mock.reset_mock()
        local_mock.reset_mock()
        controller.commit_sanity_check.reset_mock()
        controller.commit()
        assert controller.commit_sanity_check.called
        assert farm_mock.called
        assert not local_mock.called

        controller.update_assets(
            [scene.assets[0].name],
            generate_alembic_from_geos=True,
            commit_on_farm=False
        )
        generate_mock.reset_mock()
        controller.commit()
        assert generate_mock.called

    def test_remote_commit(self, mvc, scene, mocker, tmpdir):
        """Test committing data on the farm."""
        model, _, controller = mvc

        mc.file(rename=os.path.join(str(tmpdir), 'test.ma'))

        controller.add_assets([scene.assets[0]])
        data = model.assets[scene.assets[0].name]

        batch_mock = mocker.MagicMock()
        batch_init = mocker.patch(
            'nwave.effects.tools.nwFenixCommitter.Controller.Batch',
            new=mocker.MagicMock(return_value=batch_mock)
        )
        add_job_mock = mocker.MagicMock()
        launch_mock = mocker.MagicMock()
        batch_mock.configure_mock(
            add_job=add_job_mock,
            launch=launch_mock
        )

        mocker.spy(mc, 'file')
        controller.remote_commit(data)
        # Test new scene save
        assert mc.file.called
        args = mc.file.call_args
        assert 'exportAll' in args[1]
        assert args[1]['exportAll'] is True
        assert 'type' in args[1]
        assert args[1]['type'] == 'mayaAscii'
        assert '_farm.ma' in args[0][0]

        # Test batch args
        assert batch_init.called
        args = batch_init.call_args
        assert Settings.MUSTER_FOLDER in args[0]
        assert 'commit_{}'.format(data.asset.name.replace(':', '_')) in args[0]
        assert add_job_mock.called
        assert launch_mock.called
