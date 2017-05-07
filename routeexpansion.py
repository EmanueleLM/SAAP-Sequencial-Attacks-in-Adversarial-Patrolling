# -*- coding: utf-8 -*-
"""
Created on Sun Apr 30 19:01:56 2017

@author: Emanuele

Expand Route algorithm: it is used to implement the elements contained in the
dp  matrix M, i.e. the routes.
We implemented two versions of the RouteExpansion's object; the former is for 2 attacks
the latter is an extension (thanks to inheritance) of the former that includes the concepts of
"covered targets" and "history", seen as a way to encode the past attacks in the game
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
#   getter methods for the class
    def getRoute_si(self):
        return self.route_si;
    def getRoute_ij(self):
        return self.route_ij;
    def getUtility(self):
        return self.u_ij;
#   setter methods for the class
    def setRoute_si(self, route_si):
        self.route_si = route_si;
    def setRoute_ij(self, route_ij):
        self.route_ij = route_ij;
    def setUtility(self, u_ij):
        self.u_ij = u_ij;
#   function that prints the values of the element RouteExpansion
    def printRouteExpansion(self):
        print("=====================================");
        print("Route_si: ", self.route_si, " \nRoute_ij: ", self.route_ij, " \nUtility: ",self.u_ij);
        print("=====================================");
#   function that defines if the cell i,j is defined
#   return True if there's a route defined inside of it, False otherwise
    def isNone(self):
        return (self.route_si is None);
#   function of equivalence
    def __eq__(self, x):
        return np.array_equal(np.sort(self.getRoute_si),np.sort(x.route_si)) and np.array_equal(np.sort(self.getRoute_ij),np.sort(x.route_ij)); #we suppose that two routes are equivalent if they contains the same elements, in the same order (we don't care about utility)            
#   function for distinguish between two vertices
    def __ne__(self, x):
        return not(self.__eq__(x));
#   make the object iterable in a loop (i.e. for loops)
    def __iter__(self):
        return self;

#==============================================================================
# class that manages the routes expansion when the number of attack is more than 2
# we use two different classes since we want the code to be distinct between case where k=2, and k>2        
#==============================================================================
class RouteExpansion3(RouteExpansion):
    def __init__(self, route_si, route_ij, u_ij, covered_targets, history):
        super(RouteExpansion3, self).__init__(route_si, route_ij, u_ij);
        self.covered_targets = covered_targets.astype(int);
        self.history = list() if history==None else history;
    def expandRoute(self, route_si, route_ij, u_ij, covered_targets, history):
        super(RouteExpansion3, self).expandRoute(route_si, route_ij, u_ij);
        self.covered_targets = covered_targets.astype(int);
        self.history = history;
    def getCoveredTargets(self):
        return self.covered_targets;
    def getHistory(self):
        return self.history;
    def setCoveredTargets(self, covered_targets):
        self.covered_targets = covered_targets.astype(int);
    def setHistory(self, history):
        self.history = history;
#==============================================================================
#   function that calculates the targets under attack using the history element
#   takes as input:
#    the graph G where the game is played, used to calculate the deadline of each target
#    the time j at which the game is, in order to calculate which targets is expired
#   returns:
#    the targets currently under attack, and not yet expired
#   please note that this function returns the targets not expired, but they culd have been covered yet at time j by D!
#==============================================================================
    def getTargetsUnderAttack(self, G, j):
        targets_under_attack = np.array([]);
        for el in self.history:
            for t in el[0]:
                if j-el[1] <= G.getVertex(t).getDeadline() and t not in targets_under_attack:
                    targets_under_attack = np.append(targets_under_attack,t);
        return targets_under_attack.astype(int);
#==============================================================================
#     function that returns the set of covered targets using the intersection between targets covered so far
#      and targets under attack (and not expired)
#     takes as input:
#      the graph G
#      the position v where D is at time j
#      the time passed j since the beginning of the game
#     it returns:
#      the list of covered targets
#==============================================================================
    def calculateCoveredTargets(self, G, v, j):
        covered_targets = np.array([]);
        targets_under_attack = self.getTargetsUnderAttack(G, j);
        if v != None:
            r_new_route_si = np.append(self.route_si, v);
        else:
            r_new_route_si = np.array([self.route_si]);
        for el in self.history:
            for t in el[0]:
                condition1 = t in r_new_route_si[el[1]:el[1]+G.getVertex(t).getDeadline()+1];
                condition2 = j-el[1] <= G.getVertex(t).getDeadline() and t in targets_under_attack;
                if condition1 and condition2: #if t is covered in the window where it can be covered and it's not expired yet
                    covered_targets = np.append(covered_targets, t);
        return np.unique(covered_targets.astype(int));
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
        if v != None:
            r_new_route_si = np.append(self.route_si, v);
        else:
            r_new_route_si = np.array([self.route_si]);
        for el in self.history:
            for t in el[0]:
                #print(self.history);
                if t not in r_new_route_si[el[1]:el[1]+G.getVertex(t).getDeadline()+1] and j-el[1] >= G.getVertex(t).getDeadline(): #if t is covered in the window where it can be covered
                     expired_targets = np.append(expired_targets, t);
        return np.unique(expired_targets.astype(int));
#   function that prints the values of the element RouteExpansion3
    def printRouteExpansion(self):
        print("=====================================");
        print("Route_si: ", self.route_si, " \nRoute_ij: ", self.route_ij, " \nUtility: ", self.u_ij, "\nCovered Targets: ", self.covered_targets, "\nHistory: ", self.history);        
        print("=====================================");
    def __eq__(self, x):
        return np.array_equal(np.sort(self.getRoute_si),np.sort(x.route_si)) and np.array_equal(np.sort(self.getRoute_ij),np.sort(x.route_ij)) and np.array_equal(np.sort(self.covered_targets), np.sort(x.covered_targets) and np.array_equal(np.sort(self.getTargetsUnderAttack()), np.sort(x.getTargetsUnderAttack()))); #we suppose that two routes are equivalent if they contains the same elements, in the same order (we don't care about utility)            
#   function for distinguish between two vertices
    def __ne__(self, x):
        return not(self.__eq__(x));
#   make the object iterable in a loop (i.e. for loops)
    def __iter__(self):
        return self;
#   function that calculates the number of attacks left to A for a given route (i.e. a given game's scenario)
    def attacksLeft(self, k):
        attacks = 0;
        for h in self.history:
            for t in h[0]:
                attacks += 1;
        return k-attacks;
# function that prints the elements of the dp matrix that are terminals i.e. cannot be expanded anymore and represents a game that is ended     
def printDPMatrix(M, k):
    for l in range(np.shape(M)[0]):
        for i in range(np.shape(M)[1]):
            for j in range(np.shape(M)[2]):
                if M[l][i][j] == None:
                    continue;
                else:
                    for r in M[l][i][j]:
                        if r.isNone():
                            continue;
                        elif (r.attacksLeft(k) == 0):
                            r.printRouteExpansion();
    