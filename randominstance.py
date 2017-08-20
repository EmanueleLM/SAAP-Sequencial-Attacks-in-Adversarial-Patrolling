# -*- coding: utf-8 -*-
"""
Created on Mon Jul 24 09:02:10 2017

@author: Emanuele

Program that creates a graphs starting from some initial values such as number of vertices,
number of targets, density (average number of arcs per vertex)
We can pass the adjacency matrix to the graph.py module that can create from that specification a file that
contains all the informations we need to transform it into a .xml file that can be used to automatize
the process of testing on different graphs
We can pass the xml output to solvesaap.py that solves the game ok k sequencial attacks for that graph
"""

import numpy as np
import xml.etree.ElementTree as et
import graph as gr
import shortestpath as sp

graphs_output_path = "C:\\Users\\Ga\\Desktop\\15_5_025\\"; # path to put the graphs' description
graph_tags = list(['G', 'A', 'V', 'DENSITY', 'TOPOLOGY']); # tags that we expect in a graph specification file

ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"; # string used for the salt of each graph's name to avoid collisions between graphs

#==============================================================================
# function that creates random criques (wrt the vertices type)
#   creates a crique of cardinality n and each vertex is a target with probability p
#   if the vertex is a target, it is assigned automatically a value (from min_value to max_value, uniformely at random):
#   and a deadline (uniformely at random, from min_deadline to max_deadline)
#==============================================================================
def generateRandomCrique(n, p, min_value, max_value, min_deadline, max_deadline):
    adj = list([[1 for i in range(n)] for j in range(n)]); # the graph is fully connected
    vertices = list();
    for i in range(n):
        if np.random.rand() <= p:
            deadline = np.random.randint(min_deadline, max_deadline+1);
            value = np.random.randint(10*min_value,101*max_value)/100; # two significative digits for the values
            vertices.append([1, value, deadline]);
        else:
            vertices.append([0,0,0]);
    return adj, vertices;
    
#==============================================================================
# create a file that can be used to start a saap instance with the solvesaap.py module 
#   outputfile is the output filename(path plus filename) where the graph is put in xml format
#==============================================================================
def createFileFromGraph(adj, vertices, density, topology, outputfile):
        g_tags = list();
        list_of_DOM = list([adj, vertices, density, topology]);
        g_tags.append(et.Element("G"));
        #g_tags.append(et.SubElement(root, graph_tags[0])); # G (graph) is the first child node of ROOT
        for j in range(1,len(graph_tags)):
            g_tags.append(et.SubElement(g_tags[0], graph_tags[j])); # every element of the graph is a subelement of the graph itself
            g_tags[j].text = str(list_of_DOM[j-1]);
        tree = et.ElementTree(g_tags[0]);
        tree.write(outputfile);
        
#==============================================================================
# function that generates a random adjacency matrix with the following input
#  n is the size of the matrix
#  p in the probability that a node is connected to another one (we assume indepent the prob that i is connected to j, and i is connected to w different from j)    
# it returns
#  the adjacency matrix M
#==============================================================================
def generateRandMatrix(n, density):
    l = 0;
    M = np.array([[0 for i in range(n)] for j in range(n)]);
    for i in range(n):
        M[i][i] = 1;
    for i in range(n):
        for j in range(l):
            if np.random.rand() <= density:
                M[i][j] = 1;
                M[j][i] = 1;
        l += 1;
    return M;
    
#==============================================================================
# function that returns the adjacent vertices on a line of the adjacency matrix
#==============================================================================
def returnAdjacents(v):
    res = np.array();
    for i in len(v):
        if v[i]:
            np.append(res, i);
    return res;    
    
#==============================================================================
# function that create a little 'salt' to append to each file in order to avoid cases where two graphs
# are different in topology but they have the same elements (i.e. number of vertices, targets, density etc.)
# takes as input
#     the size of the salt, n (5 should be enough)
# returns
#     the salt as a n carachters string (the space of the salt is 5^26)    
#==============================================================================
def generateSalt(n):
    chars=list();
    for i in range(n):
        chars.append(ALPHABET[np.random.randint(len(ALPHABET))]);
    return "".join(chars);
    
"""Test part 
Use this snippet of code to generate n instances of random graphs with a desired connectivity
in the loop you specify how many instances you want
then you specify the parameters of the graph (number of nodes each, probability that a node is a target etc.)
"""
verbose = True;
if verbose:
    edgedensity = 0.25; # edge density
    cardinality = 15; # cardinality of the graphs that we generate
    ptarget = 0.33; # probability that a vertex is a target
    for i in range(5):
        # generate graph info that can be passed to the createFileFromGraph function
        G = gr.generateRandomGraph(generateRandMatrix(cardinality, 0), cardinality, ptarget, 0, 20); # generate the graph (please note that the deadlines are just not informative at this point, since we will change them all with a value that is between diameter and two times the diameter)
        # connect the graph and increase the connectivity
        n = np.size(G.getAdjacencyMatrix()[0]);
        SP, SP_cost = np.array(sp.shortest_path(G.getAdjacencyMatrix(),n,n));
        connected_adj = gr.fromSpToAdjacency(sp.connectMatrix(SP_cost));
        for l in range(np.shape(connected_adj)[0]):
            G.setAdjacents(G.getVertex(l), connected_adj[l]);
        increased_adj = gr.increaseEdgeDensity(connected_adj, edgedensity); # put here the desired edge density
        for l in range(np.shape(increased_adj)[0]):
            G.setAdjacents(G.getVertex(l), increased_adj[l]);
        SP, SP_cost = np.array(sp.shortest_path(G.getAdjacencyMatrix(),n,n));
        diameter = np.matrix.max(SP_cost).astype(int);
        G.setAllDeadlines(diameter, (2*diameter)+1); # set all the deadlines between diamter and two times the diameter
        # now it should be connected
        vertices = list();
        for j in G.getVertices():
            vertices.append([j.isTarget(), j.getValue(), j.getDeadline()]); # create the graph instance
        parsedAdjMatrix = list([list(i) for i in gr.fromSpToAdjacency(G.getAdjacencyMatrix())]); # we need to parse it to put in on file
        createFileFromGraph(parsedAdjMatrix, vertices, G.getDensity(), "random", graphs_output_path+"topology_"+"random"+"_vertices_"+str(cardinality)+"_targets_"+str(len(G.getTargets()))+"_density_"+str(G.getDensity())+"_minvalue_0.1_maxvalue_1_mindeadline_"+str(diameter)+"_maxdeadline_"+str(2*diameter)+"_salt_"+generateSalt(5));