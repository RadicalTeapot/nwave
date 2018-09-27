//
// Copyright (C) 
// 
// File: FloodRelax.cpp
//
// Author: Mathias Capdet
//

#include "nwMirrorModelerMain.h"

#define LENGTH_2( vector ) vector.x * vector.x + vector.y * vector.y + vector.z * vector.z;

#define BUILD_ERROR( msg, status_type )						\
	{														\
		MStatus status = status_type;						\
		MGlobal::displayError( msg );						\
		status.perror( msg );								\
		return status;										\
	}														\

#define CHECK_ERROR( status, msg, return_object )			\
	{														\
		if ( !status )										\
		{													\
			MGlobal::displayError( msg );					\
			MGlobal::displayError( status.errorString() );	\
			status.perror( msg );							\
			status.perror( status.errorString() );			\
			return return_object;							\
		}													\
	}														\

#define WEIGHT_FLAG "-we"
#define WEIGHT_LONG_FLAG "-weight"
#define THRESHOLD_FLAG "-th"
#define THRESHOLD_LONG_FLAG "-threshold"
#define CACHE_NODE_FLAG "-cn"
#define CACHE_NODE_LONG_FLAG "-cacheNode"
#define X_FLAG "-x"
#define X_LONG_FLAG "-xAxis"
#define Y_FLAG "-y"
#define Y_LONG_FLAG "-yAxis"
#define Z_FLAG "-z"
#define Z_LONG_FLAG "-zAxis"
#define COMPONENTS_FLAG "-co"
#define COMPONENTS_LONG_FLAG "-components"

#define CACHE_ATTR_X "acMirrorModelerX"
#define CACHE_ATTR_Y "acMirrorModelerY"
#define CACHE_ATTR_Z "acMirrorModelerZ"

using namespace nwave;

FloodRelax::FloodRelax() : weight( 1.0 ), threshold ( 1.0e-4 ), use_x_axis( false ), use_y_axis( false ), use_z_axis( false ), 
	use_components( false )
{
}


FloodRelax::~FloodRelax()
{
}


void *FloodRelax::creator() 
{
	return new FloodRelax();
}

bool FloodRelax::isUndoable() const
{
	return true;
}

MSyntax FloodRelax::newSyntax()
{
	MStatus status;
	MSyntax syntax;

	status = syntax.addFlag( WEIGHT_FLAG, WEIGHT_LONG_FLAG, MSyntax::kDouble );
	CHECK_ERROR( status, "Error while adding weight flag", syntax );
	status = syntax.addFlag( THRESHOLD_FLAG, THRESHOLD_LONG_FLAG, MSyntax::kDouble );
	CHECK_ERROR( status, "Error while adding threshold flag", syntax );
	status = syntax.addFlag( CACHE_NODE_FLAG, CACHE_NODE_LONG_FLAG, MSyntax::kString );
	CHECK_ERROR( status, "Error while adding cache node flag", syntax );
	status = syntax.addFlag( X_FLAG, X_LONG_FLAG );
	CHECK_ERROR( status, "Error while adding x flag", syntax );
	status = syntax.addFlag( Y_FLAG, Y_LONG_FLAG );
	CHECK_ERROR( status, "Error while adding y flag", syntax );
	status = syntax.addFlag( Z_FLAG, Z_LONG_FLAG );
	CHECK_ERROR( status, "Error while adding z flag", syntax );
	status = syntax.addFlag( COMPONENTS_FLAG, COMPONENTS_LONG_FLAG, MSyntax::kUnsigned );
	CHECK_ERROR( status, "Error while adding components flag", syntax );
	status = syntax.makeFlagMultiUse( COMPONENTS_FLAG );
	CHECK_ERROR( status, "Error while making components flag multi use", syntax );


	syntax.useSelectionAsDefault( true );
	status = syntax.setObjectType( MSyntax::MObjectFormat::kSelectionList, 0, 1 );
	CHECK_ERROR( status, "Error while setting command object type flag", syntax );

	syntax.enableQuery( false );
	syntax.enableEdit( false );

	return syntax;
}

MStatus FloodRelax::parseArgs( const MArgList &args )
{
	MStatus status;
	MArgDatabase arg_data( syntax(), args );

	bool has_flag = arg_data.isFlagSet( WEIGHT_FLAG, &status );
	CHECK_ERROR( status, "Error while trying to read weight flag status", status );
	if ( !has_flag ) BUILD_ERROR( "Can't find weight flag", MS::kInvalidParameter );
	weight = arg_data.flagArgumentDouble( WEIGHT_FLAG, 0, &status );
	CHECK_ERROR( status, "Error while trying to read weight flag value", status );

	has_flag = arg_data.isFlagSet( THRESHOLD_FLAG, &status );
	CHECK_ERROR( status, "Error while trying to read threshold flag status", status );
	if ( !has_flag ) BUILD_ERROR( "Can't find threshold flag", MS::kInvalidParameter );
	threshold = arg_data.flagArgumentDouble( THRESHOLD_FLAG, 0, &status );
	CHECK_ERROR( status, "Error while trying to read threshold flag value", status );

	has_flag = arg_data.isFlagSet( CACHE_NODE_FLAG, &status );
	CHECK_ERROR( status, "Error while trying to read cache node flag status", status );
	if ( !has_flag ) BUILD_ERROR( "Can't find cache node flag", MS::kInvalidParameter );
	MString path = arg_data.flagArgumentString( CACHE_NODE_FLAG, 0, &status );
	CHECK_ERROR( status, "Error while trying to read cache node flag value", status );
	status = plugs.add( path + "." + CACHE_ATTR_X );
	CHECK_ERROR( status, "Error while trying to add cache attr x to selection list", status );
	status = plugs.add( path + "." + CACHE_ATTR_Y );
	CHECK_ERROR( status, "Error while trying to add cache attr y to selection list", status );
	status = plugs.add( path + "." + CACHE_ATTR_Z );
	CHECK_ERROR( status, "Error while trying to add cache attr z to selection list", status );

	has_flag = arg_data.isFlagSet( X_FLAG, &status );
	CHECK_ERROR( status, "Error while trying to read x flag status", status );
	use_x_axis = has_flag;

	has_flag = arg_data.isFlagSet( Y_FLAG, &status );
	CHECK_ERROR( status, "Error while trying to read y flag status", status );
	use_y_axis = has_flag;
	
	has_flag = arg_data.isFlagSet( Z_FLAG, &status );
	CHECK_ERROR( status, "Error while trying to read z flag status", status );
	use_z_axis = has_flag;

	use_components = arg_data.isFlagSet( COMPONENTS_FLAG, &status );
	CHECK_ERROR( status, "Error while trying to read components flag status", status );
	components.clear();
	if ( use_components )
	{
		unsigned int count = arg_data.numberOfFlagUses( COMPONENTS_FLAG );
		components.setLength( count );
		MArgList arg_list;
		for ( unsigned int i = 0; i < count; i++ )
		{
			status = arg_data.getFlagArgumentList( COMPONENTS_FLAG, i, arg_list );
			CHECK_ERROR( status, "Error while trying to read components flag argument list", status );
			if ( arg_list.length() == 1 )
				components[i] = arg_list.asInt( 0, &status );
			else
				components[i] = arg_list.asInt( i, &status );
			CHECK_ERROR( status, "Error while trying to read components flag value", status );
		}
	}

	status = arg_data.getObjects( selected );
	CHECK_ERROR( status, "Error while retrieving selected object", status );

	return status;
}

MStatus FloodRelax::doIt( const MArgList &args )
{
	MStatus status;

	status = parseArgs( args );
	CHECK_ERROR( status, "Error while parsing arguments", status );

	if ( selected.isEmpty() ) BUILD_ERROR( "No object passed to the command or selected", MS::kInvalidParameter );

	status = plugs.getPlug( 0, cache_pos_x_plug );
	CHECK_ERROR( status, "Error while getting cache attr x plug", status );
	status = plugs.getPlug( 1, cache_pos_y_plug );
	CHECK_ERROR( status, "Error while getting cache attr y plug", status );
	status = plugs.getPlug( 2, cache_pos_z_plug );
	CHECK_ERROR( status, "Error while getting cache attr z plug", status );

	MDagPath object;
	selected.getDagPath( 0, object );
	MItMeshVertex it_vertex( object );
	MFnMesh mesh( object );
	mesh.getPoints( positions, MSpace::kObject );  // Store the positions in case of an undo
	new_positions = MPointArray( positions );
	unsigned int point_count = new_positions.length();

	MIntArray skip( point_count, 0 );
	if ( use_components )
	{
		skip = MIntArray( point_count, 1 );
		unsigned int components_count = components.length();
		for ( unsigned int i = 0; i < components_count; i++ )
			skip[components[i]] = 0;
	}

	MVectorArray position_diff( point_count );
	MPoint cache_pos, pos;
	for ( unsigned int index = 0; index < point_count; index++ )
	{
		cache_pos.x = cache_pos_x_plug[index].asDouble();
		cache_pos.y = cache_pos_y_plug[index].asDouble();
		cache_pos.z = cache_pos_z_plug[index].asDouble();

		position_diff[index] = new_positions[index] - cache_pos;
	}

	double dist;
	MIntArray neighbours;
	MVector neighbours_average;
	MVectorArray deviation_vectors( point_count );
	double max_deviation_length = 0.0;
	int prev_index = 0;
	for ( unsigned int index = 0; index < point_count; index++ )
	{
		if ( skip[index] == 1 ) continue;

		it_vertex.setIndex( index, prev_index );
		it_vertex.getConnectedVertices( neighbours );
		neighbours_average = MVector::zero;
		for ( unsigned int i = 0; i < neighbours.length(); i++ )
			neighbours_average += position_diff[neighbours[i]];
		neighbours_average /= (double) neighbours.length();
		deviation_vectors[index] = position_diff[index] - neighbours_average;
		double d = LENGTH_2( deviation_vectors[index] );
		if ( d > max_deviation_length )
			max_deviation_length = d;
	}

	MVector deviation;
	double deviation_strength;
	double threshold_2 = threshold * threshold;
	if ( max_deviation_length > 0 )
		max_deviation_length = sqrt( max_deviation_length );

	for ( unsigned int index = 0; index < point_count; index++ )
	{
		if ( skip[index] == 1 ) continue;

		dist = LENGTH_2( position_diff[index] );

		if ( dist >= threshold_2 )
		{
			pos = MPoint( new_positions[index] );

			deviation_strength = pow(deviation_vectors[index].length() / max_deviation_length, 2);

			new_positions[index] = pos - deviation_vectors[index] * deviation_strength * weight;
			if ( !use_x_axis ) new_positions[index].x = pos.x;
			if ( !use_y_axis ) new_positions[index].y = pos.y;
			if ( !use_z_axis ) new_positions[index].z = pos.z;
		}
	}

	return redoIt();
}

MStatus FloodRelax::redoIt()
{
	MStatus status;
	MDagPath object;
	selected.getDagPath( 0, object );
	MFnMesh mesh( object );
	mesh.setPoints( new_positions, MSpace::kObject );

	return status;
}

MStatus FloodRelax::undoIt()
{
	MStatus status;
	MDagPath object;
	selected.getDagPath( 0, object );
	MFnMesh mesh( object );
	mesh.setPoints( positions, MSpace::kObject );

	return status;
}