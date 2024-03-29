# -*- coding: utf-8 -*-
"""
Created on Fri Dec  4 10:46:25 2020

@author: Anna Davy
"""
import pandas as pd
import numpy as np
import sys
import tkinter as tk
from tkinter import messagebox
import warnings
warnings.filterwarnings("ignore")
from datetime import datetime, date
from tkinter import ttk
from tkcalendar import Calendar
from datetime import datetime as second_datetime
import dateparser



class DataReader:
    """
    A class to read data from different file formats.

    This class is designed to handle the reading of data from multiple files,
    supporting formats like CSV and Excel (xlsx). It takes multiple file paths
    as input and provides methods to read these files into Pandas dataframes.

    Attributes:
        files (tuple): A tuple containing file paths provided during class instantiation.
    """
    
    def __init__(self,*files):
        
        self.files=(files)
        
    def read(self):
        
        for file in self.files:
            
            if file.endswith('.csv'):
                data= pd.read_csv(file)
            elif file.endswith('.xlsx'):
                stringency=pd.read_excel(file)
                
        return data,stringency     
    
class DataPreProcessor:
    """
    A class for preprocessing global mobility and stringency data for further analysis.

    Attributes:
        data (DataFrame): The initial data set containing global mobility information.
        stringency (DataFrame): The initial data set containing stringency measures.

    The preprocessing includes:
    - Removing specific countries/regions from the data set.
    - Renaming certain countries to maintain consistency.

    Methods:
    - get_dates(): Extracts the first and last dates from the mobility data and calculates a base date.

    Usage:
    The class is initialized with two data frames: `data` and `stringency`. It automatically performs the necessary preprocessing steps on instantiation. 
    The `get_dates` method can be used to retrieve key date information relevant for subsequent analysis.

    Example:
    ```
    processor = DataPreProcessor(mobility_data, stringency_data)
    first_date, last_date, base_date = processor.get_dates()
    ```

    Note:
    - The list of countries to be removed and the country renaming dictionary are hardcoded within the class.
    - This class is designed to work with specific data structures and may require modification for different data sets.
    """
    
    def __init__(self, data, stringency):
        
        self.data=data
        self.stringency=stringency
        
        to_be_removed=['Antigua and Barbuda','Aruba','Liechtenstein','North Macedonia',
                       'Puerto Rico','Réunion','Taiwan']

        self.data=self.data[~self.data.country_region.isin(to_be_removed)]

        country_dict={'The Bahamas':'Bahamas',"Côte d'Ivoire":"Cote d'Ivoire",
                      'Czechia':'Czech Republic','Guinea-Bissau':'Guinea',
                   'Kyrgyzstan':'Kyrgyz Republic','Slovakia':'Slovak Republic'}

        self.data['country_region']=self.data['country_region'].replace(country_dict)
        
    def get_dates(self):
        
        first_date=second_datetime.strptime(self.data.date.unique().tolist()[0], "%Y-%m-%d").date()       
        last_date=second_datetime.strptime(self.data.date.unique().tolist()[-1], "%Y-%m-%d").date()
        base_date=datetime.strptime(str(datetime.now().year - 10) + "/12/01",
                                      "%Y/%m/%d").date()

        return first_date, last_date, base_date
    
    @staticmethod
    def format_date(date_input):
        
        try:
                        
            date_form=second_datetime.strptime(date_input, "%Y-%m-%d").date()
        
        except:
            
            date_form=second_datetime.strptime(date_input, "%d%b%Y").date() 
       
        return date_form
        
    
    def format_stringency(self,from_date,to_date,date_dict,dict_weeks):
        
        column_names=[]
        
        for column in self.stringency.columns:
            
            try:
                date_form=self.format_date(column)
                if date_form<from_date or date_form>to_date: 
                    self.stringency.drop(columns=[column],inplace=True)                    
                else:
                    column_names.append(date_dict[date_form])

            except:
                if ('code').lower() in column:
                    column='Code'
                if ('name').lower() in column:
                    column='Country'
                column_names.append(column)
                
        self.stringency.columns=column_names
        self.stringency.drop('Code',1,inplace=True)

        self.stringency=self.stringency.T

        self.stringency.columns=self.stringency.iloc[0].tolist()
        self.stringency=self.stringency[1:]
        self.stringency=self.stringency.reset_index()
        self.stringency=self.stringency.rename(columns = {'index':'week_year'})
        self.stringency['week_year']=self.stringency['week_year'].astype(str)
        self.stringency['2weeks']=self.stringency['week_year'].replace(self.dict_weeks)
        self.stringency=self.stringency.fillna(0)
    
        return self.stringency
    
    def format_main_data(self,from_date,to_date):
        
        self.data['date_trans'] = self.data['date'].apply(lambda x:
                                                        self.format_date(x))

        self.data = self.data[(self.data.date_trans>=from_date)&(self.data.date_trans<=to_date)]
        
        self.data['week'] = self.data['date_trans'].apply(lambda x:x.isocalendar().week)
        self.data['weekday'] = self.data['date_trans'].apply(lambda x:x.isocalendar().weekday)
        self.data['year'] = self.data['date_trans'].apply(lambda x:x.isocalendar().year)
        self.data['week_year']=list(zip(self.data['week'],self.data['year']))
        
        self.date_dict=dict(zip(self.data['date_trans'],self.data['week_year']))

        self.data.drop(columns=['date_trans'],inplace=True)
        
        list_weeks=self.data['week_year'].unique().tolist()
        list1=list_weeks[::2]
        list2=list_weeks[1::2]
        list_weeks1=list(zip(list1,list2))
        
        dict_weeks1={str(x[0]):str(x) for x in list_weeks1}
        dict_weeks2={str(x[1]):str(x) for x in list_weeks1}

        self.dict_weeks=dict_weeks1|dict_weeks2
        
        self.data['week_year']=self.data['week_year'].apply(lambda x: str(x))

        self.data['2weeks']=self.data['week_year'].replace(self.dict_weeks)
        
        self.data=self.data[self.data.weekday!=6]
        self.data.drop(columns='weekday',inplace=True)
        
        return self.data, self.date_dict, self.dict_weeks
        
    def group_data(self):
        
        self.data_gr=self.data[['country_region',
               'retail_and_recreation_percent_change_from_baseline',
               'grocery_and_pharmacy_percent_change_from_baseline',
               'parks_percent_change_from_baseline',
               'transit_stations_percent_change_from_baseline',
               'workplaces_percent_change_from_baseline',
               'residential_percent_change_from_baseline', '2weeks']]\
            .groupby(['country_region','2weeks']).mean().reset_index()

        self.data_gr.columns=['country', '2weeks',
               'retail_and_recreation_percent_change_from_baseline',
               'grocery_and_pharmacy_percent_change_from_baseline',
               'parks_percent_change_from_baseline',
               'transit_stations_percent_change_from_baseline',
               'workplaces_percent_change_from_baseline',
               'residential_percent_change_from_baseline']
        
        self.stringency_gr=self.stringency.groupby(['2weeks']).mean()
        self.stringency_gr=self.stringency_gr.round()
        
        self.df_max1=self.stringency_gr.max().reset_index()
        self.df_max1=self.df_max1.set_index('index') 
        self.df_max2=self.stringency_gr.idxmax().reset_index()
        self.df_max2=self.df_max2.set_index('index')
        self.df_max=self.df_max2.merge(self.df_max1, on='index')
        self.df_max.columns=['2weeks','stringency_value']
        self.df_max['country']=self.stringency_gr.columns

        
        self.data_final=pd.merge(self.data_gr,self.df_max,on=['country','2weeks'])
        self.data_final=self.data_final[['country', '2weeks', 'stringency_value','retail_and_recreation_percent_change_from_baseline',
               'grocery_and_pharmacy_percent_change_from_baseline',
               'parks_percent_change_from_baseline',
               'transit_stations_percent_change_from_baseline',
               'workplaces_percent_change_from_baseline',
               'residential_percent_change_from_baseline']]

        self.data_final=self.data_final.fillna(0)
        
        return self.data_final
    
    
class DataWriter:
    
    def __init__(self,*files):
        
        self.files=(files)
        
    def write_to_excel(self):
        
        for file in self.files:           
    
            self.xlsx_wrt = pd.ExcelWriter("mobility_"+second_datetime.now()\
                                           .strftime("%Y_%m_%d_%H_%M")+".xlsx", engine="xlsxwriter")
        
            self.workbook  = self.xlsx_wrt.book

            file.to_excel(self.xlsx_wrt, sheet_name="Country_groups", index=False)

            self.xlsx_wrt.save()
            self.workbook.close()


def menu(choices=list(''), title='', nr_rows=30):
        """A function to create a user menu from a list as input
        Input:  choices - a list of user selectable items
                title - the menu title
                nr_rows - is the maximum number of row to be visible
                            on the screen without a mouse scroll
        Output: a_chosen - a value selected by the user from the list of choices
        """
    
        def user_selection():
            move_text = listbox.selection_get()
            curindex = int(listbox.curselection()[0])
            listbox.delete(curindex)
            a_chosen.append(move_text)
            master.quit()
    
        def quit_app():
            if messagebox.askokcancel("Quit", "Do you want to quit?"):
                print("Exiting the program")
                sys.exit(-1)
    
        master = tk.Tk(screenName=title, baseName=title)
        avl_choices = len(choices)
        wdt = len((max(choices, key=len)))
        master.geometry('300' + 'x' + str(int(min(min(nr_rows, avl_choices) * 16 + 40, 700))))
        master.title(title)
        master.protocol('WM_DELETE_WINDOW', quit_app)
    
        frame = tk.Frame(master)
        frame.pack()
    
        listbox = tk.Listbox(frame, width=int(wdt * 1.5),
                             height=int(min(nr_rows, avl_choices)), font=('times', 10))
        listbox.place(x=52, y=90)
        listbox.pack(side="left", fill="y")
    
        if avl_choices > 2:
            scrollbar = tk.Scrollbar(frame, orient="vertical")
            scrollbar.config(command=listbox.yview)
            scrollbar.pack(side="right", fill="y")
            listbox.config(yscrollcommand=scrollbar.set)
    
        a_chosen = list('')
    
        moveBtn = tk.Button(master, text="OK", command=user_selection)
        moveBtn.pack()
    
        for item in choices:
            listbox.insert(tk.END, item)
    
        master.mainloop()
        master.destroy()
        return a_chosen
    
class DateSelect:
    def __init__(self,root):        
   
        self.top = tk.Toplevel(root)
        now = datetime.now()
        
        self.cal = Calendar(self.top, font="Arial 12", selectmode='day',
                            year=now.year, month=now.month, day=now.day,
                            locale='en_US')
                            
        self.cal.pack(fill="both", expand=True)
        ttk.Button(self.top, text="OK", command=self.print_sel).pack()

        self.date = datetime.strptime(str(datetime.now().year - 10) + "/12/01",
                                      "%Y/%m/%d").date()
        self.top.grab_set()

    def print_sel(self):
        self.date = self.cal.selection_get()
        self.top.destroy()


class PeriodExtract:
    def __init__(self, from_date, to_date):
        self.root = tk.Tk()
        s = ttk.Style(self.root)
        s.theme_use('clam')

        label = ttk.Label(self.root, text="Please select From and To Dates:",
                          font=("Verdana", 10))
        label.pack(side="top", fill="x", pady=0)
        ttk.Button(self.root, text='Select: FROM Date',
                   command=self.fdate).pack(padx=10, pady=10)
        ttk.Button(self.root, text='Select:  TO  Date',
                   command=self.tdate).pack(padx=10, pady=10)

        self.frdate = from_date
        self.todate = to_date

        self.root.mainloop()

    def tdate(self):
        cal = DateSelect(self.root)
        self.root.wait_window(cal.top)
        self.frdate = cal.date
        
        if self.frdate == datetime.strptime(str(datetime.now().year - 10) + "/12/01",
                        "%Y/%m/%d").date() or self.todate == datetime.strptime(
                       str(datetime.now().year - 3) + "/12/01", "%Y/%m/%d").date():
                                
            if self.frdate == datetime.strptime(str(datetime.now().year - 10) 
                                                + "/12/01", "%Y/%m/%d").date():
                
                if self.todate == datetime.strptime(str(datetime.now().year - 10) 
                                                    + "/12/01", "%Y/%m/%d").date():
                    
                    label = ttk.Label(self.root, 
                                      text="'From Date': ____-__-__  --  'To  Date': ____-__-__",
                                      font=("Verdana", 10), foreground='#ff0000')
                else:
                    label = ttk.Label(self.root,
                                      text="'From Date': " + str(self.todate)
                                      +" --  'To  Date': ____-__-__",
                                      font=("Verdana", 10), foreground='#ff0000')
            else:
                label = ttk.Label(self.root, 
                                  text="'From Date': ____-__-__ --  'To  Date': "
                                  + str(self.frdate),
                                  font=("Verdana", 10), foreground='#ff0000')
        else:
            if self.frdate <= self.todate:
                x = self.frdate
                self.frdate = self.todate
                self.todate = x
            label = ttk.Label(self.root,
                              text="'From Date': " + str(self.todate) 
                              + " --  'To  Date': " + str(self.frdate),
                              font=("Verdana", 10))
        label.pack(side='top', fill="x", padx=0, pady=0)

    def fdate(self):
        cal = DateSelect(self.root)
        self.root.wait_window(cal.top)
        self.todate = cal.date
        if self.frdate == datetime.strptime(str(datetime.now().year - 10) + "/12/01",
                            "%Y/%m/%d").date() or self.todate == datetime.strptime(
                        str(datetime.now().year - 3) + "/12/01", "%Y/%m/%d").date():
                                    
            if self.frdate == datetime.strptime(str(datetime.now().year - 10)
                                                + "/12/01", "%Y/%m/%d").date():
                
                if self.todate == datetime.strptime(str(datetime.now().year - 10) 
                                                    + "/12/01", "%Y/%m/%d").date():
                    
                    label = ttk.Label(self.root, 
                                      text="'From Date': ____-__-__  --  'To  Date': ____-__-__",
                                      font=("Verdana", 10), foreground='#ff0000')
                else:
                    label = ttk.Label(self.root,
                                      text="'From Date': " + str(self.todate) 
                                      + " --  'To  Date': ____-__-__",
                                      font=("Verdana", 10), foreground='#ff0000')
            else:
                label = ttk.Label(self.root, 
                                  text="'From Date': ____-__-__ --  'To  Date': "
                                  + str(self.frdate),
                                  font=("Verdana", 10), foreground='#ff0000')
        else:
            if self.frdate <= self.todate:
                x = self.frdate
                self.frdate = self.todate
                self.todate = x
            label = ttk.Label(self.root,
                              text="'From Date': " + str(self.todate) 
                              + " --  'To  Date': " + str(self.frdate),
                              font=("Verdana", 10))
        label.pack(side='top', fill="x", padx=0, pady=0)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        

    

