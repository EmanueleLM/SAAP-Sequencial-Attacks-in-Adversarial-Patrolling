# -*- coding: utf-8 -*-
"""
Created on Fri Apr 14 13:50:25 2017

@author: Emanuele

Algorithm used to predict attacks once all the k targets are launched by A
Two versions of the algorithms are presented: AttackPredition2 is the version where k=2
AttackPrediction is the version for k>2
"""

import numpy as np
import copy as cp
import computecovsets as ccs
import graph as gr
import itertools
import targetdictionary as td
import routeexpansion as re

#==============================================================================
#  Attack Prediciton for k=2 sequencial attacks
#  G is the graph as set of vertices
#  v is the vertex in G where D is placed at time j
#  t is the target chosen as first target under attack by A
#  j is the time at which A launch its last resource on target t
#  return the best route in terms of utility, and the relative utility
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
#  Attack Prediction for k>2 sequencial attacks
#  G is the graph as set of vertices
#  i is the vertex in G where D is placed at time j
#  j is the number of steps passed from the begginning of the game
#  l is the current layer under exam
#  M is the column (with all the third layer) of the matrix of dp M
#  k is the total number of resources available to A
#  target_dictionary is the dictionary used to index the third matrix layer, namely l
# It returns:
#  the updated M[:][j][:]
#==============================================================================
def AttackPrediction(G, i, j, l, M, k, target_dictionary):
    M_temp = cp.deepcopy(M); #maybe just copy the layer under consideration M[:][j][:]
    for r in M_temp[i][j][l]: #for each route in a cell of the dp matrix
        new_history = cp.deepcopy(r.getHistory()); #copy the current history of the route
        #solve full resources attacks with computecovsets
        powerset = list();
        powerset.append([p for p in itertools.combinations(np.intersect1d(np.array(r.getTargetsUnderAttack()), np.array(G.getTargets())), k-len(r.getTargetsUnderAttack()))]);
        for t_next_attack in powerset:
            G_temp = cp.deepcopy(G); #copy the graph we will use for the simultaneous attacks' case
            for el in r.getHistory(): 
                for t in el:
                    for t1 in el[0]:
                        G_temp.getVertex(t1).diminishDeadline(el[1]); #diminish the deadlines on the new graph in order to call covsets
            t_under_attack = np.array([[s for s in q[0]] for q in r.getHistory()]); #trick to flatten the list in-place           
            print(t_under_attack)            
            ccs.computeCovSet(G_temp, i, np.intersect1d(r.getTargetsUnderAttack(), t_under_attack));
            if new_history[-1][1] == j: #if the attacks happen at the same time as the ones previousy lunched (e.g. at the beginning A uses more than 1 resources)
                new_history[-1][0].append([t for t in t_next_attack]); #append the history to the last one element of the route's history          
            else:
                new_history.append([[t for t in t_next_attack],j]);
            r_new = re.RouteExpansion3(r.getRoute_si(), r.getRoute_ij, r.getUtility(), r.getCoveredTargets(), new_history);
            new_utility = -sum(G.getVertex(t).getValue() for t in np.intersect1d(r_new.getCoveredTargets(), r_new.calculateExpiredTargets(G_temp, i, j)));
            r_new.setUtility(new_utility);                    
            l_new = target_dictionary[td.listToString([r_new.calculateExpiredTargets(G)])]#get target expired till this time of game (we can have targets with deadline equal to zero that becomes immediatly expired)
            M_temp[i][j][l_new].append([r_new]);
        #now deal with non-fully resources attacks        
        for k_left in range(k-len(r.getTargetsUnderAttack())): #for every possible combination of attacks wrt the resources left to A (excluded the fully resources attack, yet calculated)
            powerset = list(); # empty the powersets list if it was filled with the targets of the previous step
            for i in range(1, k_left): #compute the combination of the parts of the elements in l, till cardinality k 
                powerset.append([p for p in itertools.combinations(np.intersect1d(r.getTargetsUnderAttack(), G.getTargets()), i)]);
            for t_next_attack in powerset:
                if new_history[-1][1] == j: 
                    new_history[-1][0].append([t for t in t_next_attack]);
                else:
                    new_history.append([[t for t in t_next_attack],j]);
                r_new = re.ExpandRoute3(r.getRoute_si(), r.getRoute_ij, r.getUtility(), r.getCoveredTargets(), new_history);
                new_utility = -sum(G.getVertex(t).getValue() for t in np.intersect1d(r_new.getCoveredTargets(), r_new.calculateExpiredTargets()));
                r_new.setUtility(new_utility);                    
                l_new = target_dictionary[td.listToString([r_new.calculateExpiredTargets(G)])]#get target expired till this time of game (we can have targets with deadline equal to zero that becomes immediatly expired)
                M_temp[i][j][l_new].append([r_new]);
    return M_temp;

    
"""
Little testing to see if the algorithms work as expected
"""    
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

print(AttackPrediction2(G, 0, 1, 0));