//
// Copyright (C) 
// 
// File: GetMirrorVerticesIndex.h
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
#define SEARCH_POSITION_FLAG "-p"
#define SEARCH_POSITION_LONG_FLAG "-position"
#define MIRROR_AXIS_FLAG "-ma"
#define MIRROR_AXIS_LONG_FLAG "-mirrorAxis"
#define MIRROR_POSITION_FLAG "-mp"
#define MIRROR_POSITION_LONG_FLAG "-mirrorPosition"
#define THRESHOLD_FLAG "-t"
#define THRESHOLD_LONG_FLAG "-threshold"
#define WORLDSPACE_FLAG "-ws"
#define WORLDSPACE_LONG_FLAG "-worldSpace"
#define HELP_FLAG "-h"
#define HELP_LONG_FLAG "-help"

using namespace nwave;

// Initialize the command
GetMirrorVerticesIndex::GetMirrorVerticesIndex() : useWorldspace( false ), searchPosition( MPoint(0,0,0) ), mirrorMode( NONE ), 
	threshold( 0.001 ), helpFlagSet( false ),  usePosition( false ), useMirror( false ), mirrorPosition( MPoint(0,0,0) ),
	objectType( NO_TYPE ), tree( NULL ), dimensionX( -1 ), dimensionY( -1 ), dimensionZ( -1 )
{
}

// Destroy the command
GetMirrorVerticesIndex::~GetMirrorVerticesIndex() 
{
	if ( tree != NULL )
		delete tree;
}

// Create the comand
void *GetMirrorVerticesIndex::creator(){
	return new GetMirrorVerticesIndex;
}

// Make the command not undoable
bool GetMirrorVerticesIndex::isUndoable() const
{
	return false;
}

// Register the command's syntax
MSyntax GetMirrorVerticesIndex::newSyntax()
{
	MStatus status;
	MSyntax syntax;

	// Register the flags
	status = syntax.addFlag( SEARCH_POSITION_FLAG, SEARCH_POSITION_LONG_FLAG, MSyntax::kDouble, MSyntax::kDouble, MSyntax::kDouble );
	status = syntax.addFlag( MIRROR_AXIS_FLAG, MIRROR_AXIS_LONG_FLAG, MSyntax::kUnsigned );
	status = syntax.addFlag( MIRROR_POSITION_FLAG, MIRROR_POSITION_LONG_FLAG, MSyntax::kDouble, MSyntax::kDouble, MSyntax::kDouble );
	status = syntax.addFlag( THRESHOLD_FLAG, THRESHOLD_LONG_FLAG, MSyntax::kDouble );
	status = syntax.addFlag( WORLDSPACE_FLAG, WORLDSPACE_LONG_FLAG );
	status = syntax.addFlag( HELP_FLAG, HELP_LONG_FLAG );

	// Allow the current selection to be used as the object passed to the command
	syntax.useSelectionAsDefault( true );
	// Register the object to pass to the command and set the min and max object count
	status = syntax.setObjectType( MSyntax::MObjectFormat::kSelectionList, 0, 1 );

	// Deactivate the query and edit falgs
	syntax.enableQuery( false );
	syntax.enableEdit( false );

	return syntax;
}

// Parse the arguments passed to the command
MStatus GetMirrorVerticesIndex::parseArgs( const MArgList &args )
{
	MStatus status;
	// Get the args passed to the command
	MArgDatabase argData( syntax(), args );

	// Check if search position flag is passed
	bool hasFlag = argData.isFlagSet( SEARCH_POSITION_FLAG, &status );
	CHECK_ERROR( status, "Error while getting search position flag." );
	if ( hasFlag )
	{
		searchPosition = MPoint(
			argData.flagArgumentDouble( SEARCH_POSITION_FLAG, 0, &status ),
			argData.flagArgumentDouble( SEARCH_POSITION_FLAG, 1, &status ),
			argData.flagArgumentDouble( SEARCH_POSITION_FLAG, 2, &status )
			);
		CHECK_ERROR( status, "Error while getting search position flag values." );
	}
	usePosition = hasFlag;

	// Check if mirror axis flag is passed
	hasFlag = argData.isFlagSet( MIRROR_AXIS_FLAG, &status );
	CHECK_ERROR( status, "Error while getting mirror axis flag." );
	if ( hasFlag )
	{
		int value = argData.flagArgumentInt( MIRROR_AXIS_FLAG, 0, &status );
		CHECK_ERROR( status, "Error while getting mirror axis flag value." );
		switch(value)
		{
		case 0: mirrorMode = MIRROR_X; break;
		case 1: mirrorMode = MIRROR_Y; break;
		case 2: mirrorMode = MIRROR_Z; break;
		default : 
			MGlobal::displayError( "Bad mirror axis specified, the possible values are 0 for x axis mirror, 1 for y axis mirror and 2 for z axis mirror." );
			return MStatus::kInvalidParameter;
			break;
		}
	}
	useMirror = hasFlag;

	// Check if mirror position flag is passed
	hasFlag = argData.isFlagSet( MIRROR_POSITION_FLAG, &status );
	CHECK_ERROR( status, "Error while getting mirror position pos flag." );
	if ( hasFlag )
	{
		mirrorPosition = MPoint(
			argData.flagArgumentDouble( MIRROR_POSITION_FLAG, 0, &status ),
			argData.flagArgumentDouble( MIRROR_POSITION_FLAG, 1, &status ),
			argData.flagArgumentDouble( MIRROR_POSITION_FLAG, 2, &status )
			);
		CHECK_ERROR( status, "Error while getting mirror position flag values." );
	}

	// Check if threshold flag is passed
	hasFlag = argData.isFlagSet( THRESHOLD_FLAG, &status );
	CHECK_ERROR( status, "Error while getting threshold flag." );
	if ( hasFlag )
	{
		threshold = argData.flagArgumentDouble( THRESHOLD_FLAG, 0, &status );
		CHECK_ERROR( status, "Error while getting threshold flag value." );
	}

	// Check if worldspace flag is passed
	hasFlag = argData.isFlagSet( WORLDSPACE_FLAG, &status );
	CHECK_ERROR( status, "Error while getting worldspace flag." );
	useWorldspace = hasFlag;

	// Check if help flag is passed
	hasFlag = argData.isFlagSet( HELP_FLAG, &status );
	CHECK_ERROR( status, "Error while getting help flag." );
	helpFlagSet = hasFlag;

	// Get the objects passed to the command
	status = argData.getObjects( objectSelectionList );
	CHECK_ERROR( status, "Error while getting the passed fluid object." );

	return MStatus::kSuccess;
}

MStatus GetMirrorVerticesIndex::doIt( const MArgList &args )
{
	// Parse the command arguments
	parseArgs( args );

	// Display help if help flag is set
	if ( helpFlagSet )
	{
		// TODO Flesh out help str
		MGlobal::displayInfo( "Help not implemented" );
		return MStatus::kSuccess;
	}

	// Display an error message and stop if the command is neither in mirror mode or position mode
	if ( useMirror == false && usePosition == false )
	{
		MGlobal::displayError( "Neither -mirrorAxis nor -position flags used, specify one and try again" );
		return MStatus::kInvalidParameter;
	}

	// Display an error message and stop if the command is in both the mirror mode and position mode
	if ( useMirror == true && usePosition == true )
	{
		MGlobal::displayError( "Both -mirrorAxis and -position flags used, remove one and try again." );
		return MStatus::kInvalidParameter;
	}

	// Make sure there's at least one object passed to export
	if ( objectSelectionList.isEmpty() )
	{
		MGlobal::displayError( "No object passed to the command. Either select one or pass it's name to the command and try again." );
		return MStatus::kNotFound;
	}

	// Make sure the passed object is of the correct type (mesh, nurbsCurve, nurbsSurface or lattice)
	MStatus status;
	// Get the object's dag path
	MDagPath dagPath;
	status = objectSelectionList.getDagPath( 0, dagPath );
	CHECK_ERROR( status, "Error while getting the object dagPath" );
	// Get the object shape
	status = dagPath.extendToShapeDirectlyBelow( 0 );
	CHECK_ERROR( status, "Error while getting the object's shape" );
	// Get the object's shape MObject
	MObject object = dagPath.node();
	CHECK_ERROR( status, "Error while getting the object's shape MObject" );
	// Get the shape's dependency node
	MFnDependencyNode node(object, &status);
	CHECK_ERROR( status, "Error while getting the object's shape dependency node" );
	
	if ( tree != NULL )
		delete tree;

	tree = new KdTree();
	
	// Store the object's points
	points.clear();
	// Store the point ids
	MIntArray ids;

	// Get the points if the object is a mesh
	if ( strcmp( node.typeName().asChar(), "mesh" ) == 0 )
	{
		MFnMesh mesh(dagPath, &status);
		CHECK_ERROR( status, "Error while getting the object's MFnMesh" );
		if ( !useWorldspace )
			status = mesh.getPoints(points, MSpace::kObject);
		else
			status = mesh.getPoints(points, MSpace::kWorld);
		CHECK_ERROR( status, "Error while getting the mesh points" );

		dimensionX = points.length();

		for ( unsigned int i = 0 ; i < dimensionX; i++ )
			ids.append( i );

		objectType = MESH;
	}
	// Get the points if the object is a nurbs curve
	else if ( strcmp( node.typeName().asChar(), "nurbsCurve" ) == 0 )
	{
		MFnNurbsCurve curve(dagPath, &status);
		CHECK_ERROR( status, "Error while getting the object's MFNurbsCurve" );

		/*
		if ( !useWorldspace )
			status = curve.getCVs(points, MSpace::kObject);
		else
			status = curve.getCVs(points, MSpace::kWorld);
		CHECK_ERROR( status, "Error while getting the curve control vertices" );
		*/

		dimensionX = curve.numCVs( &status );
		if ( curve.form() == MFnNurbsCurve::kPeriodic )
			dimensionX = curve.numSpans( &status );
		CHECK_ERROR( status, "Error while getting the curve cv count" );

		status = points.clear();
		CHECK_ERROR( status, "Error while clearing points array" );
		MPoint point;
		// Fill the point list with point positions and ids
		for ( unsigned int i = 0 ; i < dimensionX; i++ )
		{
			ids.append( i );
			if ( !useWorldspace )
				status = curve.getCV( i, point, MSpace::kObject );
			else
				status = curve.getCV( i, point, MSpace::kWorld );
			CHECK_ERROR( status, "Error while getting the curve control vertices" );
			points.append( point );
		}

		objectType = NURBS_CURVE;
	}
	// Get the points if the object is a nurbs surface
	else if ( strcmp( node.typeName().asChar(), "nurbsSurface" ) == 0 )
	{
		MFnNurbsSurface surface(dagPath, &status);
		CHECK_ERROR( status, "Error while getting the object's MFnNurbsSurface" );

		dimensionX = surface.numCVsInU( &status );
		if ( surface.formInU() == MFnNurbsSurface::kPeriodic )
			dimensionX = surface.numSpansInU( &status );
		CHECK_ERROR( status, "Error while getting the surface u cv count" );
		dimensionY = surface.numCVsInV( &status );
		if ( surface.formInV() == MFnNurbsSurface::kPeriodic )
			dimensionY = surface.numSpansInV( &status );
		CHECK_ERROR( status, "Error while getting the surface v cv count" );

		status = points.clear();
		CHECK_ERROR( status, "Error while clearing points array" );
		MPoint point;
		// Fill the point list with point positions and ids
		for ( unsigned int i = 0; i < dimensionX; i++ )
		{
			for ( unsigned int j = 0; j < dimensionY; j++ )
			{
				ids.append( i );
				ids.append( j );
				if ( !useWorldspace )
					status = surface.getCV( i, j, point, MSpace::kObject );
				else
					status = surface.getCV( i, j, point, MSpace::kWorld );
				CHECK_ERROR( status, "Error while getting the surface control vertices" );
				points.append( point );
			}
		}

		CHECK_ERROR( status, "Error while getting the surface v span count" );

		objectType = NURBS_SURFACE;
	}
	// Get the points if the object is a lattice
	else if ( strcmp( node.typeName().asChar(), "lattice" ) == 0 )
	{
		if ( useWorldspace )
			MGlobal::displayWarning( "Can't use worldspace positions with lattice, defaulting to object space" );

		MFnLattice lattice(dagPath, &status);
		CHECK_ERROR( status, "Error while getting the object's MFnLattice" );
		status = lattice.getDivisions( dimensionX, dimensionY, dimensionZ );
		CHECK_ERROR( status, "Error while getting the lattice divisions" );
		status = points.clear();
		CHECK_ERROR( status, "Error while clearing points array" );

		for ( unsigned int i = 0; i < dimensionX; i++ )
		{
			for ( unsigned int j = 0; j < dimensionY; j++ )
			{
				for ( unsigned int k = 0; k < dimensionZ; k++ )
				{
					points.append( lattice.point( i, j, k, &status ) );
					CHECK_ERROR( status, "Error while getting the lattice points" );
					ids.append( i );
					ids.append( j );
					ids.append( k );
				}
			}
		}

		objectType = LATTICE;
	}
	// Display the error message and stop if the object is not of any accepted types
	else
	{
		MGlobal::displayError( "No correct object passed to the command. Either select one or pass it's name to the command and try again." );
		return MStatus::kInvalidParameter;
	}

	// Stop and display an error message if the point count is null
	if ( points.length() == 0 )
	{
		MGlobal::displayError( "No points to work on." );
		return MStatus::kInvalidParameter;
	}

	// Fill the point list with point positions and ids
	tree->build( points, ids );

	return redoIt();
}

MStatus GetMirrorVerticesIndex::redoIt()
{
	MStatus status;
	
	// If the command is set to position mode
	if ( usePosition == true )
	{
		// Find the nearest point to the search position
		KdTree::Node *nearest = tree->nearestNode( searchPosition );

		// Return the nearest point id if a point was found and -1 otherwise
		MIntArray result;
		
		if ( nearest != NULL )
		{
			double dist = (
				sqrt( 
					pow( searchPosition[0] - nearest->point[0], 2 ) +
					pow( searchPosition[1] - nearest->point[1], 2 ) +
					pow( searchPosition[2] - nearest->point[2], 2 ) 
					) 
				);
			if ( dist > threshold )
			{
				switch ( objectType )
				{
				case MESH:
				case NURBS_CURVE:
					result.append( -2 );
					break;
				case NURBS_SURFACE:
					result.append( -2 );
					result.append( -2 );
					break;
				case LATTICE :
					result.append( -2 );
					result.append( -2 );
					result.append( -2 );
					break;
				default :
					return MStatus::kFailure;
				}
			}
			else
			{
				switch ( objectType )
				{
				case MESH :
				case NURBS_CURVE:
					result.append( nearest->id.x );
					break;
				case NURBS_SURFACE:
					result.append( nearest->id.x );
					result.append( nearest->id.y );
					break;
				case LATTICE:
					result.append( nearest->id.x );
					result.append( nearest->id.y );
					result.append( nearest->id.z );
					break;
				default:
					return MStatus::kFailure;
				}
			}
		}
		else
		{
			switch ( objectType )
			{
			case MESH :
			case NURBS_CURVE:
				result.append( -1 );
				break;
			case NURBS_SURFACE:
				result.append( -1 );
				result.append( -1 );
				break;
			case LATTICE:
				result.append( -1 );
				result.append( -1 );
				result.append( -1 );
				break;
			default:
				return MStatus::kFailure;
			}
		}
		clearResult();
		setResult( result );
	}
	// If the command is set to mirror mode
	else if ( useMirror == true )
	{
		// Store the matching ids
		MIntArray mirrorIds;

		// Find all the matching ids for the points mirrored positions
		status = mirrorSearch( mirrorIds );

		// Return the matching ids array
		clearResult();
		setResult(mirrorIds);
	}
	return MStatus::kSuccess;
}

MStatus GetMirrorVerticesIndex::mirrorSearch( MIntArray &mirrorIds )
{
	MStatus status = MStatus::kSuccess;

	unsigned int pointCount = points.length();

	// Store whether an id has been set
	MIntArray setIds( pointCount, 0 );

	// Create the temporary id array
	MIntArray tmpIds( pointCount, -2 );

	// Cycle on all the points of the geometry
	for ( unsigned int i = 0; i < pointCount; i++ )
	{
		// Skip the points with ids already set
		if ( setIds[i] != 0 )
			continue;

		MPoint mirroredPos = points[i];

		if ( useWorldspace )
		{
			MVector diff = mirroredPos - mirrorPosition;
			switch( mirrorMode )
			{
			case MIRROR_X : diff[0] *= -1; break;
			case MIRROR_Y : diff[1] *= -1; break;
			case MIRROR_Z : diff[2] *= -1; break;
			}
			mirroredPos = mirrorPosition + diff;
		}
		else
		{
			switch( mirrorMode )
			{
			case MIRROR_X : mirroredPos[0] *= -1; break;
			case MIRROR_Y : mirroredPos[1] *= -1; break;
			case MIRROR_Z : mirroredPos[2] *= -1; break;
			}
		}

		KdTree::Node *nearestPoint = tree->nearestNode( mirroredPos );

		if ( nearestPoint != NULL )
		{
			double dist = (
				sqrt( 
					pow( mirroredPos[0] - nearestPoint->point[0], 2 ) +
					pow( mirroredPos[1] - nearestPoint->point[1], 2 ) +
					pow( mirroredPos[2] - nearestPoint->point[2], 2 ) 
					) 
				);
			if ( dist <= threshold )
			{
				switch ( objectType )
				{
				case MESH:
				case NURBS_CURVE:
					tmpIds[i] = nearestPoint->id.x;
					break;
				case NURBS_SURFACE:
					tmpIds[i] = nearestPoint->id.x * dimensionY + nearestPoint->id.y;
					break;
				case LATTICE :
					tmpIds[i] = nearestPoint->id.x * dimensionY * dimensionZ + nearestPoint->id.y * dimensionZ + nearestPoint->id.z;
					break;
				default :
					return MStatus::kFailure;
				}
			}
		}

		setIds[i] = 1;
	}
	CHECK_ERROR( status, "Error while finding the nearest neighbour" );

	// Empty the mirror ids array
	status = mirrorIds.clear();
	CHECK_ERROR( status, "Error while finding the clearing the ids array." );
	// Copy the contents of the temporary ids in the mirror ids array
	status = mirrorIds.copy( tmpIds );
	CHECK_ERROR( status, "Error copying data to the ids array" );
	
	return status;
}