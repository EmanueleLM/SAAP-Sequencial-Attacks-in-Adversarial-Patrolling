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
        self.history = history;
        
#==============================================================================
#     def expandRoute(self, route_si, route_ij, u_ij, covered_targets, history):
#         super(RouteExpansion3, self).expandRoute(route_si, route_ij, u_ij);
#         self.covered_targets = covered_targets.astype(int);
#         self.history = history;
#==============================================================================
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
#    the targets currently under attack, and neither expired nor covered
#==============================================================================
    def getTargetsUnderAttack(self, G, j):
        targets_under_attack = np.array([]);
        targets_yet_expired = self.calculateExpiredTargets(G, None, j);
        for el in self.history:
            for t in el[0]:
                condition1 = t not in targets_yet_expired; # target is not expired
                condition2 = t not in self.route_si[el[1]:el[1]+G.getVertex(t).getDeadline()+1];# in the windows in which the target is alive, it has been covered?
                if condition1 and condition2: # a target is under attack if it has not expired or it has been covered in due time
                    targets_under_attack = np.append(targets_under_attack,t);
        return np.unique(targets_under_attack).astype(int);
        
#==============================================================================
#     calculate the expired targets on G, given a route and its history of attacks
#     takes as input:
#      the graph G
#      the vertex v where D is at time j
#      the time passed j since the beginning of the game
#     it returns:
#      the list of expired targets
#==============================================================================
    def calculateExpiredTargets(self, G, v, j):
        expired_targets = np.array([]);
        if v is not None:
            r_new_route_si = np.append(self.route_si, v);
        else:
            r_new_route_si = np.array(self.route_si);
        for el in self.history:
            for t in el[0]:
                condition1 = t not in r_new_route_si[el[1]:(el[1]+G.getVertex(t).getDeadline()+1)]; # the target has not been covered
                condition2 = j-el[1] > G.getVertex(t).getDeadline() or (j-el[1] >= G.getVertex(t).getDeadline() and r_new_route_si[-1]!=t); # there's no time to cover it anymore
                condition3 = t not in expired_targets; # once it has expired, it is done (redundant since we return a numpy.unique element, but it's ok)               
                if condition1 and condition2 and condition3: #if t is covered in the window where it can be covered
                     expired_targets = np.append(expired_targets, t);
        return np.unique(expired_targets.astype(int));
        
#==============================================================================
#     calculate the expired targets on G, at the end of the game, i.e. after the covering route has been created and followed by D
#     takes as input:
#      the graph G
#      the position v where D is at time j
#      the time passed j since the beginning of the game
#     it returns:
#      the list of expired targets at the end of the game
#==============================================================================  
    def expiredTargetsAtTheEnd(self, G, v, j): 
        expired_targets = self.calculateExpiredTargets(G, v, j);
        targets_alive = self.getTargetsUnderAttack(G, j);
        return np.unique(np.append(expired_targets, np.setdiff1d(targets_alive, self.route_ij)));
        
#   function that prints the values of the element RouteExpansion3
    def printRouteExpansion(self, G):
        print("=====================================");
        print("Route_si: ", self.route_si, " \nRoute_ij: ", self.route_ij, " \nUtility: ", self.u_ij, "\nCovered Targets: ", self.covered_targets, "\nExpired Targets:", self.expiredTargetsAtTheEnd(G,None,5000),"\nHistory: ", self.history);        
        print("=====================================");
        return self.route_si, self.route_ij, self.u_ij, self.history;
        
#==============================================================================
#       function that calculates if two routes have the same history
#        it takes as input:
#           route, which is the route whose hisotry is compared to the one that invokes this function
#        it returns:
#           True or False wheter the histories are the equal
#==============================================================================
    def historyEqual(self, route):
        if len(route.history) != len(self.history): # at least they should contain the same number of elements
            return False;
        for n in range(len(self.history)):
                if self.history[n][1] != route.history[n][1]:
                    return False;
                else:
                    if not(np.array_equal(np.sort(self.history[n][0]).astype(int), np.sort(route.history[n][0]).astype(int))):
                        return False;
        return True;
        
#   function that retruns True if two routes are equal, False otherwise
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
        
#   function that returns True if the history of a route has repeated elements, False otherwise
    def repeatedAttacks(self):
        attacks = np.array([]);
        for n in range(len(self.history)):
            for t in self.history[n][0]:
                attacks = np.append(attacks, t);
        return len(attacks) != len(np.unique(attacks));
        
#==============================================================================
# function that prints the elements of the dp matrix that are terminals i.e. cannot be expanded anymore 
# and represents a game that is ended 
# it takes as input:
#  the matrix M of dp
#  the number of resources available to A at the beginning of the game, k
#  the graph G
#==============================================================================
def printDPMatrix(M, k, G):
    routes = list([]); # list with all the routes, used for data aggregation purposes
    #temp = RouteExpansion3(None, None, 0, np.array([]), list([[np.array([1]), 0], [np.array([0]), 1]]));
    for l in range(np.shape(M)[0]):
        for i in range(np.shape(M)[1]):
            for j in range(np.shape(M)[2]):
                if M[l][i][j] is None:
                    continue;
                else:
                    for r in M[l][i][j]:
                        if r.isNone():
                            continue;
                        elif (r.attacksLeft(k) == 0) and (r.getRoute_ij() is not None): # do not use routes that have not solved SRGV!
                            print(i,j,l);                            
                            r.printRouteExpansion(G);      
                            if r.getRoute_ij() is None: # do not use routes that have not solved SRGV!
                                pass;                                
                                #routes.append([np.append(r.getRoute_si(), np.array([])), r.getUtility(), r.getCoveredTargets(), r.getHistory()]);
                            else:
                                routes.append([np.append(r.getRoute_si(), r.getRoute_ij()[1:]), r.getUtility(), r.getCoveredTargets(), r.getHistory()]);
    return routes;
    
#==============================================================================
# function that prints out a single slice of the dp matrix M  
# it takes as input:
#  the matrix slice M[j] of dp
#  the number of resources available to A at the beginning of the game, k  
#  the graph G
#==============================================================================
def printDPSlice(M, j, k, G):
    routes = list([]); # list with all the routes, used for data aggregation purposes
    #temp = RouteExpansion3(None, None, 0, np.array([]), list([[np.array([1]), 0], [np.array([3]), 1],[np.array([1]), 2]]));
    for l in range(np.shape(M)[0]):
        for i in range(np.shape(M)[1]):    
            if M[l][i][j] is None:
                continue;
            else:
                for r in M[l][i][j]:
                    if r.isNone():
                        continue;
                    elif (r.attacksLeft(k) == 0) and (r.getRoute_ij() is not None): # do not use routes that have not solved SRGV!
                        print(i,j,l);                            
                        r.printRouteExpansion(G);      
                        if r.getRoute_ij() is None: # do not use routes that have not solved SRGV!
                            pass;                                
                            #routes.append([np.append(r.getRoute_si(), np.array([])), r.getUtility(), r.getCoveredTargets(), r.getHistory()]);
                        else:
                            routes.append([np.append(r.getRoute_si(), r.getRoute_ij()[1:]), r.getUtility(), r.getCoveredTargets(), r.getHistory()]);
    return routes;