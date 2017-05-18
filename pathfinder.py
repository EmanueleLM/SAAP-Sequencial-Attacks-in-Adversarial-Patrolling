# -*- coding: utf-8 -*-
"""
Created on Fri Apr 14 14:35:46 2017

@author: Emanuele

PathFinder algorithm: used to calculate the best strategy for the defender in a context of 
multiple sequencial attacks.
We provide two versions of the algorithm:
PathFinder2 which consider the possibility of being subjected to 2 attacks
while PathFinder considers more than 2 attacks

Long is the 'path' and hard, that out of Hell leads up to light [John Milton]
"""

import numpy as np;
import attackprediction as ap
import graph as gr
import targetdictionary as td
import routeexpansion as re

#==============================================================================
# PathFinder2 function is the function that returns the equilibrium path in a SRG game with k=2 attacks
# it takes as input 
#  the graph G
#  the vertex number v where D is placed when she recieves the first attack
#  the target under attack, t
# it returns:
#  the equilibrium path and the utility associated to that path        
#==============================================================================
def PathFinder2(G, v, t):
    n = len(G.getVertices());#number of vertices on G, used to size dp matrix M
    #matrix of dp algorithm, it contains |V| objects of type RouteExpansion, initially set to None
    M = np.array([[re.RouteExpansion(None, None, 0) for i in range(n)] for j in range(n)],dtype=re.RouteExpansion);
    M[v][0].expandRoute(v, None, G.getVertex(v).getValue() if v==t else 0);
    M[v][0].printRouteExpansion();
    for j in range(n-1): # j+1 at line 93(routes expansion) needs j to go till n-1
        #print("TIME ", j);        
        for i in range(n):
            #print("CELL",i);
            if M[i][j].isNone():#i.e. the cell M(i,j) is not defined
                continue;
            r_c_min, u_min = ap.AttackPrediction2(G, i, t, j);#suppose the last attack while D is on vertex i at time j (the first attack has been performed on t)          
            r_c_min = r_c_min[0];#take just the route, not the cost            
            #print(r_c_min, u_min);          
            M[i][j].expandRoute(M[i][j].getRoute_si(), r_c_min, min(u_min, M[i][j].getUtility()));#each cell will contain the route_ij which is the route that from i will cover the last target uder attack, and the relative utility 
            M[i][j].printRouteExpansion();
            #expand all the routes created so far in the new column of the dp matrix j+1            
            adjacentvertices = np.array(G.getVertex(i).getAdjacents());#put in a list all the adjacent vertices (by their index number)           
            for v1 in adjacentvertices:
                if M[i][j].getUtility() <=  M[v1][j+1].getUtility():
                    M[v1][j+1].expandRoute(np.append(M[i][j].getRoute_si(),v1), None, M[i][j].getUtility());        
    best_i = best_j = 0;#initialize indices to find the best route in M
    u_star = 0;#initilize the best utility(at the beginning the best route covers anything)
    for i in range(n):
        for j in range(n):
            if M[i][j].getUtility()<u_star:
                u_star = M[i][j].getUtility();
                best_i = i;
                best_j = j;
    return M[best_i][best_j].getRoute_si,M[best_i][best_j].getRoute_ij(),M[best_i][best_j].getUtility();
    
#==============================================================================
# PathFinder function is the function that returns the equilibrium path in a SRG game with k>2 attacks
# it takes as input:
#  G is the graph on which D and A play the game
#  v is the vertex where D stays when the function is invoked
#  t is the target under attack when the function is invoked
#  k is the number of resources left to A
# it returns:
#  the equilibrium path and the utility associated to that path  
#==============================================================================
def PathFinder(G, v, t, k):
    n = len(G.getVertices()); #number of vertices on G, used to size dp matrix M
    target_dictionary = td.listToDictionary(G.getTargets(), k+1); #transform the list of targets into a power set and then into a dictionary of targets
    M = np.array([[[None for j in range(n)] for i in range(n)]for l in range(len(target_dictionary))]);
    M[0][v][0] = list([re.RouteExpansion3(np.array([v]), np.array([]), 0, np.array([v]) if v==t else np.array([]), list([[np.array([t]),0]]))]);
    stopping_layers = np.array([target_dictionary[i] for i in target_dictionary if len(i.split())==k+1]);#put in the indices of all the layers of cardinality k, i.e. we use this array to check if a route cannot expanded anymore (this is a sufficient condition, not necessary since we can have repetead attacks on the same target)   
    #we 'populate' the matrix M by columns and then with an in-depth approach wrt the third layer l    
    for j in range(n-1):
        for l in range(len(target_dictionary)): #associate to each of the matrix M a set of covered targets over the parts of (|T| k) possible targets with k resources
            if l in stopping_layers: #we don't expand layer that are final (all targets expired). please note that a layer in final is not expanded, but not all terminal routes will be on terminal layers (e.g. A attacks twice the same target)
                continue;
            for i in range(n):
                if M[l][i][j] is None: #this condition is to prevent the expansion of null cells of M
                    continue;
                #We suppose from 1 to k-left attacks and we update M accoridng to this fact
                # we can choose to modify M by passing its column (with all the layers) to AttackPrediction function
                # or let the function return all the new routes with the respective layer and then modify M
                #Anyway, we expect that after this passage we have M modified and ready to pass through the 'expand routes' passage                    
                #print(i,j,l);
                M = ap.AttackPrediction(G, i, j, l, M, k+1, target_dictionary); #this function calculates directly the content (in terms of routes) of all the new cells activated on M            
                #M[l][i][j][0].printRouteExpansion(G);
        #'expand routes' passage
        # remember that the domination of routes is done in this way: we expand a route if
        # the next cells doesnt contain a route whose utility is higher(for the defender)
        # and the targets under attacks are the same till that time 
        for l in range(len(target_dictionary)):
            if l in stopping_layers:
                continue;
            for i in range(n):
                if M[l][i][j] is None: #this condition is to prevent the expansion of null cells of M
                    continue;
                adjacentvertices =  np.array(G.getVertex(i).getAdjacents()); #calculate adjacent vertices to vertex i on G
                for r in M[l][i][j]: #for each route in cell M[l][i][j]
                    if r.isNone() or r.attacksLeft(k+1)==0: #this condition is to prevent the expansion of null routes or routes where the number of resources left to A is zero
                        continue; 
                    for v1 in adjacentvertices:
                        if v1 in r.getTargetsUnderAttack(G, j):
                            covered = np.append(r.getCoveredTargets(), v1);
                        else:
                            covered = r.getCoveredTargets();#returns the targets covered so far in the game, we need v1 in order to calculate if moving on a new vertex can save something!                       
                        expired = r.calculateExpiredTargets(G, v1, j+1); #returns the targets expired so far in the game, we need v1 in order to calculate if moving on a new vertex can save something!
                        utility = -sum(G.getVertex(t).getValue() for t in expired);     
                        l_new = target_dictionary[td.listToString(expired)]; #new layer on dp matrix M where the route is moved (if some target has expired)                          
                        #we will update the routes in this manner: if a route enters in a cell and that cell does not contain  a route
                        # with the same targets under attack, we will append that route on that cell. Otherwise if a route has the same targets under
                        # attack and the same terminal node, we will bring with us, and expand, only the route that guarantees a better utility to D (so the best between two)
                        condition1 = True;
                        condition2 = True;
                        if M[l_new][v1][j+1] != None:
                           for r_next_layer in M[l_new][v1][j+1]:
                               # condition one checks if the targets currently under attack (and not expired) are the same
                               condition1 = np.array_equal(np.setdiff1d(r.getTargetsUnderAttack(G, j), r.getCoveredTargets()), np.setdiff1d(r_next_layer.getTargetsUnderAttack(G, j+1), r_next_layer.getCoveredTargets())); #left condition on third layer if some tareget is expired on the next step!
                               if condition1 and v1 in np.setdiff1d(r.getTargetsUnderAttack(G, j), r.getCoveredTargets()):
                                   condition2 = r.getUtility() < r_next_layer.getUtility(); #check out the verse of this inequality!
                                   break;
                        if condition1 and condition2: 
                            if M[l_new][v1][j+1] != None:
                                M[l_new][v1][j+1].append(re.RouteExpansion3(np.append(r.getRoute_si(),v1), np.array([]), min(utility, r_next_layer.getUtility()), covered, r.getHistory()));#expand the new route calculating all the new elements inside it     
                            else:
                                M[l_new][v1][j+1] = list([re.RouteExpansion3(np.append(r.getRoute_si(),v1), np.array([]), utility, covered, r.getHistory())]);#expand the new route calculating all the new elements inside it     

    # extract the utilities of the game
    # then terminate  
    re.printDPMatrix(M, k+1, G); #print layers where the number of resources left to A is 0, se the game is ended    
    return;
    
"""
Little testing to see if the algorithms work as expected
"""    
print("\nStart PathFinder Test Part::");          
#create vertices        
v1 = gr.Vertex(0,0,0);
v2 = gr.Vertex(1,0.5,2);
v3 = gr.Vertex(1,0.6,2);
v4 = gr.Vertex(1,0.7,2);
v5 = gr.Vertex(1,0.8,2);

#create graph (the issue of assigning a vertex number is given to the graph)
G = gr.Graph(np.array([v1,v2,v3,v4,v5]));

G.setAdjacents(v1,np.array([1,0,0,1,1]));
G.setAdjacents(v2,np.array([0,1,1,1,0]));
G.setAdjacents(v3,np.array([0,1,1,1,0]));
G.setAdjacents(v4,np.array([1,1,1,1,1]));
G.setAdjacents(v5,np.array([1,0,0,1,1]));

PathFinder(G, 0, 1, 2);