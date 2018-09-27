//
// Copyright (C) 
//
// Plugin Name : nwMirrorModeler
// 
// File: FloodRelax.h
//
// Command: floodRelax
//
// Author: Mathias Capdet
//
#pragma once

namespace nwave {

	class FloodRelax : public MPxCommand
	{
	public:
		FloodRelax();
		virtual ~FloodRelax();
		static void *creator();
		static MSyntax newSyntax();
		bool isUndoable() const;
		MStatus parseArgs( const MArgList &args );
		MStatus doIt( const MArgList &args );
		MStatus redoIt();
		MStatus undoIt();

	private :
		double weight;
		double threshold;
		bool use_x_axis;
		bool use_y_axis;
		bool use_z_axis;
		MSelectionList plugs;
		MPlug cache_pos_x_plug, cache_pos_y_plug, cache_pos_z_plug;
		MSelectionList selected;
		MPointArray positions;
		MPointArray new_positions;
		bool use_components;
		MIntArray components;
	};
}