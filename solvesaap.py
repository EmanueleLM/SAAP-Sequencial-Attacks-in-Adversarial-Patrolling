# -*- coding: utf-8 -*-
"""
Created on Wed Jul 19 14:33:27 2017

@author: Emanuele

Solve SAAP() script:
takes as input a series of graphs encoded in a XML file filled up with an adjacency matrix A, and a description of each node
encoded as type of node (simple vertex or target), its value (0 if it's not a target, between 0 and 1
if it's a target) and a deadline (0 if it's a vertex, greater than zero and integer if it's a target)
"""
import pathfinder as pf
import numpy as np
import xml.etree.ElementTree as et
from xml.dom import minidom
import graph as gr
import os.path
import time

graphs_input_path = "C:\\Users\\Ga\\Desktop\\instances\\test\\"; # path to find the graphs' description
output_path  = "C:\\Users\\Ga\\Desktop\\"; # path to store the output in pseudo-xml format
graphs = list(); # list that contains the name of each graph file in txt format
k = 4; # number of resources we want the solver solves for each instance of the graphs specified in graphs
# complete description of each tag in our xml file (intermediate aggregate file)
#
# .. TO_DO
#
graph_tags = list(['G', 'A', 'VERTICES', 'V0', 'T0', 'NUM_V', 'NUM_T', 'DENSITY', 'TOPOLOGY']);
other_tags = list(['K', 'PATH', 'COVERED', 'LOST', 'HISTORY', 'UTILITY', 'EXEC_TIME', 'ROUTES']);

aggregate_filepath = "C:\\Users\\Ga\\Desktop\\"; # filepath to the aggregate (.dat) file
aggregate_output = "aggregate.dat"; # name of the aggregate file
aggregate_prefix = ['NAME', 'TOPOLOGY', 'NUM_V', 'NUM_T', 'K', 'EXEC_TIME', 'UTILITY', 'LENGTH_EQ_PATH', 'AVG_LENGTH_PATH', 'DENSITY']; # prefix for the aggregate file: specifies each entry on that file


#==============================================================================
# function that invokes pathfinder for a given specification of the SAAP game 
#     and solves it for the instances of sequencial attacks that go from 1 to k
#     creates a "dom"-like structure that is used to store all the salient elements of the saap solution
# takes as input
#   the file, filepath, where there's the graph specification
#   the initial vertex v
#   the initial target under attack
#   number of resources avilable to A
# returns a list of the files that contains the results of the various saap instances
#==============================================================================
def solveSAAP(filepath, v, t, k):
    files = list();
    G, vertices, density, topology = createGraphFromFile(filepath);    

    start_time = time.time(); # start measuring the time of execution (we don't care if we have a small overhead since we don't start measuring int in the true function, that's because eery instance will have the same (little) overhead)
    #routes = pf.PathFinder(G, v, t, k); # solve the game for a specific instance with a given number of resources 'k' for the Attacker
    exec_time = (time.time() - start_time); # calculate execution time (little overhead introduced by returning of the function, still not important since we are facing an exponential problem)        
    # write all the stuff to a file in a xml pseudo-format
    g_tags = list();
    o_tags = list();
    root = et.Element("ROOT");
    g_tags.append(et.SubElement(root, graph_tags[0])); # G (graph) is the first child node of ROOT
    for j in range(1,len(graph_tags)):
        g_tags.append(et.SubElement(g_tags[0], graph_tags[j])); # every element of the graph is a subelement of the graph itself
    for j in range(len(other_tags)):
        o_tags.append(et.SubElement(root, other_tags[j]));
    # follow the order in graph_tags to see what's the content of each of the following element
    g_tags[1].text = str(list(G.getAdjacencyMatrix())); # adjacency matrix
    g_tags[2].text = str(vertices); # specification of each vertex
    g_tags[3].text = str(v); # initila vertex
    g_tags[4].text = str(t); # initial target
    g_tags[5].text = str(len(vertices)); # number of vertices on the graph
    g_tags[6].text = str(len(G.getTargets())); # number of targets on the graph
    g_tags[7].text = str(G.getDensity()); # edge density
    g_tags[8].text = topology; # topology of the graph
    # follow the order in other_tags to see what's the content of each of the following element
    o_tags[0].text = str(k+1); # number of resources
    # fill this section up with the other o_tags
    # o_tags[1].text =
    # o_tags[2].text =
    # o_tags[3].text = 
    # ...
    o_tags[6].text = str(exec_time); # execution time
    #o_tags[7].text = str(routes); # list of all the routes generated by the saap instance
    tree = et.ElementTree(root);
    files.append(output_path+"_topology_"+topology+"_vertices_"+str(len(G.getVertices()))+"_density_"+str(G.getDensity())+"_V0_"+str(v)+"_T0_"+str(t)+"_resources_"+str(k+1));
    tree.write(files[-1]); # write on file
    
    return files;
#==============================================================================
# function that create a graph G from a file that specifies the adjacency matrix at first
#     the initial vertex v, the first target under attack t and how the graph is (vertices, targets, their values and deadlines..)
#     the format of the file is the following and in this order: 
#         adjacency matrix A specified as [[1,0],[0,1]]
#         a list of each vertex charachteristic as [vertex/target, value, deadline] where vertex=0, target=1
#             , value is a real number in [0,1](0 is for vertices)
#             , deadline is a natural number (0 for vertices, any other for targets)
#             , e.g. [0,0,0] --> vertex, [1, 0.5, 10] --> target with 0.5 as value, 10 as deadline
#             , an example of a 3*3 vertices' specification is [[0,0,0],[1,1,4],[1,0.3,5]]
#          edge density defined as density = 2|E|/|V|(|V|-1)    
##         topology of the graph, the possible choices are {'graph', 'line', 'star', 'crique', ..}
#     all this stuff must be encoded in a pseudo-xml format (just to be a little more polite and clean)
#     even if you can find an example of psuedo-xml graph in the repo on github, here's one:

#     <G>
#         <A>[[1,1,1],[1,1,1],[1,1,1]]</A>
#         <V>[[1,0.3,3],[0,0,0],[1,0.8,12]]</V>
#         <DENSITY>0.3</DENSITY>
#         <TOPOLOGY>graph</TOPOLOGY>
#     </G>

#     the previous example specifies a fully connected graph with 3 vertices, 2 targets (index 0 and 2) and a vertex (index 1)
#     the density is set to 0.3
#     the topology of the graph ('graph' if it's not a specific topology, 'crique', 'line', 'start' etc. otherwise)
# the function returns 
#       a graph G, 
#       the vertices that compose the graph (each one specify if it's a vertex or a target, its value and its deadline)
#       the density of the graph
#       the topology of the graph
#==============================================================================
def createGraphFromFile(filepath):
#    elements_check = ["A", "V", "DENSITY", "TOPOLOGY"]; # elements to check if all the graph's elements are present in the file 
    tree = et.parse(filepath);
    root = tree.getroot();
    # create the empty Graph and the adjacency matrix by parsing the file (thanks to eval, even if I should not use it :P)
    adj_matrix = np.array(eval(root[0].text)); 
    vertices = np.array(eval(root[1].text)); 
    V = list();
    # for each vertex create the graph G
    for v in vertices:
        V = np.append(V, gr.Vertex(int(v[0]), float(v[1]), int(v[2])));
    G = gr.Graph(np.array(V));
    n = 0;
    for v in vertices:
        G.setAdjacents(V[n], np.array(adj_matrix[n]));
        n += 1;       
    return [G, vertices, float(root[2].text), root[3].text]; # return the graph, the vertices, the density and the topology
#==============================================================================
# function that given a xml result coming from a saap solution, prints on screen all the xml file 
#     takes as input the filepath of the xml file
#     returns none
#     please note that if verbose is set to True it will print out all the routes generated (usually a lot)
#     otherwise it does not print them
#==============================================================================
def printSaapDOM(filepath, verbose):
    root = et.parse(filepath).getroot();
    for j in root[0]:
        print(j.tag);
        print(j.text, "\n");  
    if verbose:
        nop = len(root);
    else:
        nop = -1;
    for i in root[1:nop]:
        print(i.tag);
        print(i.text, "\n");
#==============================================================================
# function that "prettifies" the output
#    takes as input the element in ElementTree to be prettyfied
#    returns the string prettified
#==============================================================================
def prettify(elem):
    rough_string = et.tostring(elem, 'utf-8');
    reparsed = minidom.parseString(rough_string);
    return reparsed.toprettyxml(indent="\t"); 
#==============================================================================
# function that returns the root of the xml file, given the path of the xml file
#     it takes as input the xml file
#     it returns the root element of the file
#==============================================================================
def getRootElement(filepath):
    return et.parse(filepath).getroot();
#==============================================================================
# function that turns a xml file into aggregate data, useful to plot the data
#     takes as input the result of a saap instance as filepath + filename
#     returns a new line in the aggregate.dat file file that is composed in this way:
#         filename num_nodes num_targets resources exec_time utility length_eq_path average_length_path density 
#==============================================================================
def fromXml2Aggregate(filepath, filename):
    data_to_find = ['TOPOLOGY', 'NUM_V', 'NUM_T', 'K', 'EXEC_TIME', 'UTILITY', 'LENGTH_EQ_PATH', 'AVG_LENGTH_PATH', 'DENSITY'];
    result = list([filename]);
    root = et.parse(filepath+filename).getroot();
    for i in data_to_find:
        if root[0].find(str(i)) != None:
            result.append(root[0].find(i).text);
        else:
            if root.find(i) != None:
                result.append(root.find(i).text);
            else:
                result.append('None');
    return result;   
#==============================================================================
# function that creates from a graph specification a string that is used to feed the 
#     function that create the aggregate file from the various xml instances of saaps
#     takes as input
#         file, which is the filename (filepath+filename)
#     returns
#         the filename of the xml file to be used to feed the aggregate file
#==============================================================================
def fromGraphToXmlName(file):
    G, vertices, v, t, topology = createGraphFromFile(file); 
    filename = "_topology_"+topology+"_vertices_"+str(len(G.getVertices()))+"_density_"+str(G.getDensity())+"_V0_"+str(v)+"_T0_"+str(t);
    return filename;
    
"""
Little testing to see if the algorithms work as expected
"""    
verbose = True; # this variable controls whether the output is printed
if verbose:
    # extract elements from the graph file
    for inputgraph in os.listdir(graphs_input_path):
        print(inputgraph);
        [printSaapDOM(i, True) for i in solveSAAP(graphs_input_path+inputgraph,0,0,3)];    
        if not(os.path.isfile(aggregate_filepath + aggregate_output)): # if the file does not exists, create it with the prefix
            prefix = str();
            for i in aggregate_prefix:
                prefix += str(i)+'\t';
            f = open(aggregate_filepath + aggregate_output, "w"); # create the file with the prefix
            f.write(prefix + '\n');
        else:
            f = open(aggregate_filepath + aggregate_output, "a"); # open in appendix mode
        # write all the results row by row, using the fromGraphToXmlName function as "feeder" to the fromXml2Aggregate function, plus the number of resources of a given instance
        for i in range(1,k+1):
            line = fromXml2Aggregate("C:\\Users\\Ga\\Desktop\\", fromGraphToXmlName(graphs_input_path+inputgraph)+"_resources_"+str(i));
            f.write(str(line)+'\n');        
        f.close(); # close the file