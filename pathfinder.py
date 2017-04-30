# -*- coding: utf-8 -*-
"""
Created on Fri Apr 14 14:35:46 2017

@author: Emanuele

PathFinder algorithm: used to calculate the best strategy for the defender in a context of 
multiple sequencial attacks.
We provide two versions of the algorithm:
PathFinder2 which consider the possibility of being subjected to 2 attacks
while PathFinder considers more than 2 attacks

Long is the 'path' and hard, that out of Hell leads up to light
"""

import numpy as np;
import attackprediction as ap
import graph as gr
import computecovsets as ccs
import targetdictionary as td

#class that models the content of a cell in the dynamic programming matrix M,
#used to store the routes/utility associated to a feasible expansion of the pathfinder algorithm
#each M(i,j) cell contains three elements:
#route_si is the route from vertex s to vertex i
#route_ij is the best covering route from vertex i at time j in order to cover the targets under attack
#u_ij is the utility associated to route route_ij
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

#class that manages the routes expansion when the number of attack is more than 2
#we use two different classes since we want the code to be distinct between case where k=2, and k>2        
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
        return targets_under_attack;
    #function that returns the set of covered targets using the intersection between targets covered so far
    # and targets under attack 
    #takes as input:
    # the graph G
    # the position v where D is at time j
    # the time passed j since the beginning of the game
    #it returns:
    # the list of covered targets
    def calculateCoveredTargets(self, G, v, j):
        covered_targets = np.array();
        r_new = np.append(self.route_si, v);
        for el in self.history:
            for t in el[0]:
                if t in r_new[el[1]:el[1]+G.getVertex(t).getDeadline()]: #if t is covered in the window where it can be covered
                    covered_targets = np.append(covered_targets, t);
        return covered_targets;
    #calculate the expired targets on G, given a route and its history of attacks
    #takes as input:
    # the graph G
    # the position v where D is at time j
    # the time passed j since the beginning of the game
    #it returns:
    # the list of expired targets
    def calculateExpiredTargets(self, G, v, j):
        expired_targets = np.array();
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
    
#PathFinder2 function is the function that returns the equilibrium path in a SRG game with k=2 attacks
#it takes as input 
# the graph G
# the vertex number v where D is placed when she recieves the first attack
# the target under attack, t
#it returns:
# the equilibrium path and the utility associated to that path        
def PathFinder2(G, v, t):
    n = len(G.getVertices());#number of vertices on G, used to size dp matrix M
    #matrix of dp algorithm, it contains |V| objects of type RouteExpansion, initially set to None
    M = np.array([[RouteExpansion(None, None, 0) for i in range(n)] for j in range(n)],dtype=RouteExpansion);
    M[v][0].expandRoute(v, None, G.getVertex(v).getValue() if v==t else 0);
    M[v][0].printRouteExpansion();
    for j in range(n-1): # j+1 at line 93(routes expansion) needs j to go till n-1
        #print("TIME ", j);        
        for i in range(n):
            #print("CELL",i);
            if M[i][j].isNone():#i.e. the cell M(i,j) is not defined
                continue;
            r_c_min, u_min = ap.AttackPrediction2(G, i, t, j);#suppose the last attack while D is on vertex i at time j (the first attack has been performed on t)          
            r_c_min = r_c_min[0];#take just the route, not the cost            
            #print(r_c_min, u_min);          
            M[i][j].expandRoute(M[i][j].getRoute_si(), r_c_min, min(u_min, M[i][j].getUtility()));#each cell will contain the route_ij which is the route that from i will cover the last target uder attack, and the relative utility 
            M[i][j].printRouteExpansion();
            #expand all the routes created so far in the new column of the dp matrix j+1            
            adjacentvertices = np.array(G.getVertex(i).getAdjacents());#put in a list all the adjacent vertices (by their index number)           
            for v1 in adjacentvertices:
                if M[i][j].getUtility() <=  M[v1][j+1].getUtility():
                    M[v1][j+1].expandRoute(np.append(M[i][j].getRoute_si(),v1), None, M[i][j].getUtility());        
    best_i = best_j = 0;#initialize indices to find the best route in M
    u_star = 0;#initilize the best utility(at the beginning the best route covers anything)
    for i in range(n):
        for j in range(n):
            if M[i][j].getUtility()<u_star:
                u_star = M[i][j].getUtility();
                best_i = i;
                best_j = j;
    return M[best_i][best_j].getRoute_si,M[best_i][best_j].getRoute_ij(),M[best_i][best_j].getUtility();
    
#PathFinder function is the function that returns the equilibrium path in a SRG game with k>2 attacks
#it takes as input:
# G is the graph on which D and A play the game
# v is the vertex where D stays when the function is invoked
# t is the target under attack when the function is invoked
# k is the number of resources left to A
#it returns:
# the equilibrium path and the utility associated to that path 
def PathFinder(G, v, t, k):
    n = len(G.getVertices()); #number of vertices on G, used to size dp matrix M
    target_dictionary = td.listToDictionary(G.getTargets(), k+1); #transform the list of targets into a power set and then into a dictionary of targets
    #print(target_dictionary);
    M = np.array([[[None for l in range(len(target_dictionary))] for j in range(n)]for i in range(n)]);   
    initial_layer = target_dictionary[td.listToString([v])] if v==t else 0; #initial layer on M where the game begins  
    M[v][0][initial_layer] = list([RouteExpansion3(v, None, G.getVertex(v).getValue() if v==t else 0, np.array(v) if v==t else None, [[t],0])]);       
    # TODO: remeber to eliminate the empty route (isNone()==True) when at least a valid route is added to a cell of M[][][]
    stopping_layers = np.array([target_dictionary[i] for i in target_dictionary if len(i.split())==k+1]);#put in the indices of all the layers of cardinality k, i.e. we use this array to check if a route cannot expanded anymore
    #print(stopping_layers);    
    #we 'populate' the matrix M by columns and then with an in-depth approach wrt the third layer l    
    for j in range(n-1):
        for l in range(len(target_dictionary)): #associate to each of the matrix M a set of covered targets over the parts of (|T| k) possible targets with k resources
            if l in stopping_layers: #we don't expand layer that are final (all targets expired)
                continue;
            for i in range(n):
                if M[i][j][l] is None: #this condition is to prevent the expansion of null cells of M
                    continue;
                #We suppose from 1 to k-left attacks and we update M accoridng to this fact
                # we can choose to modify M by passing its column (with all the layers) to AttackPrediction function
                # or let the function return all the new routes with the respective layer and then modify M
                #Anyway, we expect that after this passage we have M modified and ready to pass through the 'expand routes' passage                    
                M = ap.AttackPrediction(G, i, j, l, M, k+1, target_dictionary); #this function calculates directly the content (in terms of routes) of all the new cells activated on M
                """ ATTENZIONE A NON CREARE ROTTE E RICHIAMARE SU DI ESSE ATTACKPREDICTION ALTRIMENTI VA AD INFINITO FINO A FINE GIOCO
                AL PRIMO TURNO!!!"""                
        # 'expand routes' passage
            # remember that the domination of routes is done in this way: we expand a route if
                # the next cells doesnt contain a route whose value is higher(for the defender)
                # and the targets under attacks are the same till that time 
        for l in range(len(target_dictionary)):
            if l in stopping_layers:
                continue;
            for i in range(n):
                if M[i][j][l] is None: #this condition is to prevent the expansion of null cells of M
                    continue;
                adjacentvertices =  np.array(G.getVertex(i).getAdjacents()); #calculate adjacent vertices to vertex i on G
                for r in M[i][j][l]: #for each route in cell M[i][j][l]
                    if r.isNone() or r is None: #this condition is to prevent the expansion of null routes
                        continue; 
                    for v1 in adjacentvertices:
                        condition1 = r.getUtility() <= min(r_1.getUtility() for r_1 in M[v1][j+1][l]); #check out the verse of this inequality!
                        condition2 = np.array_equal(np.intersect1d(r.getTargetsUnderAttack(), r.getCoveredTargets()), M[v1][j+1][l].getTargetsUnderAttack(), M[v1][j+1][l].getCoveredTargets()); #left condition on third layer if some tareget is expired on the next step!
                        if condition1 and condition2 : 
                            #check expired in the next step j+1
                            expired = r.caluclateExpiredTargets(G, v1, j+1); #returns the targets expired so far in the game, we need v1 in order to calculate if moving on a new vertex can save something!
                            covered = r.calculateCoveredTargets(G, v1, j+1); #returns the targets covered so far in the game, we need v1 in order to calculate if moving on a new vertex can save something!                       
                            utility = min(0,-sum(G.getVertex(t).getValue() for t in expired));                            
                            l_new = target_dictionary[td.listToString(expired)]; #new layer on dp matrix M where the route is moved (if some target has expired)                          
                            M[v1][j+1][l_new].append(RouteExpansion3(np.append(r.getRoute_si(),v1), None, utility, covered, r.getHistory()));#expand the new route calculating all the new elements inside it     
    # extract the utilities of the game
    # then terminate  
    return;
    
"""
Little testing to see if the algorithms work as expected
"""    
print("\nStart PathFinder Test Part:");          
#create vertices        
v1 = gr.Vertex(0,0,0);
v2 = gr.Vertex(1,0.5,3);
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

print(ccs.computeCovSet(G, 0, G.getTargets()));

print("bestroute")
print(PathFinder2(G, 1, 2)); #when D is on vertex 0, recieves an attack on target 1
                             #we expect to loose -0.5 since the first attack is on vertex 1, but the best 
                             #strategy for A is a sim. attack to two targets at the beginning, and D will never cover both of them
PathFinder(G, 0, 2, 2);