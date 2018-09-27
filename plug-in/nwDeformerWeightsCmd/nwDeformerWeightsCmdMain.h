//
// Copyright (C)
//
// File: nwDeformerWeightsCmdMain.h
//
// Author: Mathias Capdet
//
#pragma once

#include <algorithm>
#include <maya/MPxCommand.h>
#include <maya/MSyntax.h>
#include <maya/MString.h>
#include <maya/MGlobal.h>
#include <maya/MArgDatabase.h>
#include <maya/MArgList.h>
#include <maya/MSelectionList.h>
#include <maya/MPlug.h>
#include <maya/MFnDependencyNode.h>
#include <maya/MDagPath.h>
#include <maya/MFnComponent.h>
#include <maya/MFnSingleIndexedComponent.h>
#include <maya/MFnDoubleIndexedComponent.h>
#include <maya/MFnTripleIndexedComponent.h>
#include <maya/MFnMesh.h>
#include <maya/MFnNurbsSurface.h>
#include <maya/MFnLattice.h>
#include <maya/MFnGeometryFilter.h>

#include "nwDeformerWeightsCmd.h"