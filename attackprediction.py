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

# Attack Prediciton for k=2 sequencial attacks
# G is the graph as set of vertices
# v is the vertex in G where D is placed at time j
# t is the target chosen as first target under attack by A
# j is the time at which A launch its last resource on target t
# return the best route in terms of utility, and the relative utility
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
 
# Attack Prediction for k>2 sequencial attacks
# G is the graph as set of vertices
# v is the vertex in G where D is placed at time j
# T is the set of targets previosusly under--attack by A at time i<j
# k is the number of resources available at the beginning of the game to A
# j is the time at which A launch its last resource on target t
def AttackPrediction(G, v, T, k, j):
    G_temp = cp.deepcopy(G); #use a temporary version of the graph in order to modify its components
    for t in T: #set the deadline on each target previously under attack equal to its deadline minus the time passed till that phase of the game
        target = G_temp.getVertex(t);
        target.setDeadline(target.getDeadline()-j);#update target's deadline
    R_best = list();
    U_best = len(T)+1;
    for t1 in G_temp.getTargets():
        if t1 != t:
            R,U = ccs.computecovsets(G_temp, v, np.array([T,t1]));#MODIFY IT, WE NEED SOLVESRG() NOT COMPUTECOVSETS()
            if U <= U_best: #consider just the best route and its utility
                U_best = U;
                R_best = R;
    return [R_best,U_best]#return the best route in terms of utility, and the relative utility

    
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