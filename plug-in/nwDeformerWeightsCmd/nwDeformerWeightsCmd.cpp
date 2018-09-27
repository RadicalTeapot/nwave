//
// Copyright (C)
//
// File: nwDeformerWeightsCmd.cpp
//
// Author: Mathias Capdet
//
#include "nwDeformerWeightsCmdMain.h"

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

#define SOURCE_FLAG "-so"
#define SOURCE_LONG_FLAG "-source"
#define DESTINATION_FLAG "-de"
#define DESTINATION_LONG_FLAG "-destination"
#define MULTIPLY_FLAG "-m"
#define MULTIPLY_LONG_FLAG "-multiply"
#define COMPLEMENT_FLAG "-c"
#define COMPLEMENT_LONG_FLAG "-complement"
#define SET_FLAG "-sv"
#define SET_LONG_FLAG "-setValues"
#define SET_MEL_FLAG "-svm"
#define SET_MEL_LONG_FLAG "-setValuesMel"

using namespace nwave;

const MString nwDeformerWeightsCmd::command_name( "deformerWeightsTools" );

nwDeformerWeightsCmd::nwDeformerWeightsCmd() : is_query( false ), multiply_mode( false ), complement_mode( false ), set_mode( false ), use_source( false )
{
}


nwDeformerWeightsCmd::~nwDeformerWeightsCmd()
{
}

void *nwDeformerWeightsCmd::creator()
{
	return new nwDeformerWeightsCmd();
}

bool nwDeformerWeightsCmd::isUndoable() const
{
	return !is_query;
}

MSyntax nwDeformerWeightsCmd::newSyntax()
{
	MSyntax syntax;
	MStatus status;

	status = syntax.addFlag( SOURCE_FLAG, SOURCE_LONG_FLAG, MSyntax::kString );
	CHECK_ERROR( status, "Error while adding source flag", syntax );

	status = syntax.addFlag( DESTINATION_FLAG, DESTINATION_LONG_FLAG, MSyntax::kString );
	CHECK_ERROR( status, "Error while adding destination flag", syntax );
	status = syntax.makeFlagQueryWithFullArgs( DESTINATION_FLAG, false );
	CHECK_ERROR( status, "Error while setting destination query state", syntax );

	status = syntax.addFlag( MULTIPLY_FLAG, MULTIPLY_LONG_FLAG, MSyntax::kDouble );
	CHECK_ERROR( status, "Error while adding multiply flag", syntax );

	status = syntax.addFlag( COMPLEMENT_FLAG, COMPLEMENT_LONG_FLAG );
	CHECK_ERROR( status, "Error while adding complement flag", syntax );

	status = syntax.addFlag( SET_FLAG, SET_LONG_FLAG, MSyntax::kString );
	CHECK_ERROR( status, "Error while adding set flag", syntax );
	/*
	status = syntax.addFlag( SET_FLAG, SET_LONG_FLAG, MSyntax::kDouble );
	CHECK_ERROR( status, "Error while adding set flag", syntax );
	status = syntax.makeFlagMultiUse( SET_FLAG );
	CHECK_ERROR( status, "Error while making set flag multi-use", syntax );
	*/
	status = syntax.addFlag( SET_MEL_FLAG, SET_MEL_LONG_FLAG );
	CHECK_ERROR( status, "Error while adding set mel flag", syntax );

	// Set the command to use the selection if no object name is passed to it
	syntax.useSelectionAsDefault( true );
	// Set the maximum object count to 1
	status = syntax.setObjectType( MSyntax::MObjectFormat::kSelectionList, 0 );
	CHECK_ERROR( status, "Error while setting command object type flag", syntax );

	syntax.enableQuery( true );
	syntax.enableEdit( false );

	return syntax;
}

MStatus nwDeformerWeightsCmd::parseArgs( const MArgList &args )
{
	MStatus status;
	MArgDatabase argData( syntax(), args );

	is_query = argData.isQuery( &status );
	CHECK_ERROR( status, "Error while reading query flag state", status );

	bool use_destination = argData.isFlagSet( DESTINATION_FLAG, &status );
	CHECK_ERROR( status, "Error while reading destination flag state", status );
	if ( !use_destination )
	{
		MGlobal::displayError( "Destination flag not set" );
		return MStatus::kInvalidParameter;
	}
	MString deformed_attribute = argData.flagArgumentString( DESTINATION_FLAG, 0, &status );
	CHECK_ERROR( status, "Error while getting the destination attribute value.", status );

	MSelectionList sel_list;
	sel_list.add( deformed_attribute );
	sel_list.getPlug( 0, destination_plug );
	CHECK_ERROR( status, "Error while getting the destination attribute.", status );

	use_source = argData.isFlagSet( SOURCE_FLAG, &status );
	CHECK_ERROR( status, "Error while reading source flag state", status );
	if ( use_source )
	{
		sel_list.clear();
		deformed_attribute = argData.flagArgumentString( SOURCE_FLAG, 0, &status );
		CHECK_ERROR( status, "Error while getting the source attribute value.", status );

		sel_list.add( deformed_attribute );
		sel_list.getPlug( 0, source_plug );
		CHECK_ERROR( status, "Error while getting the source attribute.", status );
	}

	multiply_mode = argData.isFlagSet( MULTIPLY_FLAG, &status );
	CHECK_ERROR( status, "Error while reading multiply flag state", status );
	if ( multiply_mode )
	{
		multiply_value = argData.flagArgumentDouble( MULTIPLY_FLAG, 0, &status );
		CHECK_ERROR( status, "Error while reading multiply flag value", status );
	}

	complement_mode = argData.isFlagSet( COMPLEMENT_FLAG, &status );
	CHECK_ERROR( status, "Error while reading complement flag state", status );

	set_mode = argData.isFlagSet( SET_FLAG, &status );
	CHECK_ERROR( status, "Error while reading set flag state", status );
	if ( set_mode )
	{
		MString value = argData.flagArgumentString( SET_FLAG, 0, &status );
		CHECK_ERROR( status, "Error while reading set flag value", status );
		MStringArray split;
		value.split( ' ', split );
		set_values.clear();
		for ( unsigned int i = 0; i < split.length(); i++ )
		{
			status = set_values.append( split[i].asDouble() );
			CHECK_ERROR( status, "Error while parsing set flag values", status );
		}
	}

	/*
	MArgParser parser( this->syntax(), args, &status );
	unsigned int set_values_count = parser.numberOfFlagUses( SET_FLAG );
	set_mode = ( set_values_count > 0 );

	if ( set_mode )
	{
		set_values.clear();
		for ( unsigned int i = 0; i < set_values_count; i++ )
		{
			MArgList arg_list;
			status = parser.getFlagArgumentList( SET_FLAG, i, arg_list );
			CHECK_ERROR( status, "Error while reading set flag value at index " + i, status );
			set_values.append( arg_list.asDouble( 0, &status ) );
			CHECK_ERROR( status, "Error while appending set flag value at index " + i, status );
		}
	}

	if ( !set_mode )
	{
		unsigned int flag_index = args.flagIndex( SET_MEL_FLAG, SET_MEL_LONG_FLAG );
		set_mode = ( flag_index != MArgList::kInvalidArgIndex );
		if ( set_mode )
		{
			set_values.clear();

			flag_index++;
			status = args.get( flag_index, set_values );
			CHECK_ERROR( status, "Error while get set mel flag values", status );
		}
	}
	*/

	component_ids.clear();

	// Get the objects passed to the command
	sel_list.clear();
	status = argData.getObjects( sel_list );
	CHECK_ERROR( status, "Error while getting the object.", status );

	if ( sel_list.length() > 0 )
	{
		MDagPath dag_path;
		MObject components_object;
		
		components_count = 0;

		for ( unsigned int sel_list_index = 0; sel_list_index < sel_list.length(); sel_list_index++ )
		{
			sel_list.getDagPath( sel_list_index, dag_path, components_object );
			CHECK_ERROR( status, "Error while getting object components.", status );

			unsigned int count = 0;

			if ( components_object.hasFn( MFn::kSingleIndexedComponent ) )
			{
				component_type = MFn::kSingleIndexedComponent;
				MFnSingleIndexedComponent components( components_object, &status );
				CHECK_ERROR( status, "Error while getting object single index components ids.", status );
				count = components.elementCount();

				if ( count > 0 )
				{
					MIntArray ids;
					status = components.getElements( ids );
					CHECK_ERROR( status, "Error while getting object single index components ids list.", status );

					for ( unsigned int i = 0; i < count; i++ )
						component_ids.append( ids[i] );
				}
			}
			else if ( components_object.hasFn( MFn::kDoubleIndexedComponent ) )
			{
				component_type = MFn::kDoubleIndexedComponent;
				MFnDoubleIndexedComponent components( components_object, &status );
				CHECK_ERROR( status, "Error while getting object double index components ids.", status );
				count = components.elementCount();

				if ( count > 0 )
				{
					MFnNurbsSurface nurbs( dag_path );
					unsigned int max_v = nurbs.numCVsInV();

					MIntArray u, v;
					status = components.getElements( u, v );
					CHECK_ERROR( status, "Error while getting object double index components indices lists.", status );

					for ( unsigned int i = 0; i < count; i++ )
						component_ids.append( v[i] + u[i] * max_v );
				}
			}
			else if ( components_object.hasFn( MFn::kTripleIndexedComponent ) )
			{
				component_type = MFn::kTripleIndexedComponent;
				MFnTripleIndexedComponent components( components_object, &status );
				CHECK_ERROR( status, "Error while getting object triple index components ids.", status );
				count = components.elementCount();

				if ( count > 0 )
				{
					MFnLattice lattice( dag_path );
					unsigned int max_s, max_t, max_u;
					lattice.getDivisions( max_s, max_t, max_u );

					MIntArray s, t, u;
					status = components.getElements( s, t, u );
					CHECK_ERROR( status, "Error while getting object single index components ids list.", status );

					for ( unsigned int i = 0; i < count; i++ )
						component_ids.append( u[i] + t[i] * max_u + s[i] * max_u * max_t );
				}
			}

			components_count += count;
		}

		if ( components_count == 0 )
		{
			// No components where selected, pass the whole geo components to the arrays
			if ( dag_path.hasFn( MFn::kMesh ) )
			{
				MFnMesh mesh( dag_path );

				components_count = mesh.numVertices();
			}
			else if ( dag_path.hasFn( MFn::kNurbsSurface ) )
			{
				MFnNurbsSurface nurbs( dag_path );
				unsigned int max_u = nurbs.numCVsInV();
				unsigned int max_v = nurbs.numCVsInV();

				components_count = max_u * max_v;
			}
			else if ( dag_path.hasFn( MFn::kLattice ) )
			{
				MFnLattice lattice( dag_path );
				unsigned int max_s, max_t, max_u;
				lattice.getDivisions( max_s, max_t, max_u );

				components_count = max_s * max_t * max_u;
			}
			else
			{
				MGlobal::displayError( "Wrong object type passed/selected, aborting." );
				return MStatus::kInvalidParameter;
			}

			for ( unsigned int i = 0; i < components_count; i++ )
				component_ids.append( i );
		}
	}
	else
	{
		// Split the destination string on the '.' character to extract the deformer name and deformed geo index
		MStringArray destination_split_data;
		status = deformed_attribute.split( '.', destination_split_data );
		CHECK_ERROR( status, "Error while extracting data from destination attribute value.", status );

		// Get the deformed index geo from the splitted destination string
		MStringArray index_array;
		status = destination_split_data[1].split( '[', index_array );
		CHECK_ERROR( status, "Error while extracting deformed geometry index from destination attribute value.", status );
		unsigned int deformed_index = index_array[0].substring( 0, index_array[0].length() - 1 ).asUnsigned();

		// Build the geometry filter from the splitted destination string
		sel_list.clear();
		sel_list.add( destination_split_data[0] );
		MObject deformer_object;
		status = sel_list.getDependNode( 0, deformer_object );
		CHECK_ERROR( status, "Error while getting the deformer object.", status );
		MFnGeometryFilter deformer( deformer_object, &status );
		CHECK_ERROR( status, "Error while getting the deformer geometry filter.", status );

		// Get the object corresponding to the deformed geo
		MObject deformed_object = deformer.outputShapeAtIndex( deformed_index, &status );
		CHECK_ERROR( status, "Error while getting the deformer object at index " + deformed_index, status );

		// No components where selected, pass the whole geo components to the arrays
		if ( deformed_object.hasFn( MFn::kMesh ) )
		{
			MFnMesh mesh( deformed_object );

			components_count = mesh.numVertices();
		}
		else if ( deformed_object.hasFn( MFn::kNurbsSurface ) )
		{
			MFnNurbsSurface nurbs( deformed_object );
			unsigned int max_u = nurbs.numCVsInV();
			unsigned int max_v = nurbs.numCVsInV();

			components_count = max_u * max_v;
		}
		else if ( deformed_object.hasFn( MFn::kLattice ) )
		{
			MFnLattice lattice( deformed_object );
			unsigned int max_s, max_t, max_u;
			lattice.getDivisions( max_s, max_t, max_u );

			components_count = max_s * max_t * max_u;
		}
		else
		{
			MGlobal::displayError( "Wrong object type passed/selected, aborting." );
			return MStatus::kInvalidParameter;
		}

		for ( unsigned int i = 0; i < components_count; i++ )
			component_ids.append( i );
	}

	return MS::kSuccess;
}

MStatus nwDeformerWeightsCmd::doIt( const MArgList &args )
{
	MStatus status;

	status = parseArgs( args );
	CHECK_ERROR( status, "Error while parsing flags", status );

	// Flag compatibilty checks
	if ( use_source && set_mode )
	{
		MGlobal::displayError( "Cannot use both set and source flag at the same time." );
		return MStatus::kSuccess;
	}

	if ( complement_mode && set_mode )
	{
		MGlobal::displayError( "Cannot use both set and complement flag at the same time." );
		return MStatus::kSuccess;
	}

	if ( !use_source && multiply_mode )
	{
		MGlobal::displayError( "Cannot use multiply flag without source flag" );
		return MStatus::kSuccess;
	}

	if ( components_count == 0 )
	{
		MGlobal::displayError( "No components found for the passed deformer." );
		return MStatus::kSuccess;
	}

	if ( set_mode && set_values.length() != components_count )
	{
		MGlobal::displayError( "Invalid number of weights provided for set mode." );
		return MStatus::kSuccess;
	}

	if ( use_source )
	{
		source_weights.clear();
		source_weights.setLength( components_count );
		for ( unsigned int i = 0; i < components_count; i++ )
			source_weights[i] = source_plug.elementByLogicalIndex( component_ids[i] ).asFloat();
	}

	previous_weights.clear();
	previous_weights.setLength( components_count );
	for ( unsigned int i = 0; i < components_count; i++ )
	{
		int index = component_ids[i];
		double value = destination_plug.elementByLogicalIndex( index ).asDouble();
		previous_weights[i] = value;
	}

	return redoIt();
}

MStatus nwDeformerWeightsCmd::redoIt()
{
	clearResult();
	if ( is_query )
	{
		setResult( previous_weights );
	}
	else
	{
		MDoubleArray weights( previous_weights );
		if ( use_source )
			weights = MDoubleArray( source_weights );

		if ( multiply_mode )
		{
			for ( unsigned int i = 0; i < components_count; i++ )
				weights[i] = previous_weights[i] * std::max(1.0 - multiply_value, 0.) + weights[i] * multiply_value;
		}

		if ( complement_mode )
		{
			for ( unsigned int i = 0; i < components_count; i++ )
				weights[i] = 1.0 - weights[i];
		}

		if ( set_mode )
		{
			for ( unsigned int i = 0; i < components_count; i++ )
				weights[i] = set_values[i];
		}

		for ( unsigned int i = 0; i < components_count; i++ )
			destination_plug.elementByLogicalIndex( component_ids[i] ).setDouble( weights[i] );
	}

	return MS::kSuccess;
}

MStatus nwDeformerWeightsCmd::undoIt()
{
	for ( unsigned int i = 0; i < components_count; i++ )
	{
		int index = component_ids[i];
		double value = previous_weights[i];
		destination_plug.elementByLogicalIndex( index ).setDouble( value );
	}

	return MS::kSuccess;
}