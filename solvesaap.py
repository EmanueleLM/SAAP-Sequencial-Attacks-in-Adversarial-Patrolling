# -*- coding: utf-8 -*-
"""
Created on Wed Jul 19 14:33:27 2017

@author: Emanuele

Solve SAAP() script:
takes as input a series of graphs encoded as an adjacency matrix A, and a description of each node
encoded as type of node (simple vertex or target), its value (0 if it's not a target, between 0 and 1
if it's a target) and a deadline (0 if it's a vertex, greater than zero and integer if it's a target)
"""

import pathfinder as pf
import numpy as np
import xml.etree.ElementTree as et
import graph as gr

path = ""; # path to find the graphs' description
graphs = list(); # list that contains the name of each graph file in txt format
k = 3; # number of resources we want the solver solves for each instance of the graphs specified in graphs


#==============================================================================
# function that invokes pathfinder for a given specification of the SAAP game (Graph, initial vertex, initial target)
#     and solves it for the instances of sequencial attacks that go from 1 to k
# returns a file .dat that contains all the routes generated and the best route associated to the equilibrium path and its utility
#==============================================================================
def solveSAAP():
    for graph in graphs:
        G, v, t = createGraphFromFile(path+str(graph)); # returns in G the grapg, in v the initial vertex where D stays at the beginning of the game, and the initial target attack t       
        for i in range(k):
            pf.PathFinder(G, v, t, k); # solve the game for a specific instance with a given number of resources 'k' for the Attacker
    return;

#==============================================================================
# function that create a graph G from a file that specifies the adjacency matrix at first
#     the initial vertex v, the first target under attack t and how the graph is (vertices, targets, their values and deadlines..)
#     the format of the file is the following and in this order: 
#         adjacency matrix A specified as [[1,0],[0,1]]
#         a list of each vertex charachteristic as [vertex/target, value, deadline] where vertex=0, target=1
#             , valie is a real number in [0,1](0 is for vertices)
#             , deadline is a natural number (0 for vertices, any other for targets)
#             , e.g. [0,0,0] --> vertex, [1, 0.5, 10] --> target with 0.5 as value, 10 as deadline
#             , an example of a 3*3 vertices' specification is [[0,0,0],[1,1,4],[1,0.3,5]]
#         initial vertex as a number (rememeber that the first vertex in the graph is the vertex 0 and so on..)
#         initial target as a number that identifies the vertex (rememeber that the first vertex in the graph is the vertex 0 and so on..)
#     all this stuff must be encoded in a pseudo-xml format (just to be a little more polite and clean)
#     even if you can find an example of psuedo-xml graph in the repo on github, here's one:

#     <G>
#         <A>[[1,1,1],[1,1,1],[1,1,1]]</A>
#         <V>[[1,0.3,3],[0,0,0],[1,0.8,12]]</V>
#         <V0>2</V0>
#         <T0>1</T0>
#     </G>

#     the previous example specifies a fully connected graph with 3 vertices, 2 targets (index 0 and 2) and a vertex (index 1)
#     the initial vertex is vertex whose id is 2, i.e. the third(and last) vertex in G
#     the initial target under attack is vertex whose index is 1, i.e. the second vertex on G
# the function returns a graph G, the intial vertex v and the initial target under attack t that can be used to invoke PathFinder
#==============================================================================
def createGraphFromFile(filepath):
    elements_check = ["A", "V", "V0", "T0"]; # elements to check if all the graph's elements are present in the file 
    tree = et.parse(filepath);
    root = tree.getroot();
    # check if everything is ok with the specification file, otherwise exit
    for element in tree:
        for check in elements_check:
            if str(check)!=str(element.tag):
                print("Missing ", check ,"or troubles with order");
                exit();
    # create the empty Graph and the adjacency matrix by parsing the file (thanks to eval, even if I should not use it :P)
    G = gr.Graph(np.array([]));
    adj_matrix = np.array(eval(root[0].text)); 
    vertices = np.array(eval(root[1].text)); 
    n = 0;
    # for each vertex create the graph G
    for v in vertices:
        G = np.append(G, gr.Vertex(int(v[0]), float(v[1]), int(v[2])));
        G.setAdjacents(gr.Vertex(int(v[0]), float(v[1]), int(v[2])), np.array(adj_matrix[n]));
        n += 1;       
    return [G, int(root[2].text), int(root[3].text)]; # return the graph, the initial vertex where D stays and the iinitial attack target

