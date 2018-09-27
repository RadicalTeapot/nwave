//
// Copyright (C)
//
// File: nwDeformerWeightsCmdMain.cpp
//
// Author: Mathias Capdet
//
#include <maya/MFnPlugin.h>
#include "nwDeformerWeightsCmdMain.h"


MStatus initializePlugin( MObject obj )
{
	MStatus   status;
	MFnPlugin plugin( obj, "Mathias Capdet", "1.0", "Any" );

	status = plugin.registerCommand( 
		nwave::nwDeformerWeightsCmd::command_name, 
		nwave::nwDeformerWeightsCmd::creator, 
		nwave::nwDeformerWeightsCmd::newSyntax );
	if ( !status ) {
		status.perror( "Error while registering the " + nwave::nwDeformerWeightsCmd::command_name + " command" );
		return status;
	}

	return status;
}

MStatus uninitializePlugin( MObject obj )
{
	MStatus   status;
	MFnPlugin plugin( obj );

	status = plugin.deregisterCommand( nwave::nwDeformerWeightsCmd::command_name );
	if ( !status ) {
		status.perror( "Error while deregistering the " + nwave::nwDeformerWeightsCmd::command_name + " command" );
		return status;
	}

	return status;
}
