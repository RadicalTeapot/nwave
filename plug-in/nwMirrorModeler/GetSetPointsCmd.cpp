//
// Copyright (C)
//
// File: GetSetPointsCmd.h
//
// Author: Mathias Capdet
//

#include "nwMirrorModelerMain.h"

#define CHECK_ERROR( status, msg )							\
	{														\
		if ( !status )										\
		{													\
			MGlobal::displayError( msg );					\
			MGlobal::displayError( status.errorString() );	\
			status.perror( msg );							\
			status.perror( status.errorString() );			\
			return status;									\
		}													\
	}														\


// Define the flags
#define POINTS_FLAG "-p"
#define POINTS_LONG_FLAG "-points"

#define WORLDSPACE_FLAG "-ws"
#define WORLDSPACE_LONG_FLAG "-worldspace"

#define HELP_FLAG "-h"
#define HELP_LONG_FLAG "-help"

using namespace nwave;

// Initialize the command
GetSetPointsCmd::GetSetPointsCmd() : space( MSpace::kObject ), state( GET ), helpFlagSet( false )
{
}

// Destroy the command
GetSetPointsCmd::~GetSetPointsCmd()
{
}

// Create the comand
void *GetSetPointsCmd::creator(){
	return new GetSetPointsCmd;
}

// Register the command's syntax
MSyntax GetSetPointsCmd::newSyntax()
{
	MStatus status;
	MSyntax syntax;

	// Register the flags
	status = syntax.addFlag( POINTS_FLAG, POINTS_LONG_FLAG, MSyntax::kDouble, MSyntax::kDouble, MSyntax::kDouble );
	status = syntax.makeFlagMultiUse( POINTS_FLAG );
	status = syntax.addFlag( WORLDSPACE_FLAG, WORLDSPACE_LONG_FLAG );
	status = syntax.addFlag( HELP_FLAG, HELP_LONG_FLAG );

	// Allow the current selection to be used as the object passed to the command
	syntax.useSelectionAsDefault( true );
	// Register the object to pass to the command and set the min and max object count
	status = syntax.setObjectType( MSyntax::MObjectFormat::kSelectionList, 1, 1 );

	// Deactivate the query and edit falgs
	syntax.enableQuery( false );
	syntax.enableEdit( false );

	return syntax;
}

// Parse the arguments passed to the command
MStatus GetSetPointsCmd::parseArgs( const MArgList &args )
{
	MStatus status;
	// Get the args passed to the command
	MArgDatabase argData( syntax(), args );

	// Check if points position flag is passed
	bool hasFlag = argData.isFlagSet( POINTS_FLAG, &status);
	CHECK_ERROR( status, "Error while getting points flags." );
	if ( hasFlag )
	{
		unsigned int count = argData.numberOfFlagUses( POINTS_FLAG );
		points.clear();
		points.setLength( count );
		MArgList pointsArgs;
		for ( unsigned int i = 0; i < count; i++ )
		{
			status = argData.getFlagArgumentList( POINTS_FLAG, i, pointsArgs );
			CHECK_ERROR( status, "Error while getting point positions flag values." );
			points[i] = MPoint (pointsArgs.asDouble( i*3, &status ), pointsArgs.asDouble( i*3+1, &status ), pointsArgs.asDouble( i*3+2, &status ));
			CHECK_ERROR( status, "Error while converting point positions flag values to MPoint." );
		}
		state = SET;
	}

	// Check if worldspace flag is passed
	hasFlag = argData.isFlagSet( WORLDSPACE_FLAG, &status);
	CHECK_ERROR( status, "Error while getting worldspace flag." );
	if ( hasFlag )
		space = MSpace::kWorld;

	// Check if help flag is passed and diplay help
	hasFlag = argData.isFlagSet( HELP_FLAG, &status);
	CHECK_ERROR( status, "Error while getting help flag." );
	if ( hasFlag )
	{
		helpFlagSet = true;
		MGlobal::displayInfo( "Synopsis getSetPoints [flags] [String...]\nFlags:\n\t-p -points\t3 float (multi-use)\n\t-ws -worldspace\n\t-h -help\n\nUse the points flag to set points positions, without it the command returns a list of all the point positions of the geometry" );
		return MStatus::kSuccess;
	}

	// Get the objects passed to the command
	MSelectionList objectSelectionList;
	status = argData.getObjects( objectSelectionList );
	CHECK_ERROR( status, "Error while getting the passed fluid object." );
	if (objectSelectionList.length() == 0 )
	{
		MGlobal::displayWarning( "A mesh must be selected or passed to the command.");
		return MStatus::kInvalidParameter;
	}
	objectSelectionList.getDagPath( 0, objectDagPath );

	return MStatus::kSuccess;
}

MStatus GetSetPointsCmd::doIt( const MArgList &args )
{
	MStatus status;
	// Parse the command arguments
	status = parseArgs( args );
	CHECK_ERROR( status, "Error while parsing arguments." );

	// Return if help flag is set
	if ( helpFlagSet )
		return MStatus::kSuccess;

	// Get the object shape
	status = objectDagPath.extendToShapeDirectlyBelow( 0 );
	CHECK_ERROR( status, "Error while getting the object's shape" );
	// Get the object's shape MObject
	MObject object = objectDagPath.node();
	CHECK_ERROR( status, "Error while getting the object's shape MObject" );
	// Get the shape's dependency node
	MFnDependencyNode node(object, &status);
	CHECK_ERROR( status, "Error while getting the object's shape dependency node" );

	// Stop and display an error if the passed object is of the wrong type
	if (
		strcmp( node.typeName().asChar(), "mesh" ) != 0 &&
		strcmp( node.typeName().asChar(), "nurbsCurve" ) != 0 &&
		strcmp( node.typeName().asChar(), "nurbsSurface" ) != 0 &&
		strcmp( node.typeName().asChar(), "lattice" ) != 0
		)
	{
		MGlobal::displayWarning( "Invalid object selected or passed to the command." );
		return MStatus::kInvalidParameter;
	}

	// Get the original points positions for undo/redo
	MItGeometry itGeo( objectDagPath, &status );
	CHECK_ERROR( status, "Error while getting the object's itGeometry." );
	status = itGeo.allPositions( nonModifiedPoints, space );
	CHECK_ERROR( status, "Error while getting the object's points positions." );

	return redoIt();
}

MStatus GetSetPointsCmd::redoIt()
{
	MStatus status;

	if ( state == SET )
	{
		// Check if the number of points passed to the command is correct
		if ( points.length() != nonModifiedPoints.length() )
		{
			MGlobal::displayWarning( "Wrong number of points passed to the command." );
			return MStatus::kInvalidParameter;
		}

		// Set the objects points positions
		MItGeometry itGeo( objectDagPath, &status );
		CHECK_ERROR( status, "Error while getting the object's itGeometry." );
		status = itGeo.setAllPositions( points, space );
		CHECK_ERROR( status, "Error while getting the object's points positions." );

		clearResult();
		setResult( true );
	}
	else
	{
		clearResult();
		MDoubleArray positions;

		positions.clear();
		unsigned int count = nonModifiedPoints.length();
		positions.setLength( count * 3 );
		for ( unsigned int i = 0; i < count; i++ )
		{
			positions[i*3] = nonModifiedPoints[i][0];
			positions[i*3+1] = nonModifiedPoints[i][1];
			positions[i*3+2] = nonModifiedPoints[i][2];
		}

		setResult( positions );
	}

	return MStatus::kSuccess;
}

MStatus GetSetPointsCmd::undoIt()
{
	MStatus status;

	if ( state == SET )
	{
		// Set the objects points positions
		MItGeometry itGeo( objectDagPath, &status );
		CHECK_ERROR( status, "Error while getting the object's itGeometry." );
		status = itGeo.setAllPositions( nonModifiedPoints, space );
		CHECK_ERROR( status, "Error while getting the object's points positions." );

		clearResult();
		setResult( true );
	}

	return MStatus::kSuccess;
}

bool GetSetPointsCmd::isUndoable() const
{
	return ( state == SET );
}