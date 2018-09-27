//
// Copyright (C) 
//
// Plugin Name : nwMirrorModeler
// 
// File: GetMirrorVerticesIndex.h
//
// Command: getMirrorVerticesIndex
//
// Author: Mathias Capdet
//
#pragma once

namespace nwave{

class GetMirrorVerticesIndex : public MPxCommand{
	private :
		// Enumerate the mirror modes for the nearest neighbour search
		enum MirrorMode
		{
			NONE,
			MIRROR_X,
			MIRROR_Y,
			MIRROR_Z
		};

		// Enumerate the type of objects that can be used by the command
		enum ObjectType
		{
			NO_TYPE,
			MESH,
			NURBS_CURVE,
			NURBS_SURFACE,
			LATTICE
		};

		// Store whether the search is to be done in world space
		bool useWorldspace;
		// Store whether the search is in position mode
		bool usePosition;
		// Store whether the search is in mirror mode
		bool useMirror;
		// Store the position to search for the nearest neighbour search
		MPoint searchPosition;
		// Store the mirror mode for the nearest neighbour search
		MirrorMode mirrorMode;
		// Store the type of object passed to the command
		ObjectType objectType;
		// Store the position of the mirror axis
		MPoint mirrorPosition;
		// Store the threshold value for nearest neighbour search
		double threshold;
		// Store whether the user used the help flag
		bool helpFlagSet;
		// Store the objects passed to the command
		MSelectionList objectSelectionList;
		// Store the quad tree
		KdTree *tree;
		// Store the points
		MPointArray points;

		unsigned int dimensionX, dimensionY, dimensionZ;

	public :
		// Initialize the command class
		GetMirrorVerticesIndex();
		// Destroy the command class
		virtual ~GetMirrorVerticesIndex();
		// Create the command class
		static void *creator();
		
		// Declare the syntax for the command
		static MSyntax newSyntax();
		// Set the command undoable state
		bool isUndoable() const;
		// Parse the flags passed to the command from Maya
		MStatus parseArgs( const MArgList &args );
		
		// Set the class vars and build the tree
		MStatus doIt( const MArgList &args );
		// Do the search
		MStatus redoIt();

		// Do a mirror position search
		MStatus mirrorSearch( MIntArray &mirrorIds );
};

}