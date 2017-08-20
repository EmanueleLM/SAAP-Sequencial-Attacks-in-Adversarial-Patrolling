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
input_aggregate = "copia.dat"; # name of the aggregate file
aggregate_prefix = ['NAME', 'TOPOLOGY', 'NUM_V', 'NUM_T', 'K', 'EXEC_TIME', 'UTILITY', 'V0', 'DENSITY']; # prefix for the aggregate file: specifies each entry on that file

output_image_file = "C:\\Users\\Ga\\Desktop\\plot\\img\\";
output_pdf_file = "C:\\Users\\Ga\\Desktop\\plot\\pdf\\";

#==============================================================================
# this function fixes k (i.e. the number of resources available to A)
# and plot the execution time of all the instances available in the 
# aggregate file
# percentage_min/percentage_max is the ratio between |T|/|V| that we consider to plot (e.g.if you put both as 0.5, this function will plot just the instances where |T|/|V|==0.5)
#==============================================================================
def plotExecTimeByNumberOfVertices(k, percentage_min, percentage_max):
    content = list();
    if not(os.path.isfile(input_aggregate_path + input_aggregate)):
        print("File does not exists: exit");
        exit();
    else:
        with open(input_aggregate_path + input_aggregate) as f:
            content = f.readlines()[1:];
    # you may also want to remove whitespace characters like `\n` at the end of each line
    content = sanitizeString(content); 
    exec_time = np.array([]);
    number_of_vertices = np.sort(np.unique(np.array([[int(n[2]) for n in content if int(n[4])==k]]))); # order the number of vertices in ascending order, in a numpy.unique array (the x axis)
    for n in number_of_vertices:
        exec_time = np.append(exec_time, np.average([float(t[5]) for t in content if int(t[2])==n and int(t[4])==k and float(int(t[3])/int(t[2]))>=percentage_min and float(int(t[3])/int(t[2]))<=percentage_max])); # save all the exec_time for a given k in a numpy array (i.e. the Y axis points)
    #print(exec_time, number_of_vertices);
    pl.plot(np.append(0,number_of_vertices), np.append(0,exec_time), max(number_of_vertices)+10, max(exec_time));
    pl.legend(['|T|/|V| in [' + str(percentage_min) + ';' + str(percentage_max) + ']'], loc='best');
    pl.xlabel('|V|');
    pl.ylabel('time [s]');
    pl.title('Exec-time wrt number of vertices, fixed density, k='+str(k));
    filename = "exectime_vertices_targets_ratio_"+str(percentage_min)+"_"+str(percentage_max)+"_resources_"+str(k); # filename
#    pl.savefig(output_image_file+filename+".png", bbox_inches='tight');
#    pl.savefig(output_pdf_file+filename+".pdf", bbox_inches='tight');    
    
#==============================================================================
# this function fixes k (i.e. the number of resources available to A)
# and plot the execution time of all the instances available in the 
# aggregate file
# it plots the execution time for a given instance of V vertices, if we modify the number of targets from 0 to |T|=|V| at step 'step'
#==============================================================================
def plotExecTimeByVerticesTargetsRatio(k, V, step):
    content = list();
    if not(os.path.isfile(input_aggregate_path + input_aggregate)):
        print("File does not exists: exit");
        exit();
    else:
        with open(input_aggregate_path + input_aggregate) as f:
            content = f.readlines()[1:];
    # you may also want to remove whitespace characters like `\n` at the end of each line
    content = sanitizeString(content); 
    exec_time = np.array([]);
    number_of_targets = np.array([i for i in range(step, V+step, step)]); # order the number of vertices in ascending order, in a numpy.unique array (the x axis)
    for n in range(step, V+step, step):
        exec_time = np.append(exec_time, np.average([float(t[5]) for t in content if int(t[2])==V and int(t[4])==k and int(t[3])==n])); # save all the exec_time for a given k in a numpy array (i.e. the Y axis points)
    #print(exec_time, number_of_vertices);
    pl.plot(np.append(0,number_of_targets), np.append(0,exec_time), max(number_of_targets)+10, max(exec_time));
    pl.xlabel('|T|');
    pl.ylabel('time [s]');
    pl.title('Exec-time wrt vertices-targets ratio, |V|= '+ str(V) + ' ,k='+str(k));
    filename = "exectime_vertices_"+str(V)+"_"+"_step_targets_"+str(step)+"_resources_"+str(k); # filename
#    pl.savefig(output_image_file+filename+".png", bbox_inches='tight');
#    pl.savefig(output_pdf_file+filename+".pdf", bbox_inches='tight');
    
#==============================================================================
# this function plot the execution time of all the instances available in the 
# aggregate file using as X axis the number of resources k available to A
# this graph is very important since we expect an exponential behavior of exec_time
# wrt the free variable 'number of resources'
# percentage_min/percentage_max is the ratio between |T|/|V| that we consider to plot (e.g.if you put both as 0.5, this function will plot just the instances where |T|/|V|==0.5)
# k_min and k_max are the max and min number of resources (extremes included) taken into consideration (e.g. k_min=2 and k_max=5 consider k=2,3,4,5)
#
# please note that we impose a logarithmic scale, (see comments for strange 1 instead of zero appearing in the code)
#   and you need to have at least a working solved saap for each k you want to test (this means that if you test vertices |V|={5,10,15} you NEED at least a line of solved saap for each k, for each number of vertices)    
#==============================================================================
def plotExecTimeByNumberOfResources(percentage_min, percentage_max, k_min, k_max):
    content = list();
    if not(os.path.isfile(input_aggregate_path + input_aggregate)):
        print("File does not exists: exit");
        exit();
    else:
        with open(input_aggregate_path + input_aggregate) as f:
            content = f.readlines()[1:];
    # you may also want to remove whitespace characters like `\n` at the end of each line
    content = sanitizeString(content); 
    number_of_vertices = np.sort(np.unique(np.array([[int(n[2]) for n in content if int(n[4])==k_min]]))); # order the number of vertices in ascending order, in a numpy.unique array (the x axis)
    number_of_vertices = np.append(0, number_of_vertices); 
    for k in range(k_min, k_max+1):    
        exec_time = np.array([1]); # logarithmic scale! so we need a 1 not the allow the log to explode!
        for n in number_of_vertices[1:]:
            exec_time = np.append(exec_time, np.average([float(t[5]) for t in content if int(t[2])==n and int(t[4])==k and float(int(t[3])/int(t[2]))>=percentage_min and float(int(t[3])/int(t[2]))<=percentage_max])); # save all the exec_time for a given k in a numpy array (i.e. the Y axis points)
        #print(exec_time, number_of_vertices);
        pl.plot(number_of_vertices, exec_time, max(number_of_vertices)+10, max(exec_time));
        pl.legend(['k in [' + str(k_min) + ';' + str(k_max) + ']'], loc='best');
        pl.xlabel('|V|');
        pl.ylabel('time [s]');
        pl.yscale('log');
        pl.title('Logarithmic-execution time wrt number of vertices');
        
#==============================================================================
# this function plots a box-plot('grafo a baffi') wrt the utility of the Defender on a series of instances wrt the number of resources
#  of the Attacker
#==============================================================================
def plotUtilityByResources(k):
    content = list();
    if not(os.path.isfile(input_aggregate_path + input_aggregate)):
        print("File does not exists: exit");
        exit();
    else:
        with open(input_aggregate_path + input_aggregate) as f:
            content = f.readlines()[1:];
    # you may also want to remove whitespace characters like `\n` at the end of each line
    content = sanitizeString(content); 
    data = list();
    number_of_vertices = np.sort(np.unique(np.array([[int(n[2]) for n in content if int(n[4])==k]]))); # order the number of vertices in ascending order, in a numpy.unique array (the x axis)
    label = [str(i) for i in number_of_vertices];  
    for n in number_of_vertices:
        data.append(np.array([float(t[6]) for t in content if int(t[2])==n and int(t[4])==k]));
    pl.boxplot(data, labels=label); # save all the exec_time for a given k in a numpy array (i.e. the Y axis points)
    pl.xlabel('|V|');
    pl.ylabel('utility');
    pl.title('Boxplot: utility wrt number of vertices with '+ str(k)+' resources');
    
#==============================================================================
# this function plots a box-plot('grafo a baffi') wrt the utility of the Defender on a series of instances wrt the number of resources
#  of the Attacker, wrt the ratio between the vertices in a Graph and targets |T|/|V|
#==============================================================================
def plotUtilityByVerticesTargetsRatio(k, ratio_min, ratio_max):
    content = list();
    if not(os.path.isfile(input_aggregate_path + input_aggregate)):
        print("File does not exists: exit");
        exit();
    else:
        with open(input_aggregate_path + input_aggregate) as f:
            content = f.readlines()[1:];
    # you may also want to remove whitespace characters like `\n` at the end of each line
    content = sanitizeString(content); 
    data = list();
    number_of_vertices = np.sort(np.unique(np.array([[int(n[2]) for n in content if int(n[4])==k]]))); # order the number of vertices in ascending order, in a numpy.unique array (the x axis)
    label = [str(i) for i in number_of_vertices];  
    for n in number_of_vertices:
        data.append(np.array([float(t[6]) for t in content if int(t[2])==n and int(t[4])==k and float(int(t[3])/int(t[2]))>=ratio_min and float(int(t[3])/int(t[2]))<=ratio_max]));
    pl.boxplot(data, labels=label); # save all the exec_time for a given k in a numpy array (i.e. the Y axis points)
    pl.xlabel('|V|');
    pl.ylabel('utility');
    pl.title('Boxplot: utility wrt number of vertices with '+ str(k)+' resources');
    filename = "utility_wrt_vertices_"+str(number_of_vertices)+"_resources_"+str(k); # filename
    pl.savefig(output_image_file+filename+".png", bbox_inches='tight');
    pl.savefig(output_pdf_file+filename+".pdf", bbox_inches='tight'); 
    
#==============================================================================
# this function fixes the number of vertices V and Targets (between min_T and max_T, included)
# and plot the execution time of all the instances available in the aggregate file by using different graph densities
# k_min and k_max are the number of resources taken under consideration (included, and e.g. if you specify min_k=2 and max_k=4 it will plot 3 different plots (k=2,3,4))
#==============================================================================
def plotExecTimeByDensity(k_min, k_max, V, min_T, max_T):
    content = list();
    if not(os.path.isfile(input_aggregate_path + input_aggregate)):
        print("File does not exists: exit");
        exit();
    else:
        with open(input_aggregate_path + input_aggregate) as f:
            content = f.readlines()[1:];
    # you may also want to remove whitespace characters like `\n` at the end of each line
    content = sanitizeString(content); 
    densities = np.sort(np.unique(np.array([[float(n[8]) for n in content if int(n[4])==k_min and int(n[2])==V and int(n[3])>=min_T and int(n[3])<=max_T]]))); # order the number of vertices in ascending order, in a numpy.unique array (the x axis)
    densities = np.append(0, densities); 
    for k in range(k_min, k_max+1):    
        exec_time = np.array([0]);
        for n in densities[1:]:
            exec_time = np.append(exec_time, np.average([float(t[5]) for t in content if float(t[8])==n and int(t[4])==k and int(t[2])==V and int(t[3])>=min_T and int(t[3])<=max_T])); # save all the exec_time for a given k in a numpy array (i.e. the Y axis points)
    #print(exec_time, number_of_vertices);
    pl.plot(densities, exec_time, 1, max(exec_time));
    pl.legend(['k in [' + str(k_min) + ';' + str(k_max) + ']'], loc='best');
    pl.xlabel('edge-density');
    pl.ylabel('time [s]');
    pl.title('Execution time wrt edge-density');
    
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
    #plotExecTimeByNumberOfVertices(3, 0, 1);
    #plotExecTimeByVerticesTargetsRatio(2, 20, 5);
    #plotExecTimeByNumberOfResources(0,1,2,3);
    #plotUtilityByResources(2);
    #plotExecTimeByDensity(2,2,10,0,10);
    plotUtilityByVerticesTargetsRatio(3, 0, 1);