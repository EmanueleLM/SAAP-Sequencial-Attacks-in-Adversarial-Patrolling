# -*- coding: utf-8 -*-
"""
Created on Sat Apr  8 11:45:19 2017

@author: Emanuele

Pseudocode for the Compute--Cov--Set
Given as input a vertex and a set of target T' under attack (simultaneous)
return the best vertex where D should stay, the strategy and the utility
associated to that scenario

We employ lists instead of numpy.array for storing routes since numpy is not optimized for 
managing non-omogenous arrays (while we use numpy for the shortest paths matrix)
"""

import numpy as np
from operator import attrgetter
import btree as bt
import shortestpath as sp



def computeCovSet(G, v, T):
    utility = 0;
    targets = [G.getVertex(t) for t in T];
    targets.sort(key=attrgetter('vertex_number'), reverse=True); #order the targets by their index_number (we use the same order in the btree)
    btree = bt.BTree(); #create an aempty binary tree 
    n=len(G.getVertices());#calculate the size of the sp matrix
    SP_cost = np.array(sp.shortest_path(G.getAdjacencyMatrix(),n,n)[1]);
    btree.getShortestPaths(SP_cost);#get the sp matrix available to the btree
    if v in [t.getVertexNumber() for t in targets] and v.isTarget(): #if v is a target, it has been yet covered by D at the beginning of the game
        utility += v.getValue();
        btree.update(v.getVertexNumber(),targets, btree.root, bt.binaryVectorFromRoute(v,targets),v.getVertexNumber());#create the first element in the tree
    r0 = list([v]);#the initial route is the one that will be expanded at the beginning
    C = list([r0,0]);#its cost is zero and contains just the initial vertex
    for i in range(len(T)):
        for t in T:
            for q in C:
                Q = list([]);#vector that will contain temporary route+expansions for a given q
                W = list([]); #vector with all the feasible expansions for q
                cost = q[1] + SP_cost[t.getVertexNumber()][q[0][-1].getVertexNumber()]; #the cost of the route is the older cost plus the cost of the shortest path between the new target and the last elemente in the route (i.e. [-1])
                #see if we satisfy the three conditions in order to extend a route (see comments at teh beginning)
                for t1 in T:    
                    condition1 = (t1.getVertexNumber() not in [p.getVertexNumber() for p in q[0]]);#we don't choose a target already covered
                    condition2 = (cost <= t1.getDeadline()); #the target is not expired 
                    condition3 = True;
                    for t2 in targets:
                        if SP_cost[t2.getVertexNumber()][q[0][-1].getVertexNumber()] < cost: #the target chosen for the expansion is the closest in terms of shortest path
                            condition3 = False;
                            break;
                    if (condition1) and (condition2) and (condition3):
                        W.append(t1); #legal and feasible expansions for current route q
                for w in W: #for all expansions, see if they are better than the current one (using a B-Tree)
                            # if so, subsistute them 
                    Q.append([np.append(q[0],w),[cost]]);
                    U = btree.search(Q[-1][1],Q[-1][0]);
                    if U: #just take the depth of the tree where the nodes goes to the right(r contains the target)
                        C.append([[list([q[0],w])],[cost]]);
                        btree.update(C[-1][0],T,btree.root,C[-1][0]);#update the tree (maybe its better to do it in the search function?)
    return C;