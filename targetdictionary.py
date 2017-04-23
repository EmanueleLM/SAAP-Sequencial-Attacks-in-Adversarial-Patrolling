# -*- coding: utf-8 -*-
"""
Created on Sun Apr 23 17:46:13 2017

@author: Emanuele
"""

import itertools

#Transofrm a list in the form [indexNumber, IndexNumber, ...] into a dictionary
# which is the composed by the power set of the elements fo the list, up to a cardinality which is at most equal to the number of elements in the list itself
#It is used to turn a list of targets into a vocabulary where each memeber is a set of targets (or an empty list)
#In order to access to an element of the dictionary, for example targets whose indexNumeber is 2,3,5 return the function to a fresh new dictionary
# and call the dictionary in this way 
# name_of_the_dict['2 3 5'] (any permutation of the previous must be passed in order)
# TODO: make it possible to pass to the dictionary every permutation
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
    
"""
Little testing to see if the algorithms work as expected
"""  

powerset_targets = list([1,2,3,4]); #create the list of elements
dic = listToDictionary(powerset_targets, 3); #turn the list into a dictionary
print(dic); #print whole the dictionary
print(dic['']); #access to the empty element in the list, we expect 0 as output
print(dic['2 3 4']); #access to the element formed by 2,3 and 4
