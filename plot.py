# -*- coding: utf-8 -*-
"""
Created on Sat Jul 22 10:33:02 2017

@author: Emanuele


This file's purpose is to take as input an aggregate file as a set of rows that contain each data
about a specific instance of a solved saap, and plot some graph
"""

import os.path
import numpy as np
import pylab as pl

input_aggregate_path = "C:\\Users\\Ga\\Desktop\\"; # input path for the aggregate file
input_aggregate = "aggregate.dat"; # name of the aggregate file
aggregate_prefix = ['NAME', 'TOPOLOGY', 'NUM_V', 'NUM_T', 'K', 'EXEC_TIME', 'UTILITY', 'LENGTH_EQ_PATH', 'AVG_LENGTH_PATH', 'DENSITY']; # prefix for the aggregate file: specifies each entry on that file

#==============================================================================
# this function fixes k (i.e. the number of resources available to A)
# and plot the execution time of all the instances available in the 
# aggregate file
#==============================================================================
def plotExecTimeByNumberOfNodes(k):
    content = list();
    if not(os.path.isfile(input_aggregate_path + input_aggregate)):
        print("File does not exists: exit");
        exit();
    else:
        with open(input_aggregate_path + input_aggregate) as f:
            content = f.readlines()[1:];
    # you may also want to remove whitespace characters like `\n` at the end of each line
    content = sanitizeString(content); 
    exec_time = np.array([float(t[5]) for t in content if int(t[4])==k]); # save all the exec_time for a given k in a numpy array (i.e. the Y axis points)
    number_of_nodes = np.array([int(n[2]) for n in content if int(n[4])==k]); # save all the number_of_nodes for a given k in a numpy array (i.e. the X axis points)
    #print(exec_time, number_of_nodes); # print the vectors to be plotted
    pl.plot(number_of_nodes, exec_time, 'ro');
    
#==============================================================================
# this function plot the execution time of all the instances available in the 
# aggregate file using as X axis the number of resources k available to A
# this graph is very important since we expect an exponential behavior of exec_time
# wrt the free variable 'number of resources'
#==============================================================================
def plotExecTimeByNumberOfResources():
    content = list();
    if not(os.path.isfile(input_aggregate_path + input_aggregate)):
        print("File does not exists: exit");
        exit();
    else:
        with open(input_aggregate_path + input_aggregate) as f:
            content = f.readlines()[1:];
    # you may also want to remove whitespace characters like `\n` at the end of each line
    content = sanitizeString(content); 
    exec_time = np.array([float(t[5]) for t in content]); # save all the exec_time for a given k in a numpy array (i.e. the Y axis points)
    number_of_nodes = np.array([int(n[4]) for n in content]); # save all the number_of_nodes for a given k in a numpy array (i.e. the X axis points)
    # print(exec_time, number_of_nodes);
    pl.plot(number_of_nodes, exec_time, 'go');
    
#==============================================================================
# this function fixes ranges for the number of nodes and targets on the graphs instances
#   i.e. min_V and min_T are the minimum numbers of respectively vertices and targets on G
#   while max_V and max_T are the maximum numbers of respectively vertices and targets on G
# and plot the utility of all the instances available in the aggregate file
#==============================================================================
def plotUtilityByDensity(min_V, max_V, min_T, max_T):
    content = list();
    if not(os.path.isfile(input_aggregate_path + input_aggregate)):
        print("File does not exists: exit");
        exit();
    else:
        with open(input_aggregate_path + input_aggregate) as f:
            content = f.readlines()[1:];
    # you may also want to remove whitespace characters like `\n` at the end of each line
    content = sanitizeString(content); 
    utilities = np.array([int(u[6]) for u in content if int(u[2])<=max_V and int(u[2])>=min_V and int(u[3])<=max_T and int(u[3])>=min_T]); # save all the exec_time for a given k in a numpy array (i.e. the Y axis points)
    densities = np.array([float(d[9]) for d in content if int(d[2])<=max_V and int(d[2])>=min_V and int(d[3])<=max_T and int(d[3])>=min_T]); # save all the number_of_nodes for a given k in a numpy array (i.e. the X axis points)
    print(utilities, densities); # print the vectors to be plotted
    pl.plot(utilities, densities, 'yo');
    
#==============================================================================
# function that sanitizes the specific content of the aggregate .dat file  
#   takes as input the file in rows, except the prefix row
#   returns the file without special charachters
#   please note that there's no need to use regexo for this specific purpose since the eliminations are few and very simple
#==============================================================================
def sanitizeString(content):
    content = [x.strip('\n') for x in content];  # eliminate newlines
    content = [x.replace("'", '') for x in content]; # eliminate the ' character 
    content = [x.replace("[", '') for x in content]; # eliminate the square bracket '[' character 
    content = [x.replace("]", '') for x in content]; # ..
    content = [x.split(',') for x in content]; # split the elements in a list fashion
    return content;
        
"""
Little testing to see if the algorithms work as expected
"""    
verbose = True; # this variable controls whether the output is printed
if verbose:
    #plotExecTimeByNumberOfNodes(3);
    plotExecTimeByNumberOfResources();
    #plotUtilityByDensity(0,10,0,10);
    