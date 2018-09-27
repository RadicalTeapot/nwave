//
// Copyright (C)
//
// File: nwMirrorModelerMain.cpp
//
// Author: Mathias Capdet
//
#include <maya/MFnPlugin.h>
#include "nwMirrorModelerMain.h"

MStatus initializePlugin( MObject obj )
{
	MStatus   status;
	MFnPlugin plugin( obj, "Mathias Capdet", "1.0", "Any" );

	status = plugin.registerCommand( "getSetPoints", nwave::GetSetPointsCmd::creator, nwave::GetSetPointsCmd::newSyntax );
	if (!status) {
		status.perror( "Error while registering the getSetPointsCmd command" );
		return status;
	}

	status = plugin.registerCommand( "getMirrorVerticesIndex", nwave::GetMirrorVerticesIndex::creator, nwave::GetMirrorVerticesIndex::newSyntax );
	if (!status) {
		status.perror( "Error while registering the getMirrorVerticesIndex command" );
		return status;
	}

	status = plugin.registerCommand( "floodRelax", nwave::FloodRelax::creator, nwave::FloodRelax::newSyntax );
	if ( !status ) {
		status.perror( "Error while registering the floodRelax command" );
		return status;
	}

	return status;
}

MStatus uninitializePlugin( MObject obj)
{
	MStatus   status;
	MFnPlugin plugin( obj );

	status = plugin.deregisterCommand( "getSetPoints" );
	if (!status) {
		status.perror( "Error while deregistering the getSetPointsCmd command" );
		return status;
	}

	status = plugin.deregisterCommand( "getMirrorVerticesIndex" );
	if (!status) {
		status.perror( "Error while deregistering the getMirrorVerticesIndex command" );
		return status;
	}

	status = plugin.deregisterCommand( "floodRelax" );
	if ( !status ) {
		status.perror( "Error while deregistering the floodRelax command" );
		return status;
	}

	return status;
}