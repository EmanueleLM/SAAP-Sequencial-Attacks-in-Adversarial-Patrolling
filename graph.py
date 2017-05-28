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
        
 
"""
Little testing to see if the algorithms work as expected
"""              
#create vertices   
#please note that in this graph, starting from vertex 0, it is impossible to
#cover targets 1,4,2 together if a simultaneous attack is performed on all the three targets           
v1 = Vertex(0,0,0);
v2 = Vertex(1,0.5,4);
v3 = Vertex(1,0.6,2);
v4 = Vertex(1,0.7,3);
v5 = Vertex(1,0.8,2);
v6 = Vertex(1,0.9,3);
v7 = Vertex(1,1,2);
v8 = Vertex(0,0,0);
v9 = Vertex(1,0.3,3);
v10 = Vertex(0,0,0);
v11 = Vertex(1,1,4);


#create graph (the issue of assigning a vertex number is given to the graph)
G = Graph(np.array([v1,v2,v3,v4,v5,v6,v7,v8,v9,v10,v11]));

G.setAdjacents(v1,np.array([1,0,0,1,1,0,1,0,0,0,0]));
G.setAdjacents(v2,np.array([0,1,1,1,0,0,1,0,0,0,0]));
G.setAdjacents(v3,np.array([0,1,1,1,0,0,1,0,0,0,0]));
G.setAdjacents(v4,np.array([1,1,1,1,1,0,1,0,0,0,0]));
G.setAdjacents(v5,np.array([1,0,0,1,1,1,1,0,0,0,0]));
G.setAdjacents(v6,np.array([0,0,0,0,1,1,1,0,0,0,0]));
G.setAdjacents(v7,np.array([1,1,1,1,1,1,1,1,1,1,1]));
G.setAdjacents(v8,np.array([0,0,0,0,0,0,1,1,1,1,1]));
G.setAdjacents(v9,np.array([0,0,0,0,0,0,1,1,1,1,1]));
G.setAdjacents(v10,np.array([0,0,0,0,0,0,1,1,1,1,1]));
G.setAdjacents(v11,np.array([0,0,0,0,0,0,1,1,1,1,1]));

verbose = False; # this variable controls whether the output is printed
if verbose:
    print("\nVertices' adjacencies:");
    v1.printAdjacents();
    v2.printAdjacents();   
    v3.printAdjacents();  
    v4.printAdjacents();  
    v5.printAdjacents();
    v6.printAdjacents();
    v7.printAdjacents();   
    v8.printAdjacents();  
    v9.printAdjacents();  
    v10.printAdjacents();
    v11.printAdjacents();
    
    
    print("\n Targets on G are:");
    print([int(i) for i in G.getTargets()]);
    
    print("\nAdjacency Matrix:");
    print(G.getAdjacencyMatrix()); 
    
    #obtain the shortest path matrix (through a classical sp algorithm)
    n = np.size(G.getAdjacencyMatrix()[0]);
    SP, SP_cost = np.array(sp.shortest_path(G.getAdjacencyMatrix(),n,n));
    
    print("\n Shortest path matrix:");
    print(SP);
    
    print("\n Shortest Path's cost Matrix:");
    print(SP_cost);