# -*- coding: utf-8 -*-
"""
Created on Sun Apr 23 17:46:13 2017

@author: Emanuele
"""

import itertools
import numpy as np

#Transofrm a list in the form [indexNumber, IndexNumber, ...] into a dictionary
# which is the composed by the power set of the elements fo the list, up to a cardinality which is at most equal to the number of elements in the list itself
#It is used to turn a list of targets into a vocabulary where each memeber is a set of targets (or an empty list)
#In order to access to an element of the dictionary, for example targets whose indexNumeber is 2,3,5 return the function to a fresh new dictionary
# and call the dictionary in this way 
# name_of_the_dict['2 3 5'] (any permutation of the previous must be passed in order)
# please note that the input string must respect the format '<indexNumber><space><indexNumber>'
#
#The function takes as input:
# the list of elements l that is turned into a dicitonary
# the cardinality till we want to transform the list into a dictionary (e.g. for 4 targets and a cardinality up to 3, pass to the function teh arguments l=list_of_targets,k=3)
#Returns:
# the dictionary
def listToDictionary(l, k):
    powerset = list(); #maybe it's better to use a vocabulary that associates each set of targets under attack to a layer l of the dp matrix M
    dic = dict();
    index = 0;    
    for i in range(k+1): #compute the combination of the parts of the elements in l, till cardinality k 
        powerset.append([p for p in itertools.combinations(l, i)]);
    for i in powerset:
        for j in i:
            regexp = str(j).replace(',', "");
            regexp = regexp.replace("(", "");
            regexp = regexp.replace(")", "");
            dic[regexp] = index;
            index += 1;
    return dic;

#Function that turns a set of integer into an address used by the dictionary created with listToDictionary()
#If the input is [1,4,3,2] it returns the string '1 2 3 4' that can be used as dictionary index
# for a vocabulary created with the function listToDictionary
#Takes as input:
# the list of integers l
#Returns:
# the string used to access to the vocabulary
def listToString(l):
    address = '';
    l = np.sort(l);
    for i in range(len(l)):
        if i==len(l)-1:
            address += str(l[i]);
        else:
            address += str(l[i])+' '; 
    return address;
"""
Little testing to see if the algorithms work as expected
"""  

powerset_targets = list([1,2,3,4]); #create the list of elements
dic = listToDictionary(powerset_targets, 3); #turn the list into a dictionary
print(dic); #print whole the dictionary
print(dic['']); #access to the empty element in the list, we expect 0 as output
print(dic['1 2 4']); #access to the element formed by 2,3 and 4
print(len(dic)); #number of elements in the dictionary
print(dic[listToString([1,3,2])]);