#pragma once

#include <maya/MPxCommand.h>
#include <maya/MStatus.h>
#include <maya/MSyntax.h>
#include <maya/MArgDatabase.h>
#include <maya/MVector.h>
#include <maya/MPointArray.h>
#include <maya/MGlobal.h>
#include <maya/MSelectionList.h>
#include <maya/MDagPath.h>
#include <maya/MFnDependencyNode.h>
#include <maya/MFnMesh.h>
#include <maya/MFnNurbsCurve.h>
#include <maya/MFnNurbsSurface.h>
#include <maya/MFnLattice.h>
#include <maya/MIntArray.h>
#include <maya/MArgList.h>
#include <maya/MItGeometry.h>
#include <maya/MDoubleArray.h>
#include <maya/MString.h>
#include <maya/MPlug.h>
#include <maya/MItMeshVertex.h>

#include <vector>
#include <algorithm>
#include <iostream>
#include <ctime>
#include <utility>

#include "KdTree.h"
#include "GetMirrorVerticesIndex.h"
#include "GetSetPointsCmd.h"
#include "FloodRelax.h"