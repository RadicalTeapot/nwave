#include "nwMirrorModelerMain.h"

using namespace nwave;

KdTree::KdTree(void) : root( NULL ), dimensions( 3 )
{
}

KdTree::~KdTree(void)
{
	if ( root != NULL )
		delete root;
}

void KdTree::build( MPointArray points, MIntArray ids )
{
	if ( root != NULL )
		delete root;

	pointCount = points.length();
	pointList.clear();
	pointList.resize( pointCount );
	// Fill the point list with point positions and ids
	for ( PointList::size_type i = 0; i < pointCount; i++ )
	{
		std::pair<MPoint, IdPoint> pair;
		pair.first = MPoint( points[(unsigned int) i] );
		if ( ids.length() == pointCount )
			pair.second = IdPoint( ids[(unsigned int) i] );
		else if ( ids.length() == pointCount * 2 )
			pair.second = IdPoint( ids[(unsigned int) i*2], ids[(unsigned int) i*2+1] );
		else if ( ids.length() == pointCount * 3 )
			pair.second = IdPoint( ids[(unsigned int) i*3], ids[(unsigned int) i*3+1], ids[(unsigned int) i*3+2] );
		pointList[i] = pair;
	}

	root = buildKdTree( pointList.begin(), pointList.end() );
}

KdTree::Node *KdTree::buildKdTree( PointIterator begin, PointIterator end, unsigned int depth, Node *currentNode )
{
	if ( begin == end )
		return NULL;

	unsigned int axis = depth % dimensions;

	switch (axis)
	{
	case 0 : std::sort( begin, end, SortX() ); break;
	case 1 : std::sort( begin, end, SortY() ); break;
	case 2 : std::sort( begin, end, SortZ() ); break;
	default :
		return NULL;
		break;
	}

	PointList::size_type half = (end - begin) / 2;

	Node *newNode = new Node( *(begin + half), depth );
	newNode->setParent( currentNode );
	if ( begin != ( begin + half ) )
		newNode->setLeftChild( buildKdTree( begin, begin + half, depth+1, newNode) );
	if ( end != ( begin + half + 1 ) )
		newNode->setRightChild( buildKdTree( begin + half + 1, end, depth+1, newNode ) );

	return newNode;
}

KdTree::Node *KdTree::nearestNeighbour( Node *node, const MPoint position )
{
	if ( node == NULL )
		return NULL;

	Node *leaf = traverseTree( node, position );
	MVector diff = (leaf->point - position);
	double dist = pow(diff[0], 2) + pow(diff[1], 2) + pow(diff[2], 2);

	if ( leaf->point == position )
		return leaf;

	node = leaf;
	Node *nearest = leaf;
	while ( node->parent != NULL )
	{
		nearest = checkSubtree( node->parent, position, nearest, dist );
		node = node->parent;
	}

	return nearest;
}

KdTree::Node *KdTree::checkSubtree( Node *node, const MPoint position, Node *nearest, double &minDist )
{
	if ( node == NULL )
		return NULL;

	MVector diff = (node->point - position);
	double dist = pow(diff[0], 2) + pow(diff[1], 2) + pow(diff[2], 2);

	if ( dist < minDist )
	{
		minDist = dist;
		nearest = node;
	}

	unsigned int axis = node->depth % dimensions;

	double d = position[axis] - node->point[axis];

	if ( (d * d) > minDist )
	{
		if ( d <= 0 && node->leftChild != NULL )
			nearest = checkSubtree( node->leftChild, position, nearest, minDist );
		else if ( d > 0 && node->rightChild != NULL )
			nearest = checkSubtree( node->rightChild, position, nearest, minDist );
	}
	else
	{
		if ( node->leftChild != NULL )
			nearest = checkSubtree( node->leftChild, position, nearest, minDist );
		if ( node->rightChild != NULL )
			nearest = checkSubtree( node->rightChild, position, nearest, minDist );
	}

	return nearest;
}

KdTree::Node *KdTree::traverseTree( Node *currentNode, const MPoint position )
{
	if ( currentNode == NULL )
		return NULL;

	if ( !currentNode->isLeaf() )
	{
		Node *child = NULL;

		unsigned int axis = currentNode->depth % dimensions;

		double d = position[axis] - currentNode->point[axis];

		if ( d <= 0 && currentNode->leftChild != NULL )
			return traverseTree( currentNode->leftChild, position );
		else if ( d > 0 && currentNode->rightChild != NULL )
			return traverseTree( currentNode->rightChild, position );
	}
	return currentNode;
}

KdTree::Node *KdTree::nearestNode( const MPoint position )
{
	return nearestNeighbour( root, position );
}