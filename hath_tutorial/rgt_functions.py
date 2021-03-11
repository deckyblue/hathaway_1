"""
This module includes functions to load in MEDPC data and outputs a dataframe. 

Authors: Brett Hathaway & Dexter Kim 
"""

print("I am being executed!")

#main imports 
import os
import pandas as pd
import numpy as np

# plotting imports 
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

# stats imports 
import scipy.stats as stats

#the following line prevents pandas from giving unecessary errors 
pd.options.mode.chained_assignment = None

#---------------------------------------------------------------#

#test 
def square(num): 
    return num^2

#---------------------------------------------------------------#



def load_data(fnames): ##fnames is an argument, and a list of strings (file names) 
    for i,file in enumerate(fnames): ##i means index (0, 1, etc.) // file is the file name (str)
##enumerate takes a list, and makes a new list where the elements are index + something (eg 0, 'BH07_raw_free_S29-30.xlsx')
        if i == 0:
            df = pd.read_excel(fnames[i]) #load in the first file from the 'file_names' list
        else:
            df2 = pd.read_excel(fnames[i]) #load in subsequent file
    #i > 0, and fnames[i] refers to the ith element of the list, fnames
            df = df.append(df2, ignore_index = True) #append it to the first file
    return df

def check_sessions(df): ##checks that the 'Session' column has correct, and non-missing session numbers
    pd.set_option('display.max_rows', None) ##otherwise it will ... the middle rows (only give the head and tail)
    print(df.groupby(['Subject','StartDate','Session'])['Trial'].max())
    pd.set_option('display.max_rows',df.Subject.max()) ##this sets the number of displayed rows to the number of subjects
    
    
    