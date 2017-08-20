# -*- coding: utf-8 -*-
"""
Created on Sat Apr  8 11:45:19 2017

@author: Emanuele

Pseudocode for the Compute--Cov--Set
Given as input a vertex and a set of target T' under attack (simultaneous)
return the strategies (i.e. the routes) and the utilities associated to that scenario

Moreover you can pass directly the parameters to the solveSRG function that invokes computeCovSets
and returns the best route and utility for a given set of targets, from a a starting position in the graph

We employ lists instead of numpy.array for storing routes since numpy is not optimized for 
managing non-omogenous arrays (while for example we use numpy for the shortest paths matrix)

What is a 'covset'?! [Dr. House]
"""

import numpy as np
import graph as gr
import btree as bt
import shortestpath as sp

#==============================================================================
#computeCovSets function calculates the covering routes on a Graph
#takes as input:
# the graph G on which the game is played (please note that if you want to calculate the best covering route
#  on a graph with different deadlines (i.e. in sequencial cases) you have to modify G before you pass it to
#  the function computecovsets)
# the vertex v as a positive integer (vertexNumber of v on G)
# the set of targets as a list of integers (the vertexNumber of each target that is under attack on G) 
#  even if there's just one target, pass it as a list (i.e. [])
#the function returns:
# the covering routes calculated from node v, composed by (route, cost, utility)
# please note that the utility is expressed as negative sum of targets' value that have been lost
#==============================================================================
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
                #see if we satisfy the three conditions in order to extend a route (see comments at the beginning)
                condition1 = (t not in q[0]);#we don't choose a target already covered by the route q selected at this step
                condition2 = (cost <= G.getVertex(t).getDeadline()); #the target is not expired 
                condition3 = True;
                for t2 in SP[q[0][-1]][t][1:-1]:#for all the elements in the shortest path between the last element of the route and the next target
                    if t2 in targets and t2 not in q[0] and G.getVertex(t2).getDeadline() >= q[1] + SP_cost[q[0][-1]][t2]:                        
                        condition3 = False;
                        break;
                if (condition1) and (condition2) and (condition3):  
                    W.append(t); #legal and feasible expansions for current route q
                for w in W: #for all expansions, see if they are better than the current one (using a B-Tree)
                            # if so, subsistute them                    
                    Q.append([np.append(q[0],w), cost.astype(int)]);
                    U = btree.search(Q[-1][1],bt.purgeBinaryVector(bt.binaryVectorFromRoute(Q[-1][0],targets)));
                    if not U: #just take the depth of the tree where the nodes goes to the right(r contains the target)
                        C.append([np.append(q[0],w),cost]);
                        btree.update(C[-1][0],targets,btree.root,bt.binaryVectorFromRoute(C[-1][0],targets),C[-1][0]);#update the tree (maybe its better to do it in the search function?)
        #print("\n\n",[c for c in C if len(c[0])==i+1]);
        if i > 0:
            C = purgeDominatedStrategies(C, i+1);
    #eventually append to each route the utility
    for c in C:
        c.append(getUtilityFromRoute(G, c[0], targets));    
    return C;

#==============================================================================
# function that eliminates the dominated covering routes of dimensionality i(i.e. contain exactly i elements)
#  a route r dominates another route r' iff r contains the same elements as r', the last element in both the routes is the same
#  and the cost of r is lower(strictly) than the cost of r'
#  if we have to choose between two identical routes (same lenght, same covered targets) we choose indifferently one of them
# takes as input
#  the set of covering routes C  
#  the current time step at which we want to apply dominance between routes 
#==============================================================================
def purgeDominatedStrategies(C, i):
    # divide each route from its cost
    C_temp = list();
    routes = list(r[0] for r in C);
    costs = np.array([r[1] for r in C]).astype(int);
    deleted = np.array([]); # list of the index of the elements deleted so far
    for n in range(len(routes)):
        for m in range(len(routes)):
            condition1 = len(routes[n]==i); # we just deal with the last layer of routes, i.e. the longest ones
            condition2 = np.array_equal(np.sort(routes[n]), np.sort(routes[m])); # we want that the routes contains the same elements
            condition3 =  m not in deleted and n not in deleted;            
            if  condition1 and condition2 and condition3:
                if routes[n][-1] == routes[m][-1] and n!=m:
                    #print("We are going to confront ",  C[n], " with ", C[m]);
                    if costs[n] <= costs[m]:
                        deleted = np.append(deleted, m);
                        #print("we eliminated ", routes[m], costs[m]);
                    else:
                        deleted = np.append(deleted, n);
                        #print("we eliminated ", routes[n], costs[n]);
    #print(deleted);
    for n in range(len(C)):
        if n not in deleted:
            C_temp.append(C[n]);
    return C_temp;

#==============================================================================
#function that computes the utility(for the Defender) associated to a route
# it's assumed that route is covered by its deadline,
# otherwise the route wouldn't have been created
#the function takes as input
#  the graph G
#  the route 'route' on which it is calculated the utility
#  the targets that are indeed under attack
#it returns:
# the utility associated to that route on G
#==============================================================================
def getUtilityFromRoute(G, route, targets):
    utility = 0;
    for t in targets:
        if t not in route:
            utility -= G.getVertex(t).getValue();
    return utility;
    
#==============================================================================
#function that computes the best covering route on a set of targets under simultaneous attack
# it's assumed that route is covered by its deadline,
# otherwise the route wouldn't have been created
#the function takes as input:
# the graph G on which the game is played (please note that if you want to calculate the best covering route
#  on a graph with different deadlines (i.e. in sequencial cases) you have to modify G before you pass it to
#  the function computecovsets)
# the vertex v as a positive integer (vertexNumber of v on G)
# the set of targets as a list of integers (the vertexNumber of each target that is under attack on G) 
#  even if there's just one target, pass it as a list (i.e. [])
#it returns:
# the best route in terms of utility
# the utility of the aformentioned route
#  please note that the utility is expressed as negative sum of targets' value that have been lost
#==============================================================================
def solveSRG(G, v, targets):
    best_utility = -len(targets); # we initially impose that the utility is the one in the worst case scenario (everything is lost, every target has value equal to 1)  
    best_route = np.array([]); # the initial best route is set to empty  
    for c in computeCovSet(G, v, targets): # we call computeCovSets and we calculate the best route,utility couple  
        if c[2] > best_utility: # strict inequality since we evaluate covering routes by increasing lenght, and we prefer obviously routes of minor complexity (i.e. shorter)            
            best_route = c[0];
            best_utility = c[2];
    return best_route, best_utility;
        
"""
Little testing to see if the algorithms work as expected
"""    
verbose = False; # this variable controls whether the output is printed
if verbose:
    print("\nStart ComputeCovSet Test Part:");          
    #create vertices        
    #create vertices        
    v1 = gr.Vertex(0,0,0);
    v2 = gr.Vertex(1,0.5,4);
    v3 = gr.Vertex(1,0.6,2);
    v4 = gr.Vertex(1,0.7,3);
    v5 = gr.Vertex(1,0.8,2);
    v6 = gr.Vertex(1,0.9,3);
    v7 = gr.Vertex(1,1,2);
    v8 = gr.Vertex(0,0,0);
    v9 = gr.Vertex(1,0.3,3);
    v10 = gr.Vertex(0,0,0);
    v11 = gr.Vertex(1,1,4);
    
    
    #create graph (the issue of assigning a vertex number is given to the graph)
    G = gr.Graph(np.array([v1,v2,v3,v4,v5,v6,v7,v8,v9,v10,v11]));
    
    G.setAdjacents(v1,np.array([1,0,0,1,1,0,1,0,0,0,0]));
    G.setAdjacents(v2,np.array([0,1,1,1,0,0,1,0,0,0,0]));
    G.setAdjacents(v3,np.array([0,1,1,1,0,0,1,0,0,0,0]));
    G.setAdjacents(v4,np.array([1,1,1,1,1,0,1,0,0,0,0]));
    G.setAdjacents(v5,np.array([1,0,0,1,1,1,1,0,0,0,0]));
    G.setAdjacents(v6,np.array([0,0,0,0,1,1,1,0,0,0,0]));
    G.setAdjacents(v7,np.array([1,1,1,1,1,1,1,1,1,1,1]));
    G.setAdjacents(v8,np.array([0,0,0,0,0,0,1,1,1,1,1]));
    G.setAdjacents(v9,np.array([0,0,0,0,0,0,1,1,1,1,1]));
    G.setAdjacents(v10,np.array([0,0,0,0,0,0,1,1,1,1,1]));
    G.setAdjacents(v11,np.array([0,0,0,0,0,0,1,1,1,1,1]));
    
    print(computeCovSet(G, 0, np.array([1,2,3,4,5,6,8,10]))); # we calculate the best covering route on the graph generated previosuly
    print(solveSRG(G, 0, np.array([1,2,3,4,5,6,8,10]))); # we calculate the best covering route on the graph by solving the SRG problem