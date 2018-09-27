# -*- coding: utf-8 -*-
"""DOCSTRING."""

import pytest

from ZefirReader import Controller
from ZefirReader import zefir

import nwave.effects.houdini.nwHoudiniTools.DisplayHoudiniDialog as \
    DisplayHoudiniDialog


class TestController(object):
    def test_initial_state(self, mocker):
        # Setup
        mocker.spy(Controller, '_connectModel')
        mocker.spy(Controller, '_connectView')
        model = mocker.MagicMock()
        view = mocker.MagicMock()
        con = Controller(model, view)

        # Control
        assert con._model == model
        assert con._view == view
        assert con._connectModel.called
        assert con._connectView.called

    def test_load_data(self, mvc, settings, mocker):
        model, view, controller = mvc
        mocker.spy(model, 'clearShotData')

        view._node.parm('sequenceshotx').set(999)
        view._node.parm('sequenceshoty').set(10)
        assert view.sequence == 999
        assert view.shot == 10

        controller._loadData()
        # Control seq shot assignement
        assert model.sequence == view.sequence
        assert model.shot == view.shot
        # Control node error message
        assert view.severity == 0
        assert view.message == ''
        # Control clearing model data
        # assert clear_shot_data.called
        # clear_shot_data.reset_mock()
        assert model.clearShotData.called
        model.clearShotData.reset_mock()

        shot = model.context.find_shot(code='999_0010')
        shot_data = dict([
            (category, [
                shot_instance
                for shot_instance in shot.shot_instances
                if (
                    shot_instance and
                    shot_instance.asset.asset_type == category
                )
            ]) for category in settings.CATEGORIES.keys()
        ])

        for category in settings.CATEGORIES.keys():
            # Control model data
            assert (
                model.getAssetCount(category) == len(shot_data[category])
            )
            # Control updating view with model
            assert (
                model.getAssetCount(category) ==
                view.getAssetCount(category)
            )

        # Control for error and no refresh when wrong seq/shot
        view._node.parm('sequenceshotx').set(-1)
        view._node.parm('sequenceshoty').set(-1)
        controller._loadData()
        assert view.severity == 2
        assert view.message.startswith('Could not find shot')
        # assert not clear_shot_data.called
        assert not model.clearShotData.called

    def test_add_asset(self, mvc, settings, shot_instance, mocker):
        # Setup
        model, view, controller = mvc
        mocker.spy(model, 'addAsset')

        # Mock setup
        components = shot_instance.components
        asset_components = shot_instance.asset.components

        shot_instance.components = None
        shot_instance.asset.components = None

        # Control model is empty
        assert model.isEmpty()

        # Control exit when no components
        controller._addAsset(zefir.ASSET_TYPES.PROP, shot_instance)
        assert not model.addAsset.called
        controller._addAsset(zefir.ASSET_TYPES.INSTANCES, shot_instance)
        assert not model.addAsset.called

        shot_instance.asset.components = asset_components
        shot_instance.components = components

        # Control exit when no valid components
        components[0].stage = settings.AUTHORIZED_STAGES[
            zefir.ASSET_TYPES.CAMERA
        ][0]

        controller._addAsset(zefir.ASSET_TYPES.PROP, shot_instance)
        assert not model.addAsset.called

        # Control call args
        controller._addAsset(zefir.ASSET_TYPES.CAMERA, shot_instance)
        assert model.addAsset.called
        expected = mocker.call(
            category=zefir.ASSET_TYPES.CAMERA,
            instance_id=shot_instance.id,
            assembly_id=None,
            uv_component_id=None,
            name=shot_instance.string_repr(),
            stages={components[0].id: str(components[0].stage.name)},
            current_stage=components[0].id,
            is_asset_context=False
        )
        assert model.addAsset.call_args == expected
        model.addAsset.reset_mock()

        assert not model.isEmpty()

        # Control call args for instance
        components[0].stage = settings.AUTHORIZED_STAGES[
            zefir.ASSET_TYPES.INSTANCES
        ][0]
        controller._addAsset(zefir.ASSET_TYPES.INSTANCES, shot_instance)
        assert model.addAsset.called
        expected = mocker.call(
            category=zefir.ASSET_TYPES.INSTANCES,
            instance_id=shot_instance.id,
            assembly_id=None,
            uv_component_id=None,
            name=shot_instance.string_repr(),
            stages={components[0].id: str(components[0].stage.name)},
            current_stage=components[0].id,
            is_asset_context=True
        )
        assert model.addAsset.call_args == expected
        model.addAsset.reset_mock()

        # Control call args for set_element
        components[0].stage = settings.AUTHORIZED_STAGES[
            zefir.ASSET_TYPES.SET_ELEMENT
        ][0]
        return_value = mocker.MagicMock()
        return_value.asset_type = zefir.ASSET_TYPES.ASSEMBLY
        return_value.id = 100
        find_asset = mocker.MagicMock(return_value=return_value)
        mocker.patch.object(
            model.context, 'find_asset',
            find_asset
        )
        controller._addAsset(zefir.ASSET_TYPES.SET_ELEMENT, shot_instance)
        assert model.addAsset.called
        assert find_asset.called
        expected = mocker.call(
            category=zefir.ASSET_TYPES.SET_ELEMENT,
            instance_id=shot_instance.id,
            assembly_id=return_value.id,
            uv_component_id=None,
            name=shot_instance.string_repr(),
            stages={components[0].id: str(components[0].stage.name)},
            current_stage=components[0].id,
            is_asset_context=False
        )
        assert model.addAsset.call_args == expected
        model.addAsset.reset_mock()

        # Control call args for character/prop
        components[0].stage = settings.AUTHORIZED_STAGES[
            zefir.ASSET_TYPES.CHARACTER
        ][0]
        shot_instance.asset.components = [asset_components[0]]
        controller._addAsset(zefir.ASSET_TYPES.CHARACTER, shot_instance)
        assert model.addAsset.called
        expected = mocker.call(
            category=zefir.ASSET_TYPES.CHARACTER,
            instance_id=shot_instance.id,
            assembly_id=None,
            uv_component_id=components[1].id,
            name=shot_instance.string_repr(),
            stages={components[0].id: str(components[0].stage.name)},
            current_stage=components[0].id,
            is_asset_context=False
        )
        assert model.addAsset.call_args == expected
        model.addAsset.reset_mock()

        shot_instance.asset.components = asset_components
        shot_instance.components = [components[0]]
        controller._addAsset(zefir.ASSET_TYPES.CHARACTER, shot_instance)
        assert model.addAsset.called
        expected = mocker.call(
            category=zefir.ASSET_TYPES.CHARACTER,
            instance_id=shot_instance.id,
            assembly_id=None,
            uv_component_id=asset_components[1].id,
            name=shot_instance.string_repr(),
            stages={components[0].id: str(components[0].stage.name)},
            current_stage=components[0].id,
            is_asset_context=False
        )
        assert model.addAsset.call_args == expected
        model.addAsset.reset_mock()

    def test_get_asset(self, mvc, settings, shot_instance, mocker):
        # Setup
        model, view, controller = mvc

        mocker.spy(model, 'getAsset')

        # Control regular call
        controller._addAsset(zefir.ASSET_TYPES.CHARACTER, shot_instance)
        controller._getAsset(
            settings.CATEGORIES[zefir.ASSET_TYPES.CHARACTER], 1
        )
        assert model.getAsset.called

        # Control wrong category
        with pytest.raises(RuntimeError):
            controller._getAsset(None, 1)

        # Control wrong parm id
        with pytest.raises(RuntimeError):
            controller._getAsset(
                settings.CATEGORIES[zefir.ASSET_TYPES.CHARACTER], 2
            )

    def test_validate_asset(self, mvc, shot_instance, settings, mocker):
        model, view, controller = mvc

        controller._addAsset(zefir.ASSET_TYPES.CHARACTER, shot_instance)
        asset = controller._getAsset(
            settings.CATEGORIES[zefir.ASSET_TYPES.CHARACTER], 1
        )

        # Mock setup
        context = mocker.MagicMock()
        context.find_asset_component = mocker.MagicMock(return_value=None)
        context.find_shot_instance_component = mocker.MagicMock(
            return_value=None
        )
        mocker.patch.dict(model.__dict__, _context=context)

        # Control for asset not to be loaded
        assert not controller._validateAsset(asset)
        assert not context.find_asset_component.called
        assert not context.find_shot_instance_component.called

        asset.load = True

        # Control for no stage
        asset.is_asset_context = True
        assert not controller._validateAsset(asset)
        assert context.find_asset_component.called

        asset.is_asset_context = False
        assert not controller._validateAsset(asset)
        assert context.find_shot_instance_component.called

        # Control no commit data
        commit_data = mocker.MagicMock()
        commit_data.commits = None
        context.find_shot_instance_component.return_value = commit_data
        assert not controller._validateAsset(asset)

        # Control all good
        commit_data.commits = True
        assert controller._validateAsset(asset)

    @pytest.mark.run
    def test_get_update(self, mvc, settings, shot_instance, node, mocker):
        # Setup
        model, view, controller = mvc

        mocker.patch.object(DisplayHoudiniDialog, 'displayHoudiniDialog')

        mocker.spy(model, 'isEmpty')
        mocker.spy(controller, '_loadAssetChecked')
        create_asset_node = mocker.MagicMock(return_value=(node, (0, 0)))
        mocker.patch.object(controller, '_createAssetNode', create_asset_node)

        context = mocker.MagicMock()
        mocker.patch.dict(model.__dict__, _context=context)

        commit_data = mocker.MagicMock()
        commit_data.commits = True
        context.find_shot_instance_component = mocker.MagicMock(
            return_value=commit_data
        )

        # Control for empty model check
        controller._getUpdate()
        assert model.isEmpty.called

        controller._addAsset(zefir.ASSET_TYPES.CHARACTER, shot_instance)
        asset = controller._getAsset(
            settings.CATEGORIES[zefir.ASSET_TYPES.CHARACTER], 1
        )
        asset.load = True

        mocker.spy(node.parm("update"), 'pressButton')
        controller._getUpdate()
        assert create_asset_node.called
        assert node.parm("stageID").evalAsInt() == asset.current_stage
        assert node.parm("instanceID").evalAsInt() == asset.instance_id
        assert node.parm("uvStageID").evalAsInt() == asset.uv_component_id
        assert node.parm("assetContext").evalAsInt() == asset.is_asset_context
        # Is not -1 when asset is a SET
        assert node.parm("assemblyID").evalAsInt() == -1
        assert node.parm('update').pressButton.called

        # Control asset uncheck
        assert controller._loadAssetChecked.called
        expected = mocker.call(
            settings.CATEGORIES[zefir.ASSET_TYPES.CHARACTER],
            asset.parm_id,
            False
        )
        assert controller._loadAssetChecked.call_args == expected
