# -*- coding: utf-8 -*-
"""
Created on Mon Apr 10 10:42:39 2017

@author: Emanuele

Binary Tree to deal with the routes, their expansions, their cost calculations
"""

import numpy as np;


#class Node that defines the nodes in the binary tree
#it hase the following attributes
#left, right: the left and right parents of the node
#parent: the parent of the node
#cost: the cost associated to the route that leads to that node(e.g. if the node is the path described by a route that covers t1,t3,t4, it will contain the cost associated to that route)
#height: the height of the node in the tree
#isLeaf: it is used to see if the node is a leaf
class Node(object):
    def __init__(self, left, right, parent, cost, height, isLeaf):
        self.left = left;
        self.right = right;
        self.parent = parent;
        self.cost = cost;
        self.height = height;
        self.isleaf = isLeaf;
    def getLeft(self):
        return self.left;
    def getRight(self):
        return self.right;
    def getParent(self):
        return self.parent;
    def getCost(self):
        return self.cost;
    def getHeight(self):
        return self.height;
    def isLeaf(self):
        return self.isLeaf;
    def setCost(self, cost):
        self.cost = cost;
    #all the other setters to be completed...
        #...
        #...
    
#class that defines the binary tree 
#it has as elements a root which is the root of the tree (it corresponds to a "virtual" vertex on G where the cost of moving from that node to every
    #node on G is 0). This trick is used to take into consideration the case where the initial vertex is a target itself: so it could be a covering route of some kind.
class BTree(object):
    def __init__(self):
        self.root = None;
        self.SP_cost = np.array([]);
    def getShortestPaths(self, SP):
        self.SP_cost = np.array(SP);
    #search in the tree if the route v we have found has a cost which
    #is higher than one which is present in the tree, returns 1, 0 otherwise
    #in the first case the route we passed to the function is better than the previous one stored
    #in the tree, so we will update() the tree acoordingly to the new route, otherwise nothing happens
    def search(self, cost, v):
        node = self.root;    
        for i in v:
            if i==1:
                node = node.right;
                if node is None:
                    return False;
            else:
                node = node.left;
                if node is None:
                    return True;
        if cost<node.getCost():
            node.setCost(cost);
            return True;
        else:
            return False;

    #update function: it updates the btree used to store the routes    
    #we go down through the tree and update a route
    #if the last target in the route is covered, build a new tree from that point on where the root is the new
    #target, and its cost is the sum of the previous route's cost plus the shortest path from 
    #prevoius vertex to this new one
    #if the target is not covered, just create a new tree on the right where the new cost is
    #the provious cost of the route (a general case of stand still for D wrt a target)
    #oldroute is the non-ordered route, used to calculate its cost (which is dependent on the targets' order obviously)
    def update(self, route, targets, node, v, oldroute):
        #print(targets[0]);
        #print(route[0]);
        if self.root is None: #if the tree is empty, create the first node
            #print("create");
            route = np.sort(route);
            targets = np.sort(targets);
            self.root = Node(None, None, None, 0, 0, False);
            node = self.root;
        if v[0]==1:
            if node.right is None:
                #print("right create");
                node.right = Node(None, None, node, calculateCostOfRoute(oldroute, self.SP_cost), node.getHeight()+1, True);
                #print("Cost of the route ",oldroute," is ", calculateCostOfRoute(oldroute, self.SP_cost));                
                node.isleaf = False;#if we insert a new target on a route, the previous one is not still a route (or at least is strictly dominated)
                return; #we assume that we call this function at each iteration (i.e. every time we update a route in the tree, we can at most extend it with one element)
            else:#it exists a route that covers that target, so let's go down the tree
                #print("right go down");
                return self.update(route[1:], targets[1:], node.right,v[1:],oldroute);
        else:
            if node.left is None: #in this case a target is not covered by a route, but another one which comes after that one (wrt the order imposed at the beginning on T) is so
                #print("left create");                
                node.left = Node(None, None, node, node.getCost(), node.getHeight()+1, False);
                node.isleaf = False;
                return self.update(route, targets[1:], node.left, v[1:],oldroute);
            else:# in this case a route that does not cover a target already exists (but for sure that route will cover at most another target which comes after in T)
                #print("left go down");                
                return self.update(route, targets[1:], node.left,v[1:],oldroute);
            
                
                
#transform a route into a binary vector where each entry v[i] is 1 if the corresponding
#target in T[i] is covered by r, 0 otherwise.
#take as input the route r (which is a vector!) and the targets T in topological order (wrt Vertex.vertex_number)
#returns the binary vector v as defined above
def binaryVectorFromRoute(r, T):
    i=0;
    r = np.sort(r);
    T = np.sort(T);
    v = np.array([]);
    for t in range(len(T)):
        if T[t] in r:
            v = np.append(v,1);
            i+=1;
        else:
            v = np.append(v,0);
    return v.astype(int);
    
    
#create a 'purged' version of the binaryVectorFromRoute:
# i.e. delete all the terminal zeros in the end of the vector
# it is used to search in the tree for routes that are already in
def purgeBinaryVector(v):
    v = v[::-1];
    for i in range(len(v)):
        if v[i]==0:
            v = np.delete(v,i);
        else:
            return v[::-1];
            
#given a route as an ordered set of targets, calculate the cost of the shortest path that covers all the target inside in it            
def calculateCostOfRoute(route, SP_cost):
    cost = 0;
    for r in range(0,len(route)-1):
        cost += SP_cost[route[r]][route[r+1]];
    return cost;



"""
Little testing to see if the algorithms works as expected
"""    
#create the tree
bt = BTree();
#get the shortest path matrix 
bt.getShortestPaths([[0,1,1],[1,0,1],[1,1,0]]);
#this is how you can create a new path
#first inizialize the binary vector route-targets
#then call the update tree function
v = np.array(binaryVectorFromRoute([0],[0,1,2])); #route that covers just target 0
bt.update([0],[0,1,2],bt.root,v,[0]);#update the tree
v = np.array(binaryVectorFromRoute([0,2],[0,1,2])); #route that covers targets 0,2
bt.update([0,2],[0,1,2],bt.root,v,[0,2]);#update the tree, its cost should be 2 (according to SP matrix defined previously)


v1 = np.array(binaryVectorFromRoute([0,2],[0,1,2]));#create the route that covers 0,2. It is present in the tree
v2 = np.array(binaryVectorFromRoute([0,1],[0,1,2]));#create the route that covers 0,1. It is not present in the tree
 
  
print(bt.search(1, purgeBinaryVector(v1)));#we see if there a route that covers 0,2 with a cost lower than 1(e.g. 0), we expect that there's not such a route(i.e. in the tree there's a better route)
print(bt.search(0, purgeBinaryVector(v1)));#we see if there a route that covers 0,2 with a cost lower than 0(e.g. -1), we expect that there's such a route (i.e. in the tree there's no better route) 
                                                    #we expect that from now on route [0,2] will cost 0  
print(bt.search(1, purgeBinaryVector(v2)));#we see if there's a route that covers 0,1: any cost should return false (even negative) since that route is not present (so we give it a low cost)