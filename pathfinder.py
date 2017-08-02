# -*- coding: utf-8 -*-
"""
Created on Fri Apr 14 14:35:46 2017

@author: Emanuele

PathFinder algorithm: used to calculate the best strategy for the defender in a context of 
multiple sequencial attacks.
We provide two versions of the algorithm:
PathFinder2 which consider the possibility of being subjected to 2 attacks
while PathFinder considers more than 2 attacks

[MINOR--BUG]: if you specify that  the first attack is on a non-target and the player is on that vertex, it doesn't care and start the game
     it's a minor since if A attacks something and V is on that vertex, no matter how D can defend it. Still I need to solve it

Long is the 'path' and hard, that out of Hell leads up to light [John Milton]
"""

import numpy as np;
import attackprediction as ap
import graph as gr
import targetdictionary as td
import routeexpansion as re
import time

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
        for i in range(n):
            if M[i][j].isNone():#i.e. the cell M(i,j) is not defined
                continue;
            r_c_min, u_min = ap.AttackPrediction2(G, i, t, j);#suppose the last attack while D is on vertex i at time j (the first attack has been performed on t)          
            r_c_min = r_c_min[0];#take just the route, not the cost            
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
    # zero case attack, solved with shortest paths    
    if k==0:
        # please note the the initial attack to a non target must be avoided in input phase (in solvesaap.py)
        if gr.getShortestPath(G, v, t) <= G.getVertex(t).getDeadline():
            route_sp =  re.RouteExpansion3(np.array([v]), np.array([t]), 0, np.array([t]), list([[np.array([t]),0]]));
        else:
            route_sp = re.RouteExpansion3(np.array([v]), np.array([]), -(G.getVertex(t).getValue()), np.array([]), list([[np.array([t]),0]]));
        route_sp.printRouteExpansion(G);
        return route_sp; 
    # more than one attack
    n = len(G.getVertices()); #number of vertices on G, used to size dp matrix M
    target_dictionary = td.listToDictionary(G.getTargets(), k+1); #transform the list of targets into a power set and then into a dictionary of targets  
    # create the dp matrix M, initially empty except for the cell that represents the starting position of D
    M = np.array([[[None for j in range(k*n)] for i in range(n)]for l in range(len(target_dictionary))]);
    M[0][v][0] = list([re.RouteExpansion3(np.array([v]), np.array([]), 0, np.array([v]) if v==t else np.array([]), list([[np.array([t]),0]]))]);
    stopping_layers = np.array([target_dictionary[i] for i in target_dictionary if len(i.split())==k+1]); # put in the indices of all the layers of cardinality k, i.e. we use this array to check if a route cannot expanded anymore (this is a sufficient condition, not necessary since we can have repetaed attacks on the same target)   
    # we 'populate' the matrix M by columns and then with an in-depth approach wrt the third layer l    
    for j in range(k*(n-1)):
        for l in range(len(target_dictionary)): # associate to each of the matrix M a set of covered targets over the parts of (|T| k) possible targets with k resources
            if l in stopping_layers: # we don't expand layer that are final (all targets expired). please note that a layer in final is not expanded, but not all terminal routes will be on terminal layers (e.g. A attacks twice the same target)
                continue;
            for i in range(n):
                if M[l][i][j] is None: # this condition is to prevent the expansion of null cells of M
                    continue;
                # we suppose from 1 to k-left attacks and we update M according to this fact
                M = ap.AttackPrediction(G, i, j, l, M, k+1, target_dictionary); #this function calculates directly the content (in terms of routes) of all the new cells activated on M            
                #M[l][i][j] = checkDominance(M, i, j, l); # eliminate all the dominated routes in a matrix cell M(i,j,l)
        #'expand routes' passage
        # remember that the domination of routes is done in this way: we expand a route if
        # the next cells doesnt contain a route whose utility is higher(for the defender)
        # and the targets under attacks are the same till that time 
        # you may ask: and what if A decides to attack D waiting some steps?
                # the answer is that we do not eliminate the route that we used to expand the others, so that's the case 
                # you mentioned!
        for l in range(len(target_dictionary)):
            if l in stopping_layers:
                continue;
            for i in range(n):
                if M[l][i][j] is None: # this condition is to prevent the expansion of null cells of M
                    continue;
                adjacentvertices =  np.array(G.getVertex(i).getAdjacents()); # calculate adjacent vertices to vertex i on G
                for r in M[l][i][j]: # for each route in cell M[l][i][j]
                    if r.isNone() or r.attacksLeft(k+1)==0: # or len(r.getTargetsUnderAttack(G, j))==0: #this condition is to prevent the expansion of null routes or routes where the number of resources left to A is zero
                        continue; 
                    for v1 in adjacentvertices:
                        if v1 in r.getTargetsUnderAttack(G, j):
                            covered = np.append(r.getCoveredTargets(), v1);
                        else:
                            covered = r.getCoveredTargets();# returns the targets covered so far in the game, we need v1 in order to calculate if moving on a new vertex can save something!                       
                        r.setCoveredTargets(covered);
                        expired = r.calculateExpiredTargets(G, v1, j+1); # returns the targets expired so far in the game, we need v1 in order to calculate if moving on a new vertex can save something!
                        utility = -sum(G.getVertex(t).getValue() for t in expired);     
                        l_new = target_dictionary[td.listToString(expired)]; # new layer on dp matrix M where the route is moved (if some target has expired)                          
                        # we will update the routes in this manner: if a route enters in a cell and that cell does not contain  a route
                        # with the same targets under attack, we will append that route on that cell. Otherwise if a route has the same targets under
                        # attack and the same terminal node, we will bring with us, and expand, only the route that guarantees a better utility to D (so the best between two)
                        if M[l_new][v1][j+1] != None:
                           for r_next_layer in M[l_new][v1][j+1]:
                               # condition one checks if the targets currently under attack (and not expired) are the same
                               condition1 = r.historyEqual(r_next_layer); # np.array_equal(np.setdiff1d(r.getTargetsUnderAttack(G, j), r.getCoveredTargets()), np.setdiff1d(r_next_layer.getTargetsUnderAttack(G, j+1), r_next_layer.getCoveredTargets())); #left condition on third layer if some tareget is expired on the next step!
                               if condition1: # and v1 in np.setdiff1d(r.getTargetsUnderAttack(G, j), r.getCoveredTargets()):
                                   condition2 = utility > r_next_layer.getUtility();  
                                   if condition2:
                                       r_next_layer.setRoute_si(np.append(r.getRoute_si(),v1));
                                       r_next_layer.setUtility(utility);
                                       break;
                                   else:
                                       break;
                        else:
                            M[l_new][v1][j+1] = list([re.RouteExpansion3(np.append(r.getRoute_si(),v1), np.array([]), utility, covered, r.getHistory())]);#expand the new route calculating all the new elements inside it     

    # extract the utilities of the game
    # then terminate 
    print("Elements at the equilibrium ", extractUtility(M, k+1));
    return re.printDPMatrix(M, k+1, G); #print layers where the number of resources left to A is 0, se the game is ended    

#==============================================================================
# function that returns, given a cell of the dp matrix, only the routes that are not dominated by other routes
#     takes as input:
#         the cell of the dp matrix M, so M, i,j,l
#     returns
#         the modified cell according to the dominance
#     please note that r dominates r' if they have very the same history and one of them has a utility which is better than the other one
#==============================================================================
def checkDominance(M, i, j, l):    
    M_temp = list();
    deleted = np.array([]);
    if M[l][i][j] == None or len(M[l][i][j]) < 2:
        return M[l][i][j];
    else:
        for n in range(len(M[l][i][j])):
            for m in range(len(M[l][i][j])):
                if n!=m and M[l][i][j][n].historyEqual(M[l][i][j][m]):
                    if M[l][i][j][n].getUtility() >= M[l][i][j][m].getUtility():
                        deleted = np.append(deleted, n);
                        break;
                    else:
                        deleted = np.append(deleted, m);
    for n in range(len(M[l][i][j])):
        if n not in deleted:
            M_temp.append(M[l][i][j][n]);
    #print(len(deleted));
    return M_temp; 

#==============================================================================
# function that returns the utility and the route at the equilibrium: 
#  takes as input:
#    the dp matrix, M
#    the number of resources available to A, k
# returns
#   the utility at the equilibrium
#   the route at the equilibrium
#   the history (of the attacks) at the equilibrium
# please note that this piece of code implements a MaxMin w.r.t. the utility of the game.
# it basically extracts, for all histories (i.e. all kinds of attacks by A)
#    the best way to reply for D to each of them
# once we have every best way to react fro D, to each kind of attack by A
# we select the worst (for D) of the attacks and the utility associated to that attack
#==============================================================================
def extractUtility(M, k):   
    histories = list(); # list with every possible attack by A, they are not-in-order, but we do not care, we copare them with the historyEqual function of RouteExpansion3
    utilitydef = np.array([]); # array of floats that contains at the same index of histories, the respective utility
    paths = list(); # same as utilitydef but with the repsective equilibrium path
    for j in range(np.shape(M)[2]):
        for l in range(np.shape(M)[0]):
            for i in range(np.shape(M)[1]):
                if M[l][i][j] == None:
                    continue;
                for r in M[l][i][j]: # for each route that is final, find the best reply to each possible attack of A(i.e. histories of D)
                    if r.attacksLeft(k) == 0:
                        isEqual = False;
                        n = 0; # var that control the indices on the hisotries and utilitydef (useless declaration but makes the code clear since we will use n as index)
                        for n in range(len(histories)):
                            temproute = re.RouteExpansion3(np.array([]), np.array([]), 0, np.array([]), histories[n]);
                            if r.historyEqual(temproute):
                                isEqual = True;
                                break;
                        if isEqual:
                            if r.getUtility() > utilitydef[n]: # max for D w.r.t. the utility, greater is to speedup the function (whats the point of substituting an equilibrium path with another one?)
                                utilitydef[n] = r.getUtility();
                                paths.append(list([r.getRoute_si()[-1],r.getRoute_ij()]));
                        else: # if the attack is not present in the list, add it, we will compare it from now on to the ones that are equal (with RouteExpansion3.historyEqual() function)
                            histories.append(r.getHistory());
                            utilitydef = np.append(utilitydef, r.getUtility());
                            paths.append(list([r.getRoute_si()[-1],r.getRoute_ij()]));
    # min for A w.r.t. the utility
    if len(histories) > 0:
        utility = min(utilitydef);
        index = np.where(utilitydef==utility)[0][0];
        history_at_equilibrium = histories[index];
        route_at_the_equilibrium = paths[index];
        return utility, route_at_the_equilibrium, history_at_equilibrium;    
    else:
        print("A did not attack in this game :P\n");
        return np.NaN, list([np.NaN]), list([np.NaN]); # return NaN types if there's something wrong wiht the matrix 
    
"""
Little testing to see if the algorithms work as expected
"""    
verbose = True; # this variable controls whether the output is printed
if verbose:
    print("\nStart PathFinder Test Part::");          
    v1 = gr.Vertex(1,0.6,2);
    v2 = gr.Vertex(1,0.5,2);
    v3 = gr.Vertex(1,0.6,2);
    v4 = gr.Vertex(1,0.7,2);
    G = gr.Graph(np.array([v1,v2,v3,v4]));
    G.setAdjacents(v1,np.array([1,0,1,1]));
    G.setAdjacents(v2,np.array([0,1,1,0]));
    G.setAdjacents(v3,np.array([1,1,1,1]));
    G.setAdjacents(v4,np.array([1,0,1,1]));
  
    initial_vertex = 1;
    initial_target = 2; # extract the index number of the first target (if no targets, the program will end up with an error, anyhow the graph is not interesting for attacks and sequencial attacks, right?)
    for i in range(0,5):
        start_time = time.time();
        PathFinder(G, initial_vertex, initial_target, i);
        print("Instance with k= ", i+1);
        print("Starting on vertex ", initial_vertex);
        print("Initial target ", initial_target);
        print("--- %s seconds ---" % (time.time() - start_time));