# -*- coding: utf-8 -*-
"""Common methods of the Pair Connector."""

import maya.cmds as mc


class Utils:
    """Collection of methods of the Pair Connector."""

    @staticmethod
    def connectAttribute(source, destination, attribute):
        """Connect the visibility attribute of two nodes.

        The attribute value is copied from the source to the destination in
        case no anim curve exists on the source attribute. The anim curve from
        the source attribute is connected to the destination attribute
        otherwise. A RuntimeError exception is raised if the destination node
        is referenced and it's attribute is locked as this prevents changing
        or connecting it.

        Parameters
        ----------
        source: str
            The full path to the object to use as a source for the connection.
        destination: str
            The full path to the object to use as a destination for
            the connection.
        attribute: str
            The attribute name to use for the connection.

        Raises
        ------
        RuntimeError
            The destination node is referenced and the destination attibute is
            locked.

        """
        source_attribute = '{}.{}'.format(source, attribute)
        destination_attribute = '{}.{}'.format(destination, attribute)

        # Raise if the destination node is referenced.
        if (
            mc.referenceQuery(destination, isNodeReferenced=True) and
            mc.getAttr(destination_attribute, lock=True)
        ):
            raise RuntimeError(
                '{} is referenced and locked.'.format(destination_attribute)
            )

        value = mc.getAttr(source_attribute)

        # Get the input connections of the source attribute
        source_connections = mc.listConnections(
            source_attribute,
            source=True,
            destination=False
        )
        anim_curves = []
        if source_connections:
            anim_curves = [
                node
                for node in source_connections
                if 'anim' in mc.nodeType(node)
            ]

        # Get the input connections of the destination attribute
        destination_connections = mc.listConnections(
            destination_attribute,
            source=True,
            destination=False
        )

        # Skip if the same anim curves are found connected on the source
        # and destination attribute
        if (
            destination_connections and
            any(node in destination_connections for node in anim_curves)
        ):
            return

        if anim_curves:
            # Connect the anim curve to the destination attribute
            mc.connectAttr(
                '{}.output'.format(anim_curves[0]),
                destination_attribute,
                force=True,
                lock=False
            )
        else:
            if mc.getAttr(destination_attribute, lock=True):
                mc.setAttr(destination_attribute, lock=False)
            mc.setAttr(destination_attribute, value)

    @staticmethod
    def connectWorldMesh(source, destination, ignore_inputs=False):
        """Connect the world mesh/in mesh attributes of two nodes.

        Parameters
        ----------
        source: str
            The full path to the object to use as a source for the connection.
        destination: str
            The full path to the object to use as a destination for
            the connection.
        ignore_inputs: bool
            Whether to ignore connected input blendshapes on the destination
            attribute.

        Raises
        ------
        RuntimeError
            The destination node is referenced and it's in mesh attribute is
            locked.

        """
        source_attribute = '{}.worldMesh[0]'.format(source)
        destination_attribute = '{}.inMesh'.format(destination)

        # Raise if the destination node is referenced.
        if (
            mc.referenceQuery(destination, isNodeReferenced=True) and
            mc.getAttr(destination_attribute, lock=True)
        ):
            raise RuntimeError(
                '{} is referenced and locked.'.format(destination_attribute)
            )

        # Get the output connection of the source attribute
        source_connections = mc.listConnections(
            source_attribute,
            source=False,
            destination=True
        )
        # Stop if the attributes are already connected to each other
        if source_connections:
            source_connections = [
                mc.ls(node, l=True)[0]
                for node in source_connections
            ]
            if destination in source_connections:
                return

        if not ignore_inputs:
            # Get the input connections of the destination attribute
            destination_connections = mc.listConnections(
                destination_attribute,
                source=True,
                destination=False
            )

            blend_shape_nodes = []
            if destination_connections:
                blend_shape_nodes = [
                    node
                    for node in destination_connections
                    if 'blendShape' in mc.nodeType(node)
                ]

            if blend_shape_nodes:
                return

        mc.connectAttr(
            source_attribute, destination_attribute, force=True, lock=False
        )

    @staticmethod
    def makeBlendShape(source, destination):
        """Connect two nodes with a blendshape.

        The blendshape is created in world space and it's weight attribute is
        set to 1.
        Parameters
        ----------
        source: str
            The full path to the object to use as a source for the connection.
        destination: str
            The full path to the object to use as a destination for
            the connection.

        Raises
        ------
        RuntimeError
            The destination node is referenced some of it's transform
            attributes are locked.

        """
        # Build the attribute names
        destination_translate_x = '{}.translateX'.format(destination)
        destination_translate_y = '{}.translateY'.format(destination)
        destination_translate_z = '{}.translateZ'.format(destination)

        destination_rotate_x = '{}.rotateX'.format(destination)
        destination_rotate_y = '{}.rotateY'.format(destination)
        destination_rotate_z = '{}.rotateZ'.format(destination)

        destination_scale_x = '{}.scaleX'.format(destination)
        destination_scale_y = '{}.scaleY'.format(destination)
        destination_scale_z = '{}.scaleZ'.format(destination)

        # Raise if the destination node is referenced.
        if (mc.referenceQuery(destination, isNodeReferenced=True)):
            for attr in [
                destination_translate_x,
                destination_translate_y,
                destination_translate_z,

                destination_rotate_x,
                destination_rotate_y,
                destination_rotate_z,

                destination_scale_x,
                destination_scale_y,
                destination_scale_z
            ]:
                if mc.getAttr(attr, lock=True):
                    raise RuntimeError(
                        '{} is referenced and locked.'.format(attr)
                    )

        # Reset the destination transform
        for attr in [
            destination_translate_x,
            destination_translate_y,
            destination_translate_z
        ]:
            if mc.getAttr(attr, lock=True):
                mc.setAttr(attr, lock=False)
            mc.setAttr(attr, 0)

        for attr in [
            destination_rotate_x,
            destination_rotate_y,
            destination_rotate_z
        ]:
            if mc.getAttr(attr, lock=True):
                mc.setAttr(attr, lock=False)
            mc.setAttr(attr, 0)

        for attr in [
            destination_scale_x,
            destination_scale_y,
            destination_scale_z
        ]:
            if mc.getAttr(attr, lock=True):
                mc.setAttr(attr, lock=False)
            mc.setAttr(attr, 1)

        # Create the blend shape
        mc.blendShape(source, destination, weight=(0, 1), origin='world')

    @staticmethod
    def makeWrap(source, destination):
        """Connect two nodes with a blendshape.

        The blendshape is created in world space and it's weight attribute is
        set to 1.
        Parameters
        ----------
        source: str
            The full path to the object to use as a source for the connection.
        destination: str
            The full path to the object to use as a destination for
            the connection.

        Raises
        ------
        RuntimeError
            The destination node is referenced some of it's transform
            attributes are locked.

        """
        # Create the wrap node and set it's attribute values
        wrap = mc.deformer(destination, type='wrap')[0]
        mc.setAttr("{0}.exclusiveBind".format(wrap), 1)
        mc.setAttr('{0}.maxDistance'.format(wrap), 1.0)
        mc.setAttr('{0}.autoWeightThreshold'.format(wrap), True)

        # Create the base geo mesh, hide it and connect it to the wrap
        baseGeo = mc.duplicate(source, n='{0}_baseMesh'.format(source))[0]
        mc.setAttr('{0}.visibility'.format(baseGeo), lock=False)
        mc.setAttr('{0}.visibility'.format(baseGeo), 0)
        mc.connectAttr(
            '{0}.worldMesh[0]'.format(baseGeo),
            '{0}.basePoints[0]'.format(wrap),
            f=True
        )

        # Connect the source node to the wrap node
        mc.connectAttr(
            '{0}.worldMesh[0]'.format(source),
            '{0}.driverPoints[0]'.format(wrap),
            f=True
        )

        # Create the necessary attributes on the source node and connect them
        # to the wrap node
        if not mc.attributeQuery('inflType', node=source, exists=True):
            mc.addAttr(
                source, ln='inflType', at='short',
                dv=2, min=1, max=2
            )
        mc.connectAttr(
            '{0}.inflType'.format(source),
            '{0}.inflType[0]'.format(wrap)
        )

        if not mc.attributeQuery('smoothness', node=source, exists=True):
            mc.addAttr(
                source, ln='smoothness',
                at='double', dv=0.0
            )
        mc.connectAttr(
            '{0}.smoothness'.format(source),
            '{0}.smoothness[0]'.format(wrap)
        )

        if not mc.attributeQuery('dropoff', node=source, exists=True):
            mc.addAttr(
                source, ln='dropoff', at='double', dv=4.0
            )
        mc.connectAttr(
            '{0}.dropoff'.format(source),
            '{0}.dropoff[0]'.format(wrap)
        )

        # Connect the destination node to the wrap node
        mc.connectAttr(
            "{0}.worldMatrix[0]".format(destination),
            "{0}.geomMatrix".format(wrap), f=True
        )
