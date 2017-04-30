# -*- coding: utf-8 -*-
"""
Created on Sun Apr 30 19:01:56 2017

@author: Emanuele
"""


import numpy as np

#==============================================================================
# class that models the content of a cell in the dynamic programming matrix M,
# used to store the routes/utility associated to a feasible expansion of the pathfinder algorithm
# each M(i,j) cell contains three elements:
# route_si is the route from vertex s to vertex i
# route_ij is the best covering route from vertex i at time j in order to cover the targets under attack
# u_ij is the utility associated to route route_ij
#==============================================================================
class RouteExpansion(object):
    def __init__(self, route_si, route_ij, u_ij):
        self.route_si = route_si;
        self.route_ij = route_ij;
        self.u_ij = u_ij;
    def expandRoute(self, route_si, route_ij, u_ij):
        self.route_si = route_si;
        self.route_ij = route_ij;
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
    #function that prints the values of the element RouteExpansion
    def printRouteExpansion(self):
        print("Route_si: ", self.route_si, " \nRoute_ij: ", self.route_ij, " \nUtility: ",self.u_ij);
    #function that defines if the cell i,j is defined
    #return True if there's a route defined inside of it, False otherwise
    def isNone(self):
        return (self.route_si is None);
    #function of equivalence
    def __eq__(self, x):
        return np.array_equal(np.sort(self.getRoute_si),np.sort(x.route_si)) and np.array_equal(np.sort(self.getRoute_ij),np.sort(x.route_ij)); #we suppose that two routes are equivalent if they contains the same elements, in the same order (we don't care about utility)            
    #function for distinguish between two vertices
    def __ne__(self, x):
        return not(self.__eq__(x));
    #make the object iterable in a loop (i.e. for loops)
    def __iter__(self):
        return self;

#==============================================================================
# class that manages the routes expansion when the number of attack is more than 2
# we use two different classes since we want the code to be distinct between case where k=2, and k>2        
#==============================================================================
class RouteExpansion3(RouteExpansion):
    def __init__(self, route_si, route_ij, u_ij, covered_targets, history):
        super(RouteExpansion3, self).__init__(route_si, route_ij, u_ij);
        self.covered_targets = covered_targets;
        self.history = list() if history==None else list([history]);
    def expandRoute(self, route_si, route_ij, u_ij, covered_targets, history):
        super(RouteExpansion3, self).expandRoute(route_si, route_ij, u_ij);
        self.covered_targets = covered_targets;
        self.history.append(history);
    def getCoveredTargets(self):
        return self.covered_targets;
    def getHistory(self):
        return self.history;
    def setCoveredTargets(self, covered_targets):
        self.covered_targets = covered_targets;
    def setHistory(self, history):
        self.history = history;
    # function that calculates the targets under attack using the history element
    def getTargetsUnderAttack(self):
        targets_under_attack = np.array([]);
        for el in self.history:
            targets_under_attack = np.append(targets_under_attack,[t for t in el[0]]);
        return targets_under_attack.astype(int);
#==============================================================================
#     function that returns the set of covered targets using the intersection between targets covered so far
#      and targets under attack 
#     takes as input:
#      the graph G
#      the position v where D is at time j
#      the time passed j since the beginning of the game
#     it returns:
#      the list of covered targets
#==============================================================================
    def calculateCoveredTargets(self, G, v, j):
        covered_targets = np.array();
        r_new = np.append(self.route_si, v);
        for el in self.history:
            for t in el[0]:
                if t in r_new[el[1]:el[1]+G.getVertex(t).getDeadline()]: #if t is covered in the window where it can be covered
                    covered_targets = np.append(covered_targets, t);
        return covered_targets;
#==============================================================================
#     calculate the expired targets on G, given a route and its history of attacks
#     takes as input:
#      the graph G
#      the position v where D is at time j
#      the time passed j since the beginning of the game
#     it returns:
#      the list of expired targets
#==============================================================================
    def calculateExpiredTargets(self, G, v, j):
        expired_targets = np.array([]);
        r_new = np.append(self.route_si, v);
        for el in self.history:
            for t in el[0]:
                if t in r_new[el[1]:el[1]+G.getVertex(t).getDeadline()]: #if t is covered in the window where it can be covered
                    continue;
                elif j-el[1] < G.getVertex(t).getDeadline(): #otherwise it is expired if it's deadline's ended up
                    expired_targets = np.append(expired_targets, t);
        return expired_targets;
    #function that prints the values of the element RouteExpansion3
    def printRouteExpansion(self):
        print("Route_si: ", self.route_si, " \nRoute_ij: ", self.route_ij, " \nUtility: ", self.u_ij, "\nCovered Targets: ", self.covered_targets, "\nTargets Under Attack in this scenario: ", self.getTargetsUnderAttack());
    def __eq__(self, x):
        return np.array_equal(np.sort(self.getRoute_si),np.sort(x.route_si)) and np.array_equal(np.sort(self.getRoute_ij),np.sort(x.route_ij)) and np.array_equal(np.sort(self.covered_targets), np.sort(x.covered_targets) and np.array_equal(np.sort(self.getTargetsUnderAttack()), np.sort(x.getTargetsUnderAttack()))); #we suppose that two routes are equivalent if they contains the same elements, in the same order (we don't care about utility)            
    #function for distinguish between two vertices
    def __ne__(self, x):
        return not(self.__eq__(x));
    #make the object iterable in a loop (i.e. for loops)
    def __iter__(self):
        return self;
    