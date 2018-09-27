//
// Copyright (C) 
//
// Plugin Name : nwMirrorModeler
// 
// File: KdTree.h
//
// Author: Mathias Capdet
//
#pragma once

namespace nwave {

class KdTree
{
public :
	// The structure representing a point id
    struct IdPoint
    {
        unsigned int x;
        unsigned int y;
        unsigned int z;
		unsigned int size;
		IdPoint() : x(0), y(0), z(0), size(0)
		{};
		IdPoint(unsigned int x) : x(x), y(0), z(0), size(1)
        {};
        IdPoint(unsigned int x, unsigned int y) : x(x), y(y), z(0), size(2)
        {};
        IdPoint(unsigned int x, unsigned int y, unsigned int z) : x(x), y(y), z(z), size(3)
        {};		
    };

	// The structure representing a kd-tree node
	struct Node
	{
		unsigned int depth;
		MPoint point;
		IdPoint id;

		Node *leftChild;
		Node *rightChild;
		Node *parent;

		Node(std::pair<MPoint, IdPoint> pair, unsigned int depth) : point( pair.first ), id( pair.second ), leftChild( NULL ), 
			rightChild( NULL ), parent( NULL ), depth( depth )
		{};
		void setLeftChild(Node *left) { leftChild = left; };
		void setRightChild(Node *right) { rightChild = right; };
		void setParent(Node *parentNode) { parent = parentNode; };
		inline bool hasLeftChild() { return (leftChild != NULL); };
		inline bool hasRightChild() { return (rightChild != NULL); };
		inline bool isLeaf() { return (!hasLeftChild() && !hasRightChild()); };
		inline bool isRoot() { return (!parent); };
	};
protected :
	// The PointList type definition
	typedef std::vector<std::pair<MPoint, IdPoint>> PointList;
	// The PointIterator type definition
	typedef PointList::iterator PointIterator;

	// The structure for sorting points based on their x coordinate
	struct SortX
	{
		bool operator() (std::pair<MPoint, IdPoint> pointA, std::pair<MPoint, IdPoint> pointB) { return pointA.first.x < pointB.first.x; };
	};
	// The structure for sorting points based on their y coordinate
	struct SortY
	{
		bool operator() (std::pair<MPoint, IdPoint> pointA, std::pair<MPoint, IdPoint> pointB) { return pointA.first.y < pointB.first.y; };
	};
	// The structure for sorting points based on their z coordinate
	struct SortZ
	{
		bool operator() (std::pair<MPoint, IdPoint> pointA, std::pair<MPoint, IdPoint> pointB) { return pointA.first.z < pointB.first.z; };
	};

	// Store the point count
	PointList::size_type pointCount;
	// Store the point list
	PointList pointList;
	// Store the number of dimensions
    unsigned int dimensions;

	// Build the kd-tree
	Node *buildKdTree( PointIterator begin, PointIterator end, unsigned int depth = 0, Node *currentNode = NULL );
	// Do a nearest neighbour search
	Node *nearestNeighbour( Node *node, const MPoint position );
	// Look into subtree for hyperplanes non checked
	Node *checkSubtree( Node *node, const MPoint position, Node *nearest, double &minDist );
	// Traverse the tree until the bottom, choosing a path based on the search position
	Node *traverseTree( Node *currentNode, const MPoint position );
public:

	KdTree(void);
	~KdTree(void);

	// Return whether the tree is constructed
	inline bool isBuilt() { return root != NULL; };
	// Build the tree
	void build( MPointArray points, MIntArray ids );
	// Get the closest point
	Node *nearestNode( const MPoint position );

	// Store the kd tree root node
	Node *root;
};

}