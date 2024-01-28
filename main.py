# -*- coding: utf-8 -*-
"""
Created on Mon May 15 11:39:30 2023

@author: Anna Davy
"""

import utils
from sklearn.cluster import KMeans


def main():
    """
    The main function of a data processing and analysis pipeline focused on global mobility and stringency data.

    Steps:
    1. Reads input data from 'Global_Mobility_Report.csv' and 'OxCGRT_timeseries_all.xlsx' using a custom DataReader class.
    2. Preprocesses the data using the DataPreProcessor class, extracting date-related information.
    3. Presents the user with a menu to choose between analyzing data for all available dates or a specific date range.
    4. If a specific date range is chosen, further processes the data to conform to the selected dates and checks the availability of stringency data.
    5. Formats and groups the main data and stringency data based on the user's selection.
    6. Applies a KMeans clustering algorithm to the processed data, assigning cluster labels.
    7. Appends the cluster labels to the final data and writes the output to an Excel file using the DataWriter class.

    Note:
    - The function is designed to be executed as the primary entry point of a script, with the main logic conditional on `__name__ == "__main__"`.
    - Utilizes custom utility classes (DataReader, DataPreProcessor, DataWriter) for various data handling tasks.
    - Employs a KMeans clustering model from the sklearn library to analyze the processed data.
    - Handles user input for date selection and manages data processing accordingly.
    - Ensures compatibility of selected dates with the available data range.
    """
    
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
    
    writer=utils.DataWriter(data_final)
    
    writer.write_to_excel()

if __name__ == "__main__":
    main()    
    
