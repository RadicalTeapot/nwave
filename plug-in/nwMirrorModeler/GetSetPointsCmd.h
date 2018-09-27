//
// Copyright (C) 
//
// Plugin Name : nwMirrorModeler
// 
// File: GetSetPointsCmd.h
//
// Command: getSetPoints
//
// Author: Mathias Capdet
//
#pragma once

namespace nwave{

class GetSetPointsCmd : public MPxCommand{
	private :
		// Enumerate the possible command states
		enum CommandState 
		{
			GET,
			SET
		};

		// Store the space in which to do the mesh operations
		MSpace::Space space;
		// Store whether the help flag is set
		bool helpFlagSet;
		// Store the positions to get/set
		MPointArray points;
		// Stroe the non-modified points positions
		MPointArray nonModifiedPoints;
		// Store the command state
		CommandState state;
		// Store the object dagPath
		MDagPath objectDagPath;

	public :
		// Initialize the command class
		GetSetPointsCmd();
		// Destroy the command class
		virtual ~GetSetPointsCmd();
		// Create the command class
		static void *creator();
		
		// Declare the syntax for the command
		static MSyntax newSyntax();
		// Set the command undoable state
		bool isUndoable() const;
		// Parse the flags passed to the command from Maya
		MStatus parseArgs( const MArgList &args );
		
		// Set the class vars
		MStatus doIt( const MArgList &args );
		// Do the get/set
		MStatus redoIt();
		// Undo the get/set
		MStatus undoIt();
};

}