# -*- coding: utf-8 -*-
"""
Created on Fri Apr 14 13:50:25 2017

@author: Emanuele

Algorithm used to predict attacks once all the k targets are launched by A
Two versions of the algorithms are presented: AttackPredition2 is the version where k=2
AttackPrediction is the version for k>2

How many 'routes' must a man walk down, before you call him a man? [Bob Dylan]
"""

import numpy as np
import copy as cp
import computecovsets as ccs
import graph as gr
import itertools
import targetdictionary as td
import routeexpansion as re

#==============================================================================
# Attack Prediciton for k=2 sequencial attacks
# takes as input:
#  G is the graph as set of vertices
#  v is the vertex in G where D is placed at time j
#  t is the target chosen as first target under attack by A
#  j is the time at which A launch its last resource on target t
# returns:
#  the best route in terms of utility, and the relative utility
#==============================================================================
def AttackPrediction2(G, v, t, j):
    G_temp = cp.deepcopy(G); #use a temporary version of the graph in order to modify its components
    vertex = G_temp.getVertex(t);
    vertex.setDeadline(vertex.getDeadline()-j);#update first target's deadline
    R_best = list(); #best route found out in this way
    U_best = 0; #utility associated to the best route, we need it to be -2 initially
    for t1 in G_temp.getTargets().astype(int):
        U = -2;
        R = list();
        if t1 != t:
            C = ccs.computeCovSet(G_temp, v, np.array([t,t1]));#MODIFY IT, WE NEED SOLVESRG() NOT COMPUTECOVSETS()                    
            for c in C:
                temp= np.around(ccs.getUtilityFromRoute(G_temp, c[0], [t,t1]), decimals=2);#dunno why I need to round this number, numpy wierd approx on certain numbers
                #print(ccs.getUtilityFromRoute(G_temp, c, [t,t1]), G.getVertex(t).getValue(),G.getVertex(t1).getValue(),c,temp)
                if temp > U:
                    U = temp;
                    R = c;
            print(U,R)
            if U <= U_best: #consider just the route/utility associated to the worst case scenario's attack by A           
                U_best = U;
                R_best = R;
    return [R_best,U_best]#return the best route in terms of utility, and the relative utility
 
#==============================================================================
# Attack Prediction for k>2 sequencial attacks
# takes as input:
#  G is the graph as set of vertices
#  i is the vertex in G where D is placed at time j
#  j is the number of steps passed from the begginning of the game
#  l is the current layer under exam
#  M is the column (with all the third layer) of the matrix of dp M
#  k is the total number of resources available to A
#  target_dictionary is the dictionary used to index the third matrix layer, namely l
# it returns:
#  the updated M[:][:][j] 
#==============================================================================
def AttackPrediction(G, i, j, l, M, k, target_dictionary):
    M_temp = cp.deepcopy(M); #maybe just copy the layer under consideration M[:][:][j]
    #print(i,j,l)
    for r in M[l][i][j]: #for each route in a cell of the dp matrix (the original one, otherwise we happily loop forever)      
        if r.attacksLeft(k)==0: #solved bug with final empty hisotry member, in this way it's not expanded an ended route
            continue;
        #solve full resources attacks with computecovsets
        targets_amenable = np.setdiff1d(np.array(G.getTargets()), np.append(r.calculateExpiredTargets(G, None, j), r.getTargetsUnderAttack(G, j))); # targets_amenable is the set of targets amenable to an attack (i.e. all targets minus the expired plus the targets currently under attack)
        powerset = list([np.array(p) for p in itertools.combinations(targets_amenable, r.attacksLeft(k))]);                    
        for t_next_attack in powerset:  
            G_temp = cp.deepcopy(G); #copy the graph we will use for the simultaneous attacks' case
            new_history = cp.deepcopy(r.getHistory()); #copy the current history of the route
            # prepare the new target for the attacks when all the resources of the Attacker are displayed
            for el in r.getHistory(): 
                for t in el:
                    for t1 in el[0]:
                        if t1 in r.calculateExpiredTargets(G, None, j):
                            G_temp.getVertex(t1).setDeadline(-1);
                        elif t1 in r.getTargetsUnderAttack(G, j): # the target is now under attack
                            G_temp.getVertex(t1).setDeadline(G.getVertex(t1).getDeadline() - (j-el[1])); #diminish the deadlines on the new graph in order to call covsets
            # create the new history of the attacks for the new route
            if j == 0: #if the attacks happen at the same time as the ones previousy launched (e.g. at the beginning A uses more than 1 resource)
                new_history[-1][0] = np.append(new_history[-1][0],[t for t in t_next_attack.astype(int)]); #append the history to the last one element of the route's history          
            else:
                new_history.append([np.array([t for t in t_next_attack.astype(int)]),j]); # otherwise it will be an independent element of the history
            # create the new route that will be inserted one of the final layes of M
            r_new = re.RouteExpansion3(r.getRoute_si(), np.array([]), 0, r.getCoveredTargets(), new_history);
            best_route, best_utility = ccs.solveSRG(G_temp, i, r_new.getTargetsUnderAttack(G, j)); 
            r_new_covered_targets = np.append(r_new.getCoveredTargets(), best_route[1:]);    
            r_new.setRoute_ij(best_route);
            r_new.setCoveredTargets(np.unique(r_new_covered_targets));
            targets_lost_at_the_end = np.append(r_new.calculateExpiredTargets(G, None, j), np.setdiff1d(r_new.getTargetsUnderAttack(G, j), best_route[1:]));
            r_new.setUtility(-sum(G.getVertex(t).getValue() for t in targets_lost_at_the_end));
            l_new = target_dictionary[td.listToString(targets_lost_at_the_end)]; #get target expired till this time of game (we can have targets with deadline equal to zero that becomes immediatly expired)
            if M_temp[l_new][i][j] != None:
                M_temp[l_new][i][j].append(r_new);
            else:
                M_temp[l_new][i][j] = list([r_new]);
        #now deal with non-fully resources attacks      
        powerset = list(); # empty the powersets list if it was filled with the targets of the previous step
        for k_left in range(1, r.attacksLeft(k)): #for every possible combination of attacks wrt the resources left to A (excluded the fully resources attack, yet calculated)
            for p in itertools.combinations(targets_amenable, k_left):            
                powerset.append(np.array(p));
        for t_next_attack in powerset:
            new_history = cp.deepcopy(r.getHistory()); #copy the current history of the route
            if j == 0: 
                new_history[-1][0] = np.append(new_history[-1][0],[t for t in t_next_attack.astype(int)]); #append the history to the last one element of the route's history          
            else:
                new_history.append([np.array([t for t in t_next_attack.astype(int)]),j]);
            r_new = re.RouteExpansion3(r.getRoute_si(), r.getRoute_ij(), r.getUtility(), r.getCoveredTargets(), new_history);
            r_new.setCoveredTargets(r_new.getCoveredTargets()); # nothing can happen at this stage to the covered targets            
            l_new = target_dictionary[td.listToString(r_new.calculateExpiredTargets(G, None, j))]#get target expired till this time of game (we can have targets with deadline equal to zero that becomes immediatly expired)           
            new_utility = -sum(G.getVertex(t).getValue() for t in r_new.calculateExpiredTargets(G, None, j));
            r_new.setUtility(new_utility);            
            if M_temp[l_new][i][j] != None:
                M_temp[l_new][i][j].append(r_new);
            else:
                M_temp[l_new][i][j] = list([r_new]);
    return M_temp;

    
"""
Little testing to see if the algorithms work as expected
"""    
verbose = False; # this variable controls whether the output is printed
if verbose:
    print("\nStart AttackPrediction Test Part:");          
    #create vertices        
    v1 = gr.Vertex(0,0,0);
    v2 = gr.Vertex(1,0.6,3);
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
    
    print(AttackPrediction2(G, 1, 1, 0));