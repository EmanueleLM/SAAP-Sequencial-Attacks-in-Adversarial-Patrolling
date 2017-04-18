# -*- coding: utf-8 -*-
"""
Created on Fri Apr 14 14:35:46 2017

@author: Emanuele

PathFinder algorithm: used to calculate the best strategy for the defender in a context of 
multiple sequencial attacks.
We provide two versions of the algorithm:
PathFinder2 which consider the possibility of being subjected to 2 attacks
while PathFinder considers more than 2 attacks
"""

import numpy as np;
import attackprediction as ap

#class that models the content of a cell in the dynamic programming matrix M,
#used to store the routes/utility associated to a feasible expansion of the pathfinder algorithm
#each M(i,j) cell contains three elements:
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
    #getter methods for the class
    def getRoute_si(self):
        return self.route_si;
    def getRoute_ij(self):
        return self.route_ij;
    def getUtility(self):
        return self.u_ij;
    #setter methods for the class
    def setRoute_si(self, route_si):
        self.route_si = route_si;
    def setRoute_ij(self, route_ij):
        self.route_ij = route_ij;
    def setUtility(self, u_ij):
        self.u_ij = u_ij;
    #function that defines if the cell i,j is defined
    #return True if there's a route defined inside of it, False otherwise
    def isNone(self):
        return (self.route_si is None);
    #function of equivalence
    def __eq__(self, x):
        return self.getRoute_si==x.route_si and self.getRoute_ij==x.route_ij; #we suppose that two routes are equivalent if they contains the same elements, in the same order (we don't care about utility)            
    #function for distinguish between two vertices
    def __ne__(self, x):
        return not(self.__eq__(x));
    #make the object iterable in a loop (i.e. for loops)
    def __iter__(self):
        return self;

#PathFinder2 function is the function that returns the equilibrium path in a SRG game with k=2 attacks
#it takes as input the graph G, the vertex number v where D is places when she recieves the second attack
#and last target's index under attack, namely t
#it returns the equilibrium path and the utility associated to that path        
def PathFinder2(G, v, t):
    n = len(G.getVerices());#number of vertices on G, used to size dp matrix M
    #matrix of dp algorithm, it contains |V| objects of type RouteExpansion, initially set to None
    M = np.array([[RouteExpansion(None, None, 0) for i in range(n)] for j in range(n)],dtype=RouteExpansion);
    M[v][0].__init__(v, None, G.getVertex(v).getValue());
    for j in n-1: #see if the j+1 in the expansion needs j to go till n-1
        for i in n:
            if M[i][j].isNone():#i.e. the cell M(i,j) is not defined
                continue;
            r_c_min, u_min = ap.AttackPrediction2(G, i, t, j);#suppose the last attack while D is on vertex i at time j (the first attack has been performed on t)
            M[i][j].__init__(M[i][j].getRoute_si(), r_c_min, min(u_min, M[i][j].getUtility()));#set the new route (except for the first memeber route_si, that will created based on the worst route that from the adjacent vertices come to the new one)      
            #expand all the routes created so far in the new column of the dp matrix j+1            
            adjacentvertices = np.array(G.getVertex(i).getAdjacents());#put in a list all the adjacent vertices (by their index number)
            for v1 in adjacentvertices:
                if M[i][j].getUtility() <=  M[v1][j+1].getUtility():
                    M[v1][j+1].__init__(np.append(M[i][j].getRoutesi_(),v1), None, M[i][j].getUtility());        
    
    best_i = best_j = 0;#initialize indices to find the best route in M
    u_star = 0;#initilize the best utility(at the beginning the best route covers anything)
    for i in n:
        for j in n:
            if M[i][j].getUtility()>u_star:
                u_star = M[i][j].getUtility();
                best_i = i;
                best_j = j;
    return M[best_i][best_j].getRoute_si,M[best_i][best_j].getRoute_ij(),M[best_i][best_j].getUtility();
    
def PathFinder():
    
    return;