# -*- coding: utf-8 -*-
"""
Created on Fri Apr  7 11:49:43 2017

@author: Emanuele

Algorithm that calculates shortest paths (both costs and relative paths)
between every pair of nodes in a graph
"""

import numpy as np
import networkx as nx

#Floyd--Warshall algorithm to calculate shortest paths (both cost and a shortest path)
#vertex should start with zero
#if you are giving weight above 999 adjust inf in program
#result will be the shortest path matrix and the relative costs
def shortest_path(matrix,m,n):
    inf = 999;
    SP_cost = np.array([[0 for i in range(n)] for i in range(n)]);
    SP = np.array([]);
    for i in range(n):
        for j in range(n):
            if matrix[i][j]==inf:
                matrix[i][j]=0;
    H=nx.Graph(matrix);
    SP_cost = nx.floyd_warshall_numpy(H);
    SP = nx.shortest_path(H);
    return [SP,SP_cost];   
    
#==============================================================================
# function that connects a matrix which entries are the shortest paths between vertices
# takes as input 
#     the shortest paths' matrix M where 
#         an entry of 0 means that the vertex has an auto_edge to intself
#         an entry of 1 means that a vertex is directly connected to another one
#         an entry of more than 1 but less/equal than |V| means that two vertices are connected not directly
#         an entry of 999 means that the two vertices are not connected
# returns 
#     the connected matrix M    
#==============================================================================
def connectMatrix(M):
    n = range(np.shape(M)[0]);
    inf = np.inf; # by default the value of infinite is np.inf
    counter = np.random.randint(np.shape(M)[0]); # this counter should be used to distribute the arcs uniformely
    if 999 in M:
        inf = 999;
    elif np.inf in M:
        inf = np.inf;
    while inf in M:
        for i in np.random.permutation(n):
            if M[counter,i]== inf:
                M[counter,i]=M[i,counter]=1;
                for p in n:
                    if M[counter,p]!=inf:
                        for q in n:
                            if M[p,q]==inf and M[counter,p]!=inf and M[q,i]!=inf:
                                M[p,q]=M[q,p]=M[counter,i]+M[q,i]+M[counter,p]; 
                counter +=1;
                if counter >= np.shape(M)[0]:
                    counter = 0;   
                break;
    return M;
    
"""test part"""
verbose = False;
if verbose:
    M = np.matrix([[0,999,999,1,2,999],[999,0,1,999,999,999],[999,1,0,999,999,999],[1,999,999,0,1,999],[2,999,999,1,0,999],[999,999,999,999,999,0]]);
    print(connectMatrix(M));
    print(shortest_path(np.array(M),6,6)[1]);
    M = np.matrix([[0,999,999],[999,0,999],[999,999,0]]);
    print(connectMatrix(M));
    print(shortest_path(np.array(M), 3, 3)[1]);

