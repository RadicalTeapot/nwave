//
// Copyright (C)
//
// File: nwDeformerWeightsCmd.h
//
// Author: Mathias Capdet
//
#pragma once

namespace nwave {

	class nwDeformerWeightsCmd : public MPxCommand
	{
	public:
		nwDeformerWeightsCmd();
		virtual ~nwDeformerWeightsCmd();
		static void *creator();
		static MSyntax newSyntax();
		bool isUndoable() const;
		MStatus parseArgs( const MArgList &args );
		MStatus doIt( const MArgList &args );
		MStatus redoIt();
		MStatus undoIt();

		const static MString command_name;

		bool is_query;

		bool multiply_mode;
		double multiply_value;

		bool complement_mode;

		bool set_mode;
		MDoubleArray set_values;

		bool use_source;
		MPlug source_plug;
		MDoubleArray source_weights;
		
		MPlug destination_plug;

		MDoubleArray previous_weights;

		unsigned int components_count;
		MIntArray component_ids;

		MFn::Type component_type;
	};
}