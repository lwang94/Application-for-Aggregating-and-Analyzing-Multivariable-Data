# -*- coding: utf-8 -*-
"""
Created on Thu Jan 24 22:38:26 2019

@author: lawre
"""

import numpy as np
import scipy.signal as sig
import itertools

def custom_func(dictionary):
    """the custom function in Matrix_Fun page. Should always return the dictionary that contains the matrix and its new parameters"""
    return dictionary


def custom_fit(x, p):
    """the custom function for fitting in Function_Fitting page."""
    x=np.array(x) #ensures x-values are in array and not list to make writing the function easier
    return p[0]*x+p[1]*(x**2)+p[2]*(x**3) #fits data to polynomial of order=3 (dummy function)