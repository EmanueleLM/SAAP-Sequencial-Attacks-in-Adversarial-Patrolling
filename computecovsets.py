# -*- coding: utf-8 -*-
"""
Created on Sat Apr  8 11:45:19 2017

@author: Emanuele

Pseudocode for the Compute--Cov--Set
Given as input a vertex and a set of target T' under attack (simultaneous)
return the strategies (i.e. the routes) and the utilities associated to that scenario

We employ lists instead of numpy.array for storing routes since numpy is not optimized for 
managing non-omogenous arrays (while for example we use numpy for the shortest paths matrix)
"""

import numpy as np
import graph as gr
import btree as bt
import shortestpath as sp


#the inputs are:
#the graph G on which the game is played (please note that if you want to calculate the best covering route)
#on a graph with different deadlines (i.e. in sequencial cases) you have to modify G before you pass it to
#the function computecovsets
#the vertex v as a positive integer (indexnumber of v on G)
#the set of targets as a list of numbers (the index number of each target is under attack on G) even if there's just one target, pass it as a list (i.e. [])
#the function returns the covering routes calculated from node v
def computeCovSet(G, v, targets):
    targets = np.sort(targets.astype(int)); #order the targets by their index_number (we use the same order in the btree)
    btree = bt.BTree(); #create an aempty binary tree 
    n=len(G.getVertices());#calculate the size of the sp matrix
    SP = sp.shortest_path(G.getAdjacencyMatrix(),n,n)[0];#shortest path matrix
    SP_cost = np.array(sp.shortest_path(G.getAdjacencyMatrix(),n,n)[1]);#shortest path costs' matrix
    btree.getShortestPaths(SP_cost);#get the sp matrix available to the btree
    btree.update([v], targets, btree.root, bt.binaryVectorFromRoute([v],targets), [v]);#create the first element in the tree
    C = list([[np.array([v]),0]]);#the initial route is the one that will be expanded at the beginning.its cost is zero and contains just the initial vertex
    for i in range(len(targets)):
        for t in targets:
            for q in [c for c in C if len(c[0])==i+1]: #with one-line python we consider just the routes expanded at time i-1 (we use their lenght as "watermark")                                                   
                Q = list([]);#vector that will contain temporary route+expansions for a given q
                W = list([]); #vector with all the feasible expansions for q
                cost = q[1] + SP_cost[t][q[0][-1]]; #the cost of the route is the older cost plus the cost of the shortest path between the new target and the last elemente in the route (i.e. [-1])                                       
                #see if we satisfy the three conditions in order to extend a route (see comments at teh beginning)
                condition1 = (t not in q[0]);#we don't choose a target already covered by the route q selected at this step
                condition2 = (cost <= G.getVertex(t).getDeadline()); #the target is not expired 
                condition3 = True;
                for t2 in SP[q[0][-1]][t][1:-1]:#for all the elements in the shortest path between the last element of the route and the next target
                    if G.getVertex(t2).isTarget() and t2 not in q[0] and G.getVertex(t2).getDeadline() >= q[1] + SP_cost[q[0][-1]][t2]:                        
                        condition3 = False;
                        break;
                if (condition1) and (condition2) and (condition3):    
                    W.append(t); #legal and feasible expansions for current route q
                for w in W: #for all expansions, see if they are better than the current one (using a B-Tree)
                            # if so, subsistute them 
                    Q.append([np.append(q[0],w),cost.astype(int)]);
                    U = btree.search(Q[-1][1],bt.purgeBinaryVector(Q[-1][0]));
                    if not U: #just take the depth of the tree where the nodes goes to the right(r contains the target)
                        C.append([np.append(q[0],w),cost]);
                        btree.update(C[-1][0],targets,btree.root,bt.binaryVectorFromRoute(C[-1][0],targets),C[-1][0]);#update the tree (maybe its better to do it in the search function?)
    return C;
    
"""
Little testing to see if the algorithms work as expected
"""    
print("\nStart ComputeCovSet Test Part:");          
#create vertices        
v1 = gr.Vertex(0,0,0);
v2 = gr.Vertex(1,0.5,3);
v3 = gr.Vertex(1,1,3);
v4 = gr.Vertex(1,0.6,3);
v5 = gr.Vertex(1,0.5,3);

#create graph (the issue of assigning a vertex number is given to the graph)
G = gr.Graph(np.array([v1,v2,v3,v4,v5]));

G.setAdjacents(v1,np.array([1,0,0,1,1]));
G.setAdjacents(v2,np.array([0,1,1,1,0]));
G.setAdjacents(v3,np.array([0,1,1,1,0]));
G.setAdjacents(v4,np.array([1,1,1,1,1]));
G.setAdjacents(v5,np.array([1,0,0,1,1]));

print(computeCovSet(G, 0, G.getTargets()));