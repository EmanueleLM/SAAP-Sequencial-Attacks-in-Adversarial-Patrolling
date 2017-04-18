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
    U_best = 2; #utility associated to the best route, we need it to be 2 initially
    for t1 in G_temp.getTargets():
        if t1 != t:
            R,U = ccs.computecovsets(G_temp, v, [t,t1]);#MODIFY IT, WE NEED SOLVESRG() NOT COMPUTECOVSETS()
            if U <= U_best: #consider just the route/utility associated to the worst case scenario's attack by A
                U_best = U;
                R_best = R;
    return [R_best,U_best]#return the best route in terms of utility, and the relative utility
 
# Attack Prediction for k>2 sequencial attacks
# G is the graph as set of vertices
# v is the vertex in G where D is placed at time j
# T is the set of targets previosusly under--attack by A at time i<j
# j is the time at which A launch its last resource on target t
def AttackPrediction(G, v, T, j):
    G_temp = cp.deepcopy(G); #use a temporary version of the graph in order to modify its components
    for t in T: #set the deadline on each target previously under attack equal to its deadline minus the time passed till that phase of the game
        target = G_temp.getVertex(t);
        target.setDeadline(target.getDeadline()-j);#update target's deadline
    R_best = list();
    U_best = len(T)+1;
    for t1 in G_temp.getTargets():
        if t1 != t:
            R,U = ccs.computecovsets(G_temp, v, np.append(T,t1));#MODIFY IT, WE NEED SOLVESRG() NOT COMPUTECOVSETS()
            if U <= U_best: #consider just the best route and its utility
                U_best = U;
                R_best = R;
    return [R_best,U_best]#return the best route in terms of utility, and the relative utility
    return;