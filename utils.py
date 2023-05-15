# -*- coding: utf-8 -*-
"""
Created on Fri Dec  4 10:46:25 2020

@author: Anna Davy
"""
import pandas as pd
import sys
import tkinter as tk
from tkinter import messagebox
import warnings
warnings.filterwarnings("ignore")
from datetime import datetime
from tkinter import ttk
from tkcalendar import Calendar


class DataReader:
    
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
    
    def __init__(self, data, stringency):
        
        self.data=data
        self.stringency=stringency
        
        
        
        

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
    
        listbox = tk.Listbox(frame, width=int(wdt * 1.5), height=int(min(nr_rows, avl_choices)), font=('times', 10))
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
    
class date_sel():
    def __init__(self, root):
        self.top = tk.Toplevel(root)
        now = datetime.now()
        
        #first_date1=datetime.strptime(first_date, "%Y-%m-%d").date()
        self.cal = Calendar(self.top, font="Arial 12", selectmode='day',
                            year=now.year, month=now.month, day=now.day,locale='en_US')
        #self.cal = Calendar(self.top, font="Arial 12", selectmode='day',
                            #year=first_date1.year, month=first_date1.month, day=first_date1.day,locale='en_US')
                   
                            
        self.cal.pack(fill="both", expand=True)
        ttk.Button(self.top, text="OK", command=self.print_sel).pack()

        self.date = datetime.strptime(str(datetime.now().year - 3) + "/12/01", "%Y/%m/%d").date()
        #self.date=datetime.strptime(last_date, "%Y-%m-%d").date()
        self.top.grab_set()

    def print_sel(self):
        self.date = self.cal.selection_get()
        self.top.destroy()


class get_extraction_period():
    def __init__(self, from_date, to_date):
        self.root = tk.Tk()
        s = ttk.Style(self.root)
        s.theme_use('clam')

        label = ttk.Label(self.root, text="Please select From and To Dates:", font=("Verdana", 10))
        label.pack(side="top", fill="x", pady=0)
        ttk.Button(self.root, text='Select: FROM Date', command=self.fdate).pack(padx=10, pady=10)
        ttk.Button(self.root, text='Select:  TO  Date', command=self.tdate).pack(padx=10, pady=10)

        self.frdate = from_date
        self.todate = to_date

        self.root.mainloop()

    def tdate(self):
        cal = date_sel(self.root)
        self.root.wait_window(cal.top)
        self.frdate = cal.date
        #from_date = self.frdate
        if self.frdate == datetime.strptime(str(datetime.now().year - 3) + "/12/01",
                                            "%Y/%m/%d").date() or self.todate == datetime.strptime(
                str(datetime.now().year - 3) + "/12/01", "%Y/%m/%d").date():
            if self.frdate == datetime.strptime(str(datetime.now().year - 3) + "/12/01", "%Y/%m/%d").date():
                if self.todate == datetime.strptime(str(datetime.now().year - 3) + "/12/01", "%Y/%m/%d").date():
                    label = ttk.Label(self.root, text="'From Date': ____-__-__  --  'To  Date': ____-__-__",
                                      font=("Verdana", 10), foreground='#ff0000')
                else:
                    label = ttk.Label(self.root,
                                      text="'From Date': " + str(self.todate) + " --  'To  Date': ____-__-__",
                                      font=("Verdana", 10), foreground='#ff0000')
            else:
                label = ttk.Label(self.root, text="'From Date': ____-__-__ --  'To  Date': " + str(self.frdate),
                                  font=("Verdana", 10), foreground='#ff0000')
        else:
            if self.frdate <= self.todate:
                x = self.frdate
                self.frdate = self.todate
                self.todate = x
            label = ttk.Label(self.root,
                              text="'From Date': " + str(self.todate) + " --  'To  Date': " + str(self.frdate),
                              font=("Verdana", 10))
        label.pack(side='top', fill="x", padx=0, pady=0)

    def fdate(self):
        cal = date_sel(self.root)
        self.root.wait_window(cal.top)
        self.todate = cal.date
        if self.frdate == datetime.strptime(str(datetime.now().year - 3) + "/12/01",
                                            "%Y/%m/%d").date() or self.todate == datetime.strptime(
                str(datetime.now().year - 3) + "/12/01", "%Y/%m/%d").date():
            if self.frdate == datetime.strptime(str(datetime.now().year - 3) + "/12/01", "%Y/%m/%d").date():
                if self.todate == datetime.strptime(str(datetime.now().year - 3) + "/12/01", "%Y/%m/%d").date():
                    label = ttk.Label(self.root, text="'From Date': ____-__-__  --  'To  Date': ____-__-__",
                                      font=("Verdana", 10), foreground='#ff0000')
                else:
                    label = ttk.Label(self.root,
                                      text="'From Date': " + str(self.todate) + " --  'To  Date': ____-__-__",
                                      font=("Verdana", 10), foreground='#ff0000')
            else:
                label = ttk.Label(self.root, text="'From Date': ____-__-__ --  'To  Date': " + str(self.frdate),
                                  font=("Verdana", 10), foreground='#ff0000')
        else:
            if self.frdate <= self.todate:
                x = self.frdate
                self.frdate = self.todate
                self.todate = x
            label = ttk.Label(self.root,
                              text="'From Date': " + str(self.todate) + " --  'To  Date': " + str(self.frdate),
                              font=("Verdana", 10))
        label.pack(side='top', fill="x", padx=0, pady=0)

    
