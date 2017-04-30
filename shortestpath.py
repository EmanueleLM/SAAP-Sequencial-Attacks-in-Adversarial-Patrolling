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