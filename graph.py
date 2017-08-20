# -*- coding: utf-8 -*-
"""
Created on Thu Apr  6 10:47:31 2017

@author: Emanuele

Class that manages graphs and vertices, used to shape our scenario of sequencial
attacks in adversarial patrolling

I, know a place, where the 'graph' is really greener! [Katy Perry]
"""

import shortestpath as sp
import numpy as np

inf = 999; #if an arc has this weight, it means that two nodes are not connected on G

#==============================================================================
# class Vertex that defines the vertices on graph G
# we distinguish between targets and non-targets
#  each Vertex has the following attributes
#  is_target that is True if the vertex is a target on G (False, otherwise)
#  value which is the value of the target (between 0 and 1, 0 if it's not a target, 1 at most if it's a target)
#  deadline which is the deadline associated to each vertex on G (it becomes at most -1 for expired targets)
#  adjacents which is a list of all the indices of vertices that are neighbors of the aformentioned vertex
#==============================================================================
class Vertex(object):
    vertex_number = -1; #this number must be unique for each vertex
#   initialize the object "vertex" by defyining its attributes
    def __init__(self, is_target, value, deadline):
        self.is_target = is_target;
        self.value = value;
        self.deadline = deadline;
        self.adjacents = np.array([]);
#   return the vertex number
    def getVertexNumber(self):
        return self.vertex_number;
#   set the vertex number (should be unique for each vertex in G)
    def setVertexNumber(self, vertex_number):
        self.vertex_number = vertex_number;
#   return True if the vertex is a target, False otherwise
    def isTarget(self):
        return self.is_target;
#   return the value of the vertex (0 if it's not a target, more than 0 and at most 1 if its a target)
    def getValue(self):
        return self.value;
#   return the deadline associated to the vertex (0 if the target is expired or if it's a non--target vertex)
    def getDeadline(self):
        return self.deadline;
#   return the list of adjacent vertices
    def getAdjacents(self):
        return self.adjacents.astype(int);
#   set if the vertex is a target
    def setTarget(self, is_target):
        self.is_target = is_target;
#   set the target value: at most it is 1, if it's not a target, it's zero
    def setValue(self, value):
        if self.isTarget():
            self.value = min(1, value);
        else:
            self.value = 0;
#   set the vertex deadline
    def setDeadline(self, deadline):
        if self.isTarget():
            self.deadline = max(-1, deadline);#we can't put it to max(0,deadline), 'cause if D is on a target and the deadline is 0, the target is protected, even if it has been expired from ages
        else:
            self.deadline = 0;
#   set the adjacent vertices using a binary vector where each entry is 1 if there's a connection between the vertex and another one
    def setAdjacents(self, adjacents):
        new_adjacents = np.array([]);
        for i in range(len(G.getVertices())):
            if adjacents[i]==1 and i!=self.getVertexNumber():
                new_adjacents = np.append(new_adjacents, i);
        self.adjacents = new_adjacents;
#   function that diminishes the deadline of the target of a quantity j
    def diminishDeadline(self, j):
        self.deadline -= j;
#   print the adjacent vertices
    def printAdjacents(self):
        print("Vertex "+ str(self.vertex_number) + " is adjacent to:\n"
                + str(self.getAdjacents()));
#   function of equivalence
    def __eq__(self, x):
        return self.vertex_number==x.vertex_number;
#   function for distinguish between two vertices
    def __ne__(self, x):
        return not(self.vertex_number==x.vertex_number);
#   make the object iterable in a loop (i.e. for loops)
    def __iter__(self):
        return self;
        
#==============================================================================
# class Graph that defines a graph as a set of vertices and edges       
# it has the following attributes:
#  vertices which is the complete list of vertices on G 
#==============================================================================
class Graph(object):
    vertices = np.array([]);
    def __init__(self, vertices):
        for v in vertices:
            self.vertices = np.append(self.vertices, v);
            v.setVertexNumber(len(self.vertices)-1);
#   return the vertex by its number
    def getVertex(self, indexnumber):
        if indexnumber <= len(self.vertices):
            return self.vertices[int(indexnumber)];
        else:
            print("Node does not exists\n");
    def getVertices(self):
        return self.vertices;
#   function to add a vertex after the creation of the graph
    def addVertex(self, v):
        self.vertices = np.append(self.vertices,v);
        #give to each vertex a unique number
        v.setVertexNumber = len(self.vertices)-1;
        
#==============================================================================
#     uses a binary vector to set the adjacents' vertices (can be used with the adjacency matrix)
#     takes as input the vertex, and adj_vertices, a binary vector of size |V|
#     and whenever an element on that vector is 1, it adds to the list of the adjacents
#     the corresponding vecotr in G (indexing starts from 1)
#==============================================================================
    def setAdjacents(self, vertex, adj_vertices):
        i = 0;
        for b in adj_vertices:
            if b and i not in(vertex.adjacents):
                vertex.adjacents = np.append(vertex.adjacents, i);
            i+=1;
        vertex.adjacents.sort();
        return vertex.adjacents; 
        
#==============================================================================
#     return the adjacency matrix
#     it assign a value of 1 if two vertices are directly connected, inf otherwise
#     every vertex shortest path to itself is considered to be 0 as weight
#==============================================================================
    def getAdjacencyMatrix(self): 
        n = len(self.getVertices());
        A = np.array([[inf for i in range(n)] for j in range(n)]);
        for i in self.getVertices():
            for j in range(n):
                if i.vertex_number==j:
                    A[j][j] = 0;
                elif j in i.getAdjacents():
                    A[i.vertex_number][j] = 1;
                else:
                    A[i.vertex_number][j] = inf;
        return A;
        
#   function that returns all the targets indices in G
    def getTargets(self):
        T = np.array([]);
        for v in self.getVertices():
            if v.is_target:
                T = np.append(T,v.vertex_number);
        return T.astype(int);
        
#==============================================================================
# function that returns the density of a given graps as average number of arcs per node   
#   the number of edges is drawn from a normal distribution with mean, said edge density and defined as epsilon = 2E/T*(T−1)
#==============================================================================
    def getDensity(self):
        tot = 0;
        n = np.size(self.getAdjacencyMatrix()[0]);
        SP, SP_cost = np.array(sp.shortest_path(self.getAdjacencyMatrix(),n,n));
        for i in range(n):
            for j in range(n):
                if SP_cost[i,j]==1 and i!=j:
                    tot += 1;
        return (tot)/(n*(n-1));
        
#==============================================================================
# function that set all the deadlines of the targets uniformely between min_deadline and max_deadline
#         
#==============================================================================
    def setAllDeadlines(self, min_deadline, max_deadline):
        for v in self.getTargets():
            self.getVertex(v).setDeadline(np.random.randint(min_deadline, max_deadline));
            
#==============================================================================
# function that generates a random adjacency (0,1) matrix with the following input
#  n is the size of the matrix
#  p in the probability that a node is connected to another one (we assume indepent the prob that i is connected to j, and i is connected to w different from j)    
# it returns
#  the adjacency matrix M
#==============================================================================
def generateRandMatrix(n, p):
    l = 0;
    M = np.array([[0 for i in range(n)] for j in range(n)]);
    for i in range(n):
        M[i][i] = 1;
    for i in range(n):
        for j in range(l):
            if np.random.rand() <= p:
                M[i][j] = 1;
                M[j][i] = 1;
        l += 1;
    return M;
    
#==============================================================================
# function that creates a graph that is composed by n vertices whose values is between (0,1] 
# and whose deadline is uniformely distributed between 1 and max_deadline
# takes as input:
#     the adjacency matrix M
#     the number of vertices in the graph, n
#     the probability p that a vertex is a target on G
#     the maximum deadline a target can have
# it returns
#     the graph generated with the previous carachteristics
# please note that
#     the deadlines are uniformely distributed between [min_deadline, max_deadline]
#==============================================================================
def generateRandomGraph(M, n, p, min_deadline, max_deadline):
    vertices = np.array([]);
    for i in range(n):
        if np.random.rand() <= p:
            deadline = np.random.randint(min_deadline, max_deadline+1);
            value = np.random.rand();
            v = Vertex(1, value, deadline);
        else:
            v = Vertex(0,0,0);
        vertices = np.append(vertices, v);
    G = Graph(vertices);
    for i in range(n):
        G.setAdjacents(vertices[i], M[i]);
    return G;    
    
# function that returns the shortest path cost between two nodes        
def getShortestPath(G, i, j):
    n = np.size(G.getAdjacencyMatrix()[0]);
    SP, SP_cost = np.array(sp.shortest_path(G.getAdjacencyMatrix(),n,n));
    return int(SP_cost.item(i,j));   
    
#==============================================================================
# function that returns the diameter of a graph, as the longest of the shortest paths on G
# takes as input
#     the graph G
# returns
#     the diameter as an integer
#==============================================================================
def getDiameter(G):
    n = np.size(G.getAdjacencyMatrix()[0]);
    SP, SP_cost = np.array(sp.shortest_path(G.getAdjacencyMatrix(),n,n));
    return np.matrix.max(SP_cost).astype(int);   
    
#==============================================================================
# function that transforms a shortest path matrix into an adjacency matrix
# takes as input
#     the shortest path matrix sp
# returns
#     the adjacency matrix where something is connected (even to itself) if a 1 is present in the respective
#     cell of the matrix
#==============================================================================
def fromSpToAdjacency(spmatrix):
    n = range(np.shape(spmatrix)[0]);
    adjacency = np.array([[0 for i in n]for j in n]);
    for i in n:
        for j in n:
            if spmatrix[i,j]==1 or spmatrix[i,j]==0:
                adjacency[i][j]=1;
    return adjacency;
    
#==============================================================================
# function that adds connections to a graph since its edge density reaches a value in the Neighbo(u)rhood of the input \epsilon
# takes as input
#     the adjacency matrix M ,which has to represent a connected graph, if not so connect it by using the fromSpToAdjacency(sp.connectMatrix(SP_cost)) "chain"
#     the desired edge density e, rounded to the third decimal and with an exceeding of 0.05
# returns the adjacency matrix of the graph with some new edges
# please note the each new edges is added to a random vertex, if it's not fully connected (if so, it selects another vertex)
# REMEBER THAT ONCE YOU CALL THIS FUNCTION YOU MUST RECOMPUTE THE SHORTEST PATH MATRIX!
#==============================================================================
def increaseEdgeDensity(adj, e):
    n = np.shape(adj)[0];
    density = sum(sum(adj)); # total number of edges, also the autoedges are considered here
    density -= n; # remove autoedges
    density /= n*(n-1);
    # 1.while density < e: 
    # 2.take random vertex, add an edge, if possible 
    # 3.goto 1
    while density<e:
         # pickup a vertex randomly
        v = np.random.randint(n);
        for i in np.random.permutation(n): # if we permute the indices, we connect random disconnected elements!
            if adj[v][i] == 0 and i!=v:
                adj[v][i]=adj[i][v]=1;
                density = sum(sum(adj)); # total number of edges, also the autoedges are considered here
                density -= n; # remove autoedges
                density /= n*(n-1);
                break;
    return adj;
    
"""
Little testing to see if the algorithms work as expected
"""               
verbose = False; # this variable controls whether the output is printed
if verbose: 
    M = generateRandMatrix(15, 0.15); # generate a random adjacency matrix with n vertices, and a probability to be connected to each other vertex set to p
    G = generateRandomGraph(M, np.shape(M)[0], 0.2, 0, 0); # generate the graph with the adjacency matrix M
    #print("\n Targets on G are:");
    #print([int(i) for i in G.getTargets()]);
    print("Adjacency matrix:");
    print(G.getAdjacencyMatrix());
        #obtain the shortest path matrix (through a classical sp algorithm)
    n = np.size(G.getAdjacencyMatrix()[0]);
    SP, SP_cost = np.array(sp.shortest_path(G.getAdjacencyMatrix(),n,n));
    
    #print("\n Shortest path matrix:");
    #print(SP);
    
    print("\n Shortest Path's cost Matrix:");
    print(SP_cost);
    
    print("Density of the graph is ", G.getDensity());    
    
    connected_adj = fromSpToAdjacency(sp.connectMatrix(SP_cost));    
    print("Adjacency graph of the connected matrix is\n", connected_adj);
    for i in range(np.shape(connected_adj)[0]):
        G.getVertex(i).setAdjacents(connected_adj[i]);
    
    increased_adj = increaseEdgeDensity(connected_adj, 0.35);
    print("Want to add a number of nodes s.t. the density is 0.35");
    print(increased_adj);
    for i in range(np.shape(increased_adj)[0]):
        G.getVertex(i).setAdjacents(increased_adj[i]);
        
    diameter = np.matrix.max((sp.shortest_path(G.getAdjacencyMatrix(),n,n))[1]).astype(int); # calculate the diameter in order to set the min/max deadlines on G
    G.setAllDeadlines(diameter, (2*diameter)+1);       
       
    print("Now the density is ", G.getDensity());
    print("The new adjacency matrix is ", G.getAdjacencyMatrix());
    
    SP, SP_cost = np.array(sp.shortest_path(G.getAdjacencyMatrix(),n,n));
    print(SP_cost);
    
    