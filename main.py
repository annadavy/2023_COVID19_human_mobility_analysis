# -*- coding: utf-8 -*-
"""
Created on Mon May 15 11:39:30 2023

@author: Anna Davy
"""

import utils
from sklearn.cluster import KMeans


def main():
    
    input_files = utils.DataReader('Global_Mobility_Report.csv','OxCGRT_timeseries_all.xlsx') 
    data,stringency = input_files.read()  
    
    processor=utils.DataPreProcessor(data,stringency)
    
    first_date, last_date, base_date = processor.get_dates()   
       
                
    user_choice=utils.menu(choices=['1. All available dates from '+str(first_date)+" to "+str(last_date),
                          '2. Choose dates from calendar'],
                             title=" Please select an option: ",nr_rows=30)[0]
    
    if user_choice=='2. Choose dates from calendar':
        
        per_dates = utils.PeriodExtract(base_date, base_date)
        from_date = per_dates.todate
        to_date = per_dates.frdate
        
        if from_date < first_date:
            from_date = first_date
            
        if to_date > last_date:
            to_date = last_date
            
        data = processor.format_main_data(from_date,to_date)
        
        stringency = processor.format_stringency(from_date,to_date)
        
        if stringency.shape[1]<3:
            
            print ('Stringency data not available for the selected period.')
            
    else:
            
        data, date_dict, dict_weeks = processor.format_main_data(first_date, last_date)
        stringency=processor.format_stringency(first_date, last_date, date_dict, dict_weeks)  

    data_final =processor.group_data()
    
    model = KMeans(n_clusters=4).fit(data_final.drop(['country','2weeks'],axis=1))
    labels = model.predict(data_final.drop(['country','2weeks'],axis=1))


    data_final['group']=labels

    
    
