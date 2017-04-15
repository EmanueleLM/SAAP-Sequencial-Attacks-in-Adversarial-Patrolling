# -*- coding: utf-8 -*-
"""
Created on Fri Apr 14 14:35:46 2017

@author: Emanuele

PathFinder algorithm: used to calculate the best strategy for the defender in a context of 
multiple sequencial attacks.
We provide two versions of teh algorithm:
PathFinder2 which consider the possibility of being subjected to 2 attacks
while PathFinder consider more than 2 attacks
"""

import numpy as np;

#class that models the content of the dynamic programming matrix M,
#used to store the routes/utility associated to a feasible expansion
#of the pathfinder algorithm
#it has three elements:
#route_si is the route from vertex s to vertex i
#route_ij is the best covering route from vertex i at time j in order to cover the targets under attack
#u_ij is the utility associated to route route_ij
class RouteExpansion(object):
    def __init__(self, route_si, route_ij, u_ij):
        if self.route_si is None:
            self.route_si = np.array([route_si]) if route_si!=None else np.array([]);
        else:
            self.route_si = np.append(self.route_si, route_si) if route_si!=None else self.route_si;
        if self.route_ij is None:
            self.route_ij = np.array([route_ij]) if route_ij!=None else np.array([]);
        else:
            self.route_ij = np.append(self.route_ij, route_ij) if route_ij!=None else self.route_ij;
        self.u_ij = u_ij;
    #function that defines if the cell i,j is defined
    #return True if there's a route defined inside of it, False otherwise
    def isNone(self):
        return (self.route_si is None);
        

def PathFinder2(G, v, t):
    n = len(G.getVerices());#number of vertices on G, used to size dp matrix M
    s = v.getVertexNumber();#extract the index of the vertex associated to the initial position of D
    #matrix of dp algorithm, it contains |V| objects of type RouteExpansion, initially set to None
    M = np.matrix([[RouteExpansion(None, None, 0) for i in range(n)] for j in range(n)],dtype=RouteExpansion);
    M[s][0].__init__(s, None, v.getValue()); 
    for j in n:
        for i in n:
            if M[i][j].isNone():
                continue;
            ###CONTINUE HERE###
    return;
    
def PathFinder():
    return;