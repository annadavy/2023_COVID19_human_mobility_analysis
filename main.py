# -*- coding: utf-8 -*-
"""
Created on Mon May 15 11:39:30 2023

@author: Anna Davy
"""

import utils

def main():
    
    input_files = utils.DataReader('Global_Mobility_Report.csv','OxCGRT_timeseries_all.xlsx') 
    data,stringency = input_files.read()  
    
    
       