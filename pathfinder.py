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
import graph as gr
import computecovsets as ccs

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
        if self.route_si is None:
            self.route_si = np.array([route_si]);
        else:
            self.route_si = np.append(self.route_si, route_si);
        if self.route_ij is None:
            self.route_ij = np.array([route_ij]);
        else:
            self.route_ij = np.append(self.route_ij, route_ij);
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
        return self.getRoute_si==x.route_si and self.getRoute_ij==x.route_ij; #we suppose that two routes are equivalent if they contains the same elements, in the same order (we don't care about utility)            
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
#it returns the equilibrium path and the utility associated to that path        
def PathFinder2(G, v, t):
    n = len(G.getVertices());#number of vertices on G, used to size dp matrix M
    #matrix of dp algorithm, it contains |V| objects of type RouteExpansion, initially set to None
    M = np.array([[RouteExpansion(None, None, 0) for i in range(n)] for j in range(n)],dtype=RouteExpansion);
    M[v][0].expandRoute(v, None, G.getVertex(v).getValue());
    M[v][0].printRouteExpansion();
    for j in range(n-1): #see if the j+1 in the expansion needs j to go till n-1
        for i in range(n):
            if M[i][j].isNone():#i.e. the cell M(i,j) is not defined
                continue;
            r_c_min, u_min = ap.AttackPrediction2(G, i, t, j);#suppose the last attack while D is on vertex i at time j (the first attack has been performed on t)
            M[i][j].expandRoute(M[i][j].getRoute_si(), r_c_min, min(u_min, M[i][j].getUtility()));#set the new route (except for the first memeber route_si, that will created based on the worst route that from the adjacent vertices come to the new one)      
            #expand all the routes created so far in the new column of the dp matrix j+1            
            adjacentvertices = np.array(G.getVertex(i).getAdjacents());#put in a list all the adjacent vertices (by their index number)
            for v1 in adjacentvertices:
                if M[i][j].getUtility() <=  M[v1.astype(int)][j+1].getUtility():
                    M[v1.astype(int)][j+1].expandRoute(np.append(M[i][j].getRoute_si(),v1), None, M[i][j].getUtility());        
    
    best_i = best_j = 0;#initialize indices to find the best route in M
    u_star = 0;#initilize the best utility(at the beginning the best route covers anything)
    for i in range(n):
        for j in range(n):
            if M[i][j].getUtility()>u_star:
                u_star = M[i][j].getUtility();
                best_i = i;
                best_j = j;
    print("the best route is ", M[best_i][best_j].getRoute_ij());
    print("its utility is ",M[best_i][best_j].getUtility())
    return M[best_i][best_j].getRoute_si,M[best_i][best_j].getRoute_ij(),M[best_i][best_j].getUtility();
 
#G is the graph on which D and A play the game
#v is the vertex where D stays when the function is invoked
#t is the set of targets under attack when the function is invoked
#t_covered is the set of targets covered by D when the function is invoked
#k is the number of resources left to A
def PathFinder(G, v, t, t_covered, k):
    """
    for all Tua s.t. len(Tua)=k --> covsets();
    for all Tua s.t. len(Tua)=k-1 --> expand routes; PathFinder(G, v.neighbors(), tUTua, t_covered, 1);
    ...
    for all Tua s.t. len(Tua)=1 --> expand routes; PathFinder(G, v.neighbors(), tUTua, t_covered, k-1);   
    expand routes;
    PathFinder(G, v.neighbors(), t, t_covered, k); <-- to be done until t_covered!=t
    """    
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
print(PathFinder2(G, 0, 1)); #when D is on vertex 0, recieves an attack on target 1