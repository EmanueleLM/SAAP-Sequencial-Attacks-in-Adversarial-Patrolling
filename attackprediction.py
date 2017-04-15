# -*- coding: utf-8 -*-
"""
Created on Fri Apr 14 13:50:25 2017

@author: Emanuele

Algorithm used to predict attacks once all the k targets are launched by A
Two versions of the algorithms are presented: AttackPredition2 is the version where k=2
AttackPrediction is the version for k>2
"""

import computecovsets as ccs

# Attack Prediciton for k=2 sequencial attacks
# G is the graph as set of vertices
# v is the vertex in G where D is placed at time j
# t is the target chosen as first target attack by A
# j is the time at which A launch its last resource on target t
def AttackPrediction2(G, v, t, j):
    G_temp = G; #use a temporary version of the graph in order to modify its components
    vertex = G_temp.getVertex(v);
    vertex.setDeadline(vertex.getDeadline()-j);#update first target's deadline
    for t1 in G_temp.getTargets():
        if t1 != t:
            R,U = ccs.computecovsets(G_temp, vertex, [t,t1]);
    return [rcmin,umin]#<--argmin(i)Uimin(i)Ui ..to be completed
 
# Attack Prediction for k>2 sequencial attacks
# G is the graph as set of vertices
# v is the vertex in G where D is placed at time j
# T is the set of targets previosusly under--attack by A at time i<j
# j is the time at which A launch its last resource on target t
def AttackPrediction(G, v, t, j):
    #..to be done
    return;