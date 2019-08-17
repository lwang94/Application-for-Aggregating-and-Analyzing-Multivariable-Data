# -*- coding: utf-8 -*-
"""
Created on Thu Oct 18 13:42:37 2018

@author: lawre
"""

import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.figure as fig

import scipy.optimize as opt
import Tkinter as tk
import ttk
import tkFileDialog as fd
import sys
import tkMessageBox as mb
import os
import itertools

from mpl_toolkits.mplot3d import Axes3D
import Shared_Functions as sf


#Controller class, contains dictionaries for shared data as well as container for frames
class Data_Analysis(tk.Tk):
    
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.wm_title(self, 'Multi-dimensional Data Compiler and Analyzer')
        
        #Container
        container=tk.Frame(self)
        container.pack(side='top', fill='both', expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        #Inputs dictionary
        self.inputs={
            #Initial inputs
            'ind_var_input':' ', #string
            'ind_var_unit_input':' ', #string
            'num_variables_input':0, #integer       
            #Inputs after specifying number of variables
            'variable_name_input':[], #list of strings
            'variable_unit_input':[], #list of strings
            'range_type_input': [], #list of strings
            'num_datapoints_input':[], #list of integers
            'variable_range_input':[], #nested list of floats, dim=2
            'is_included_in_file_input':[], #list of booleans/integers (0 or 1)
            'track_file_input':None, #boolean/integer (0 or 1)           
            #Listing variable names ordered by their dimension
            'unincluded_dim_name':[], #list of strings
            'included_dim_name':[], #list of strings
            'matrix_dim_name':[], #list of strings
            #Listing variable units ordered by their dimension
            'unincluded_dim_unit':[], #list of strings
            'included_dim_unit':[], #list of strings
            'matrix_dim_unit':[], #list of strings
            #Listing type of range ordered by their dimensions
            'unincluded_range_type': [], #list of strings
            'included_range_type': [], #list of strings
            'matrix_range_type': [], #list of string
            #Listing range of variables ordered by their dimensions
            'unincluded_dim_range':[], #nested list of floats, dim=2
            'included_dim_range':[], #nested list of floats, dim=2
            'matrix_dim_range':[], #nested list of floats, dim=2
            #Listing length of dimension in order   
            'unincluded_dimensions':[], #list of integers
            'included_dimensions':[], #list of integers
            'matrix_dimensions':[], #list of integers
            #Constructing the matrix 
            'matrix':[], #original raw matrix that remains unchanged through various operations
            #Open file inputs
            'num_txt_files':1, #number of text files to be added to file list
            }
        
        #Copy dictionary for relevant variables
        self.copy={
            'ind_var_input': ' ',
            'ind_var_unit_input':' ',
            'num_variables_input':0,
            'matrix_dim_name': [],
            'matrix_dim_unit': [],
            'matrix_range_type': [],
            'matrix_dim_range': [],
            'matrix_dimensions': [],
            'matrix': []
            }
        
        #Dictionary for performing derivatives
        self.numderiv={
            'num_deriv_counter': ' '
            }
        
        #Frames (pages) dictionary          
        self.frames={}        
        for F in (StartPage, Inputs, Matrix_Fun, Function_Fitting, Editor):        
            frame=F(container, self)            
            self.frames[F]=frame           
            frame.grid(row=0, column=0, sticky='nsew')
            
        self.show_frame(StartPage) #Initially will show StartPage

    def show_frame(self, cont): 
        """Raises frame to the front"""
        frame=self.frames[cont]
        frame.tkraise()
        
#Start Page
class StartPage(tk.Frame):
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)        
        self.controller=controller

        label=tk.Label(self, text='Let\'s Begin!').pack(pady=10, padx=10)
        
        start_button=ttk.Button(self, text='Start', command=
                                                    lambda: self.controller.show_frame(Inputs))
        start_button.pack()

#Create matrix from inputs or load previously saved matrix   
class Inputs(tk.Frame):
       
    def __init__(self, parent, controller): 
        tk.Frame.__init__(self, parent)
        self.controller=controller
        self.shared_func=sf.Shared_Functions()
        
        home_button=ttk.Button(self, text='Back to Home',
                  command=lambda: self.controller.show_frame(StartPage))     
        home_button.grid(row=0, column=0, pady=20)

        fun_button=ttk.Button(self, text="Matrix Fun", 
                               command=lambda: self.controller.show_frame(Matrix_Fun))
        fun_button.grid(row=0, column=1, pady=20)
        
        edit_button=ttk.Button(self, text='Editor (Beta)',
                               command=lambda: self.controller.show_frame(Editor))
        edit_button.grid(row=0, column=2, pady=20)
        
        fit_button=ttk.Button(self, text='Function Fit', 
                               command=lambda: self.controller.show_frame(Function_Fitting))
        fit_button.grid(row=0, column=3, pady=20)
        
        #Frames
        self.initial_inputs_frame=tk.Frame(self)
        self.initial_inputs_frame.grid(row=1, column=0, sticky=tk.W)
        self.initial_inputs_child_frame=tk.Frame(self.initial_inputs_frame)
        self.initial_inputs_child_frame.pack()

        self.define_variables_frame=tk.Frame(self)
        self.define_variables_frame.grid(row=2, column=0, columnspan=2, sticky=tk.W)
        self.define_variables_child_frame=tk.Frame(self.define_variables_frame)
        self.define_variables_child_frame.pack()
        
        self.file_format_frame=tk.Frame(self)
        self.file_format_frame.grid(row=4, column=0, sticky=tk.W, columnspan=2)
        self.file_format_child_frame=tk.Frame(self.file_format_frame)
        self.file_format_child_frame.pack()           

        self.tracker_frame=tk.Frame(self)
        self.tracker_frame.grid(row=3, column=0)
        self.tracker_child_frame=tk.Frame(self.tracker_frame)
        self.tracker_child_frame.pack()

        self.matrix_text_frame=tk.Frame(self)
        self.matrix_text_frame.grid(row=3, column=1, columnspan=3, pady=20)        

        #beginning widgets
        self.initial_widgets()

        self.matrix_text=tk.Text(self.matrix_text_frame, height=20, width=70)
        self.matrix_text.pack(side=tk.TOP)
        
    def initial_widgets(self, ind_var_input='', ind_var_unit_input='', num_variables_input=''):
        """creates widgets that user sees to begin creating matrix"""
        self.initial_inputs_child_frame.destroy()

        self.initial_inputs_child_frame=tk.Frame(self.initial_inputs_frame)
        self.initial_inputs_child_frame.pack()
        
        #independent variable parameter
        ind_var=tk.Label(self.initial_inputs_child_frame, text='Output Value').grid(row=0, column=0)
        self.ind_var_entry=ttk.Entry(self.initial_inputs_child_frame)
        self.ind_var_entry.insert(tk.END, ind_var_input)
        self.ind_var_entry.grid(row=0, column=1)
        
        ind_var_unit=tk.Label(self.initial_inputs_child_frame, text='Units').grid(row=0, column=2)  
        self.ind_var_unit_entry=ttk.Entry(self.initial_inputs_child_frame)
        self.ind_var_unit_entry.insert(tk.END, ind_var_unit_input)
        self.ind_var_unit_entry.grid(row=0, column=3)
        
        #number of dependent variables
        num_variables=tk.Label(self.initial_inputs_child_frame, text="Num Variables").grid(row=1, column=0, pady=5)

        self.num_variables_entry=ttk.Entry(self.initial_inputs_child_frame)
        self.num_variables_entry.insert(tk.END, num_variables_input)
        self.num_variables_entry.grid(row=1, column=1)   

        #beginning buttons
        load_button=ttk.Button(self.initial_inputs_child_frame, text='Load Matrix', command=self.load_matrix) #load already saved matrix
        load_button.grid(row=0, column=4, padx=40)
        
        self.show_Button=ttk.Button(self.initial_inputs_child_frame, text="Show", command=self.execute_first_step) #continue with making new matrix
        self.show_Button.grid(row=2, column=1, padx=5)    
    
    def execute_first_step(self):
        """sets beginning parameters into dictionary and begins next step after beginning parameters have been set"""
        self.controller.inputs['ind_var_input']=self.ind_var_entry.get() #Sets independent variable into inputs key
        self.controller.copy['ind_var_input']=self.ind_var_entry.get() #Creates copy for when manipulating matrix later
        
        self.controller.inputs['ind_var_unit_input']=self.ind_var_unit_entry.get() #Sets independent variable units into inputs key
        self.controller.copy['ind_var_unit_input']=self.ind_var_unit_entry.get()

        self.controller.inputs['num_variables_input']=int(self.num_variables_entry.get()) #Sets number of variables into inputs key
        self.controller.copy['num_variables_input']=int(self.num_variables_entry.get())        
        
        #creates widgets after beginning parameters have been set
        self.define_variables_widgets()
    
    def define_variables_widgets(self, variable_name_input=None, variable_unit_input=None):
        """creates widgets for user to define variable parameters in matrix"""
        self.show_Button.config(state=tk.DISABLED)                
        reset_initial_inputs_button=ttk.Button(self.initial_inputs_child_frame, text='Reset', command=self.reset_initial_inputs)
        reset_initial_inputs_button.grid(row=2, column=2)
        
        self.define_variables_child_frame.destroy()
        
        self.define_variables_child_frame=tk.Frame(self.define_variables_frame)
        self.define_variables_child_frame.pack()
        
        #first create variable parameter entries as empty lists
        variable_name_entry=[None]*self.controller.inputs['num_variables_input']
        variable_unit_entry=[None]*self.controller.inputs['num_variables_input']
        is_included_in_file=[None]*self.controller.inputs['num_variables_input']        
        self.uniform_range_button=[None]*self.controller.inputs['num_variables_input']
        self.custom_range_button=[None]*self.controller.inputs['num_variables_input']
        self.variable_range=[None]*self.controller.inputs['num_variables_input']
        self.range_type=[' ']*self.controller.inputs['num_variables_input']
        
        #Widgets to allow user to define variable parameters
        for i in range(self.controller.inputs['num_variables_input']):
            variable_name=tk.Label(self.define_variables_child_frame, text="     Var No. %d     "%(i+1)).grid(row=2*i, column=0)            
            variable_name_entry[i]=ttk.Entry(self.define_variables_child_frame)
            if variable_name_input!=None: #if user uses load_matrix button, will automatically insert value into the entry field
                variable_name_entry[i].insert(tk.END, variable_name_input[i])
            variable_name_entry[i].grid(row=2*i, column=1)
            
            variable_unit=tk.Label(self.define_variables_child_frame, text='Units').grid(row=2*i, column=2)            
            variable_unit_entry[i]=ttk.Entry(self.define_variables_child_frame)
            if variable_unit_input!=None:
                variable_unit_entry[i].insert(tk.END, variable_unit_input[i])
            variable_unit_entry[i].grid(row=2*i, column=3)
            
            is_included_in_file[i]=tk.IntVar()
            is_included_in_file_check=tk.Checkbutton(self.define_variables_child_frame, 
                                                     text="Included in txt file?", 
                                                     variable=is_included_in_file[i])
            is_included_in_file_check.grid(row=2*i, column=4, padx=10)
            
            self.uniform_range_button[i]=ttk.Button(self.define_variables_child_frame, text='Uniform Range?')
            self.uniform_range_button[i].grid(row=2*i, column=5)
            self.custom_range_button[i]=ttk.Button(self.define_variables_child_frame, text='Custom Range?')
            self.custom_range_button[i].grid(row=2*i+1, column=5)
            
            self.uniform_range_button[i].config(command= lambda frame=self.define_variables_child_frame, 
                                                                row=2*i, 
                                                                column=6, 
                                                                var_number=i: self.inputs_uniform_range(frame, 
                                                                                                        row, 
                                                                                                        column, 
                                                                                                        var_number))
            self.custom_range_button[i].config(command= lambda frame=self.define_variables_child_frame, 
                                                                row=2*i+1, 
                                                                column=6, 
                                                                var_number=i: self.inputs_custom_range(frame, 
                                                                                                       row, 
                                                                                                       column, 
                                                                                                       var_number))

        track_file=tk.IntVar()
        track_file_check=tk.Checkbutton(self.define_variables_child_frame, 
                                        text="Would you like to track your files?", 
                                        variable=track_file)
        track_file_check.grid(row=2+2*self.controller.inputs['num_variables_input'], column=0, columnspan=3, padx=10)
        
        #Confirm button
        self.confirm_button=ttk.Button(self.define_variables_child_frame, 
                                       text="Confirm", 
                                       command= lambda var_name=variable_name_entry, 
                                                       var_unit=variable_unit_entry, 
                                                       is_included=is_included_in_file, 
                                                       var_range=self.variable_range, 
                                                       list_type_check=self.range_type, 
                                                       track=track_file: self.variable_inputs(var_name, 
                                                                                               var_unit, 
                                                                                               is_included, 
                                                                                               var_range, 
                                                                                               list_type_check, 
                                                                                               track))                    
        self.confirm_button.grid(row=3+2*self.controller.inputs['num_variables_input'], column=1)        

    def inputs_uniform_range(self, frame, row, column, var_number, variable_range_input=None):
        """creates uniform range in the inputs page"""
        self.shared_func.build_uniform_range(frame, row, column, uniform_button=self.uniform_range_button[var_number], custom_button=self.custom_range_button[var_number], variable_range_input=variable_range_input)
        self.variable_range[var_number]=self.shared_func.variable_range
        self.range_type[var_number]=self.shared_func.range_type
    
    def inputs_custom_range(self, frame, row, column, var_number, variable_range_input=None): 
        """creates custom range in the inputs page"""
        self.shared_func.build_custom_range(frame, row, column, uniform_button=self.uniform_range_button[var_number], custom_button=self.custom_range_button[var_number], variable_range_input=variable_range_input)
        self.variable_range[var_number]=self.shared_func.variable_range
        self.range_type[var_number]=self.shared_func.range_type
        
    def variable_inputs(self, var_name, var_unit, is_included, var_range, list_type_check, track):
        """puts variable parameters into dictionary and begins process to create matrix from files"""
        self.confirm_button.config(state=tk.DISABLED)        
        reset_define_variables_button=ttk.Button(self.define_variables_child_frame, text='Reset', command=self.reset_define_variables)
        reset_define_variables_button.grid(row=3+2*self.controller.inputs['num_variables_input'], column=2)
        
        self.file_format_child_frame.destroy()
        
        self.file_format_child_frame=tk.Frame(self.file_format_frame)
        self.file_format_child_frame.pack()   
        
        #Retrieving variable parameters as usable data**
        for i in range(self.controller.inputs['num_variables_input']):
            self.controller.inputs['variable_name_input']+=[var_name[i].get()]
            self.controller.inputs['variable_unit_input']+=[var_unit[i].get()]
            self.controller.inputs['is_included_in_file_input']+=[is_included[i].get()] 
            if list_type_check[i]=='uniform':
                variable_range_input=[float(j) for j in var_range[i].get().split(',')]
                self.controller.inputs['variable_range_input']+=[list(np.linspace(variable_range_input[0], variable_range_input[1], variable_range_input[2]))]
            elif list_type_check[i]=='custom':
                variable_range_input=[float(j) for j in var_range[i].get().split(',')]
                self.controller.inputs['variable_range_input']+=[list(variable_range_input)]
            else:
                mb.showerror('Error', 'Please specify range for all variables')
            self.controller.inputs['range_type_input']+=[list_type_check[i]]
            self.controller.inputs['num_datapoints_input']+=[len(self.controller.inputs['variable_range_input'][i])]
        self.controller.inputs['track_file_input']=track.get() #boolean/integer (0 or 1)
        
        #Separates parameters by whether they are included in the .txt file**
        for i in range(self.controller.inputs['num_variables_input']):
            if self.controller.inputs['is_included_in_file_input'][i]==0: #unincluded
                self.controller.inputs['unincluded_dimensions']+=[self.controller.inputs['num_datapoints_input'][i]]
                self.controller.inputs['unincluded_dim_name']+=[self.controller.inputs['variable_name_input'][i]]
                self.controller.inputs['unincluded_dim_unit']+=[self.controller.inputs['variable_unit_input'][i]]
                self.controller.inputs['unincluded_dim_range']+=[self.controller.inputs['variable_range_input'][i]]
                self.controller.inputs['unincluded_range_type']+=[self.controller.inputs['range_type_input'][i]]
            elif self.controller.inputs['is_included_in_file_input'][i]==1: #included
                self.controller.inputs['included_dimensions']+=[self.controller.inputs['num_datapoints_input'][i]]
                self.controller.inputs['included_dim_name']+=[self.controller.inputs['variable_name_input'][i]]
                self.controller.inputs['included_dim_unit']+=[self.controller.inputs['variable_unit_input'][i]]
                self.controller.inputs['included_dim_range']+=[self.controller.inputs['variable_range_input'][i]]
                self.controller.inputs['included_range_type']+=[self.controller.inputs['range_type_input'][i]]
        #Reorders parameters by their dimensions**
        self.controller.inputs['matrix_dimensions']=self.controller.inputs['unincluded_dimensions']+self.controller.inputs['included_dimensions']
        self.controller.inputs['matrix_dim_name']=self.controller.inputs['unincluded_dim_name']+self.controller.inputs['included_dim_name']
        self.controller.inputs['matrix_dim_unit']=self.controller.inputs['unincluded_dim_unit']+self.controller.inputs['included_dim_unit']
        self.controller.inputs['matrix_dim_range']=self.controller.inputs['unincluded_dim_range']+self.controller.inputs['included_dim_range']
        self.controller.inputs['matrix_range_type']=self.controller.inputs['unincluded_range_type']+self.controller.inputs['included_range_type']
        #create copies so that matrix can be manipulated later        
        self.controller.copy['matrix_dimensions']=self.controller.inputs['unincluded_dimensions']+self.controller.inputs['included_dimensions']
        self.controller.copy['matrix_dim_name']=self.controller.inputs['unincluded_dim_name']+self.controller.inputs['included_dim_name']
        self.controller.copy['matrix_dim_unit']=self.controller.inputs['unincluded_dim_unit']+self.controller.inputs['included_dim_unit']
        self.controller.copy['matrix_dim_range']=self.controller.inputs['unincluded_dim_range']+self.controller.inputs['included_dim_range']
        self.controller.copy['matrix_range_type']=self.controller.inputs['unincluded_range_type']+self.controller.inputs['included_range_type']        
        
        #creates file parameters widgets and upload files
        self.file_inputs()
        
    def file_inputs(self): 
        """creates widgets for file parameters and uploads files for creating matrix"""
        for i in range(self.controller.inputs['num_variables_input']):
            if self.controller.inputs['is_included_in_file_input'][i]==0:
                self.controller.inputs['num_txt_files']*=self.controller.inputs['num_datapoints_input'][i] #finds the product of the length of all the unincluded dimensions
       
        #uploads files       
        if self.controller.inputs['track_file_input']==1 and self.controller.inputs['unincluded_dimensions']!=[]: #checks for whether the user would like to and is able to track their files 
            self.tracker_child_frame.destroy()
            self.tracker_child_frame=tk.Frame(self.tracker_frame)
            self.tracker_child_frame.config(highlightbackground='blue', highlightcolor='blue', highlightthickness=1, height=20, width=70)
            self.tracker_child_frame.pack()               
            self.shared_func.tracker(frame=self.tracker_child_frame, 
                                     dimensions=self.controller.inputs['unincluded_dimensions'], 
                                    dim_name=self.controller.inputs['unincluded_dim_name'], 
                                    row=0, 
                                    column=0) 
        elif self.controller.inputs['track_file_input']==1 and self.controller.inputs['unincluded_dimensions']==[]: #if the user would like to track their files but there is only one file, show error
            mb.showerror('Error', 'Cannot track only one file. Please uncheck tracking file option')                        
        else: #creates file list without tracker function           
            while len(self.shared_func.file_list)<self.controller.inputs['num_txt_files']:
                add_file=self.shared_func.select_files(self.shared_func.folder)
                if add_file==[]: #if user cancels adding files, assumes the user would like to start everything over
                    break
                add_file.append(add_file.pop(0)) #puts the first file selected back to the beginning because tkinter is weird like that (tkinter will put the first file selected at the end)
                self.shared_func.file_list+=add_file       
         
        #Check to make sure the file list is the right size
        if len(self.shared_func.file_list)!=self.controller.inputs['num_txt_files']:  
            mb.showerror("Error", "File list incompatible with amount of data specified, please reconfirm inputs and press reset")             
        
        #Widgets for loading text from the .txt files**                
        self.shared_func.file_format_widgets(frame=self.file_format_child_frame, row=0, column=0)

        #Button that will compile all the information and .txt files into an n-dimensional matrix
        compile_button=ttk.Button(self.file_format_child_frame, 
                                  text='Compile', 
                                  command= lambda comments=self.shared_func.comments_entry, 
                                                  delimiter=self.shared_func.delimiter_entry,
                                                  skiprows=self.shared_func.skiprows_entry, 
                                                  usecolumns=self.shared_func.usecols_entry: self.inputs_create_matrix(comments, 
                                                                                                                       delimiter, 
                                                                                                                       skiprows, 
                                                                                                                       usecolumns))
        compile_button.grid(row=0, column=8)

    def inputs_create_matrix(self, comments, delimiter, skiprows, usecolumns):
        """create matrix from inputs"""
        self.shared_func.create_matrix(comments=comments, 
                                       delimiter=delimiter, 
                                       skiprows=skiprows, 
                                       usecolumns=usecolumns, 
                                       dimensions=self.controller.inputs['matrix_dimensions'], 
                                        file_list=self.shared_func.file_list)
        
        #put matrix into dictionary and create a copy
        self.controller.inputs['matrix']=self.shared_func.matrix
        self.controller.copy['matrix']=self.shared_func.matrix
        
        #display matrix in text widget
        self.shared_func.display_matrix(frame=self.matrix_text_frame, 
                                        text_widget=self.matrix_text, 
                                        matrix=self.controller.inputs['matrix'], 
                                        ind_var=self.controller.inputs['ind_var_input'], 
                                        ind_var_unit=self.controller.inputs['ind_var_unit_input'], 
                                        num_var=self.controller.inputs['num_variables_input'],
                                        names=self.controller.inputs['matrix_dim_name'], 
                                        units=self.controller.inputs['matrix_dim_unit'], 
                                        dimensions=self.controller.inputs['matrix_dimensions'],
                                        range_type=self.controller.inputs['matrix_range_type'], 
                                        ranges=self.controller.inputs['matrix_dim_range'])
      
    def load_matrix(self):
        """loads in previously created matrix"""
        matrix_file=fd.askopenfilename(initialdir=self.shared_func.folder, title="Open Matrix File")
        self.shared_func.folder=os.path.dirname(matrix_file)
        
        self.controller.inputs['matrix']=np.load(matrix_file)    
        self.controller.copy['matrix']=np.load(matrix_file)   
        
        #loads in the parameters
        parameter_file=fd.askopenfilename(initialdir=self.shared_func.folder, title="Open Parameters File")
        self.shared_func.folder=os.path.dirname(matrix_file)
        
        parameters=[]
        with open(parameter_file) as parameter_file:
            for parameter in parameter_file:
                parameters+=[parameter.rstrip('\n')]
        
        #sets beginning parameters
        initial_inputs=parameters[0].split(',')
        self.controller.inputs['ind_var_input']=initial_inputs[0]
        self.controller.copy['ind_var_input']=initial_inputs[0]
        
        self.controller.inputs['ind_var_unit_input']=initial_inputs[1]
        self.controller.copy['ind_var_unit_input']=initial_inputs[1]
        
        self.controller.inputs['num_variables_input']=int(initial_inputs[2])
        self.controller.copy['num_variables_input']=int(initial_inputs[2])
        
        self.initial_widgets(ind_var_input=initial_inputs[0], 
                             ind_var_unit_input=initial_inputs[1],
                            num_variables_input=initial_inputs[2])
        
        #sets variable parameters except for range which requires special treatment
        variable_name_inputs=parameters[1].split(',')
        self.controller.inputs['matrix_dim_name']=variable_name_inputs[:-1]
        self.controller.copy['matrix_dim_name']=variable_name_inputs[:-1][:]
        
        variable_unit_inputs=parameters[2].split(',')
        self.controller.inputs['matrix_dim_unit']=variable_unit_inputs[:-1]
        self.controller.copy['matrix_dim_unit']=variable_unit_inputs[:-1][:]
                
        variable_dim_inputs=parameters[3].split(',')
        variable_dim_inputs=[int(i) for i in variable_dim_inputs[:-1]]
        self.controller.inputs['matrix_dimensions']=variable_dim_inputs
        self.controller.copy['matrix_dimensions']=variable_dim_inputs[:]
        
        self.define_variables_widgets(variable_name_input=self.controller.inputs['matrix_dim_name'], 
                                      variable_unit_input=self.controller.inputs['matrix_dim_unit'])
        
        #sets varaible ranges
        range_type=parameters[4].split(',')
        self.controller.inputs['matrix_range_type']=range_type[:-1]
        self.controller.copy['matrix_range_type']=range_type[:-1][:]
        
        range_inputs=[]
        for i in range(self.controller.inputs['num_variables_input']):
            range_input=parameters[6+i].split(',')
            range_inputs+=[[float(j) for j in range_input[:-1]]]
        self.controller.inputs['matrix_dim_range']=range_inputs
        self.controller.copy['matrix_dim_range']=range_inputs[:]
            
        for i in range(self.controller.inputs['num_variables_input']):
            if self.controller.inputs['matrix_range_type'][i]=='uniform':
                self.inputs_uniform_range(frame=self.define_variables_child_frame, 
                                          row=2*i, column=6, var_number=i, 
                                          variable_range_input=self.controller.inputs['matrix_dim_range'][i])
            elif self.controller.inputs['matrix_range_type'][i]=='custom':
                self.inputs_custom_range(frame=self.define_variables_child_frame, 
                                         row=2*i+1, column=6, var_number=i, 
                                         variable_range_input=self.controller.inputs['matrix_dim_range'][i])
        
        #displays matrix in text widget
        self.shared_func.display_matrix(frame=self.matrix_text_frame, 
                                        text_widget=self.matrix_text, 
                                        matrix=self.controller.inputs['matrix'], 
                                        ind_var=self.controller.inputs['ind_var_input'], 
                                        ind_var_unit=self.controller.inputs['ind_var_unit_input'], 
                                        num_var=self.controller.inputs['num_variables_input'],
                                        names=self.controller.inputs['matrix_dim_name'], 
                                        units=self.controller.inputs['matrix_dim_unit'], 
                                        dimensions=self.controller.inputs['matrix_dimensions'],
                                        range_type=self.controller.inputs['matrix_range_type'], 
                                        ranges=self.controller.inputs['matrix_dim_range'])                
        self.shared_func.save_button.config(state=tk.DISABLED)
        
    def reset_initial_inputs(self):
        """resets initial inputs if user input something incorrectly"""
        self.controller.inputs={
            #Initial inputs
            'ind_var_input':' ', #string
            'ind_var_unit_input':' ', #string
            'num_variables_input':0, #integer       
            #Inputs after specifying number of variables
            'variable_name_input':[], #list of strings
            'variable_unit_input':[], #list of strings
            'range_type_input': [], 
            'num_datapoints_input':[], #list of integers
            'variable_range_input':[], #nested list of floats, dim=2
            'is_included_in_file_input':[], #list of booleans/integers (0 or 1)
            'track_file_input':None, #boolean/integer (0 or 1)           
            #Listing variable names ordered by their dimension
            'unincluded_dim_name':[], #list of strings
            'included_dim_name':[], #list of strings
            'matrix_dim_name':[], #list of strings
            #Listing variable units ordered by their dimension
            'unincluded_dim_unit':[], #list of strings
            'included_dim_unit':[], #list of strings
            'matrix_dim_unit':[], #list of strings
            #Listing variable range types ordered by their dimension
            'unincluded_range_type': [],
            'included_range_type': [],
            'matrix_range_type': [],
            #Listing variable ranges ordered by their dimension
            'unincluded_dim_range':[], #nested list of floats, dim=2
            'included_dim_range':[], #nested list of floats, dim=2
            'matrix_dim_range':[], #nested list of floats, dim=2
            #Listing variable dimension lengths ordered by their dimension   
            'unincluded_dimensions':[], #list of integers
            'included_dimensions':[], #list of integers
            'matrix_dimensions':[], #list of integers
            #Constructing the matrix  
            'matrix':[], #original raw matrix that remains unchanged through various operations
            #Open file inputs
            'num_txt_files':1, #number of text files to be added to file list
            }
        self.controller.copy={
            'ind_var_input': ' ',
            'ind_var_unit_input':' ',
            'num_variables_input':0,
            'matrix_dim_name': [],
            'matrix_dim_unit': [],
            'matrix_dim_range': [],
            'matrix_dimensions': [],
            'matrix': []
            }
        
        #resets shared function variables
        self.shared_func.reset()
        
        #redo widgets
        self.matrix_text.delete(1.0, tk.END)    
        self.define_variables_child_frame.destroy()
        self.tracker_child_frame.destroy()           
        self.file_format_child_frame.destroy()      
        self.show_Button.config(state=tk.NORMAL)

    def reset_define_variables(self):
        self.controller.inputs={
            #Initial inputs
            'ind_var_input':self.controller.inputs['ind_var_input'], #string
            'ind_var_unit_input':self.controller.inputs['ind_var_unit_input'], #string
            'num_variables_input':self.controller.inputs['num_variables_input'], #integer       
            #Inputs after specifying number of variables
            'variable_name_input':[], #list of strings
            'variable_unit_input':[], #list of strings
            'range_type_input': [],
            'num_datapoints_input':[], #list of integers
            'variable_range_input':[], #nested list of floats, dim=2
            'is_included_in_file_input':[], #list of booleans/integers (0 or 1)
            'track_file_input':None, #boolean/integer (0 or 1)           
            #Listing variable names ordered by their dimension
            'unincluded_dim_name':[], #list of strings
            'included_dim_name':[], #list of strings
            'matrix_dim_name':[], #list of strings
            #Listing variable units ordered by their dimension
            'unincluded_dim_unit':[], #list of strings
            'included_dim_unit':[], #list of strings
            'matrix_dim_unit':[], #list of strings
            #Listing variable range types ordered by their dimension
            'unincluded_range_type': [],
            'included_range_type': [],
            'matrix_range_type': [],
            #Listing variable ranges ordered by their dimension
            'unincluded_dim_range':[], #nested list of floats, dim=2
            'included_dim_range':[], #nested list of floats, dim=2
            'matrix_dim_range':[], #nested list of floats, dim=2
            #Listing variable dimension lengths ordered by their dimension    
            'unincluded_dimensions':[], #list of integers
            'included_dimensions':[], #list of integers
            'matrix_dimensions':[], #list of integers
            #Constructing the matrix 
            'matrix':[], #original raw matrix that remains unchanged through various operations
            #Open file inputs
            'num_txt_files':1, #number of text files to be added to file list
            }
        self.controller.copy={
            'ind_var_input': self.controller.copy['ind_var_input'],
            'ind_var_unit_input':self.controller.copy['ind_var_unit_input'],
            'num_variables_input': self.controller.copy['num_variables_input'],
            'matrix_dim_name': [],
            'matrix_dim_unit': [],
            'matrix_dim_range': [],
            'matrix_dimensions': [],
            'matrix': []
            }
        
        #resets shared functions variables
        self.shared_func.reset()
        
        #redo widgets
        self.matrix_text.delete(1.0, tk.END)  
        self.tracker_child_frame.destroy()           
        self.file_format_child_frame.destroy()       
        self.confirm_button.config(state=tk.NORMAL)
  
#Manipulating matrix for data analysis and plots results
class Matrix_Fun(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller=controller
        self.shared_func=sf.Shared_Functions()        

        home_button=ttk.Button(self, text='Back to Home', command=lambda: self.controller.show_frame(StartPage))        
        home_button.grid(row=0, column=0, pady=20)        

        input_button=ttk.Button(self, text="Inputs", command=lambda: self.controller.show_frame(Inputs))
        input_button.grid(row=0, column=1, pady=20)
        
        edit_button=ttk.Button(self, text='Editor (Beta)', command=lambda: self.controller.show_frame(Editor))
        edit_button.grid(row=0, column=2, pady=20)
        
        fit_button=ttk.Button(self, text='Function Fit', command=lambda: self.controller.show_frame(Function_Fitting))
        fit_button.grid(row=0, column=3, pady=20)
        
        #Frames
        self.slice_frame=tk.Frame(self)
        self.slice_frame.grid(row=2, column=0, sticky=tk.N)
        self.slice_child_frame=tk.Frame(self.slice_frame)
        self.slice_child_frame.pack(side=tk.BOTTOM)        
       
        self.moveaxis_frame=tk.Frame(self)
        self.moveaxis_frame.grid(row=3, column=0, sticky=tk.N)
        self.moveaxis_child_frame=tk.Frame(self.moveaxis_frame)
        self.moveaxis_child_frame.pack(side=tk.BOTTOM)  
        
        self.numderiv_frame=tk.Frame(self)
        self.numderiv_frame.grid(row=4, column=0, sticky=tk.N)
        self.numderiv_child_frame=tk.Frame(self.numderiv_frame)
        self.numderiv_child_frame.pack(side=tk.BOTTOM) 
        
        self.fft_frame=tk.Frame(self)
        self.fft_frame.grid(row=5, column=0, sticky=tk.N)
        self.fft_child_frame=tk.Frame(self.fft_frame)
        self.fft_child_frame.pack(side=tk.BOTTOM)
        
        self.custom_frame=tk.Frame(self)
        self.custom_frame.grid(row=6, column=0, sticky=tk.N)
        self.custom_child_frame=tk.Frame(self.custom_frame)
        self.custom_child_frame.pack(side=tk.BOTTOM)
        
        self.reset_frame=tk.Frame(self)
        self.reset_frame.grid(row=7, column=0, sticky=tk.N)

        self.plot_button_frame=tk.Frame(self)
        self.plot_button_frame.grid(row=1, column=1, padx=50)
        self.plot_button_child_frame=tk.Frame(self.plot_button_frame)
        self.plot_button_child_frame.grid(row=1, column=0, columnspan=2)
        
        self.canvas_frame=tk.Frame(self)
        self.canvas_frame.grid(row=2, column=1, rowspan=5, columnspan=3, padx=50)
        self.canvas_child_frame=tk.Frame(self.canvas_frame)
        self.canvas_child_frame.pack(side=tk.TOP)               

        self.plot_opt_frame=tk.Frame(self)
        self.plot_opt_frame.grid(row=7, column=1, padx=50, sticky=tk.W)
        
        #Begining buttons
        slice_button=ttk.Button(self.slice_frame, text='Slice', command=self.slice_array_widgets)
        slice_button.pack(side=tk.TOP)

        moveaxis_button=ttk.Button(self.moveaxis_frame, text='Move Axis', command=self.move_axis_widgets)
        moveaxis_button.pack(side=tk.TOP)

        deriv_button=ttk.Button(self.numderiv_frame, text='Num Derivative', command=self.num_deriv_widgets)
        deriv_button.pack(side=tk.TOP)
        
        fft_button=ttk.Button(self.fft_frame, text="FFT", command=self.fft_widgets)
        fft_button.pack(side=tk.TOP)
        
        custom_button=ttk.Button(self.custom_frame, text='Custom', command=self.custom_widgets)
        custom_button.pack(side=tk.TOP)
        
        self.reset_button=ttk.Button(self.reset_frame, text='Reset All', command=self.reset, state=tk.DISABLED)
        self.reset_button.pack()
      
        plot_1d_button=ttk.Button(self.plot_button_frame, text='Plot 1D', command=self.plot_1d)
        plot_1d_button.grid(row=0, column=0)

        plot_2d_button=ttk.Button(self.plot_button_frame, text='Plot 2D', command=self.plot_2d)
        plot_2d_button.grid(row=0, column=1)
        
        #Canvas that contains the graph       
        canvas_container=tk.Canvas(self.canvas_child_frame, width=700, height=700)
        canvas_container.grid(row=0, column=0)
        
        hbar=ttk.Scrollbar(self.canvas_child_frame, orient=tk.HORIZONTAL)
        hbar.grid(row=1, column=0)
        vbar=ttk.Scrollbar(self.canvas_child_frame, orient=tk.VERTICAL)
        vbar.grid(row=0, column=1)
        
        hbar.config(command=canvas_container.xview)
        vbar.config(command=canvas_container.yview)
        canvas_container.config(xscrollcommand=hbar.set)
        canvas_container.config(yscrollcommand=vbar.set)       
        
        #Initial blank graph
        fig_size=(7, 7)
        f=fig.Figure(fig_size, dpi=100)        
        
        #Translating the figure as a widget
        canvas=FigureCanvasTkAgg(f, canvas_container)
        canvas_widget=canvas.get_tk_widget()
        canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        canvas_container.create_window(0, 0, window=canvas_widget)
        canvas_container.config(scrollregion=canvas_container.bbox(tk.ALL))

        self.toolbar=NavigationToolbar2Tk(canvas, self.canvas_frame)
        self.toolbar.pack(side=tk.BOTTOM)

        self.show_points=tk.IntVar()
        self.show_points.set(1)
        show_points_check=tk.Checkbutton(self.plot_opt_frame, text="Show Datapoints", variable=self.show_points).grid(row=0, column=0)
        
        self.connect_points=tk.IntVar()
        self.connect_points.set(1)
        connect_points_check=tk.Checkbutton(self.plot_opt_frame, text="Connect Datapoints", variable=self.connect_points).grid(row=0, column=1)
        
        #Misc.lists for plotting
        self.marker=[None, 'o']
        self.linestyle=['None', '-']
          
    def slice_array_widgets(self):
        """creates widgets to perform array slicing"""
        self.slice_child_frame.destroy()
        self.slice_child_frame=tk.Frame(self.slice_frame)
        self.slice_child_frame.pack(side=tk.BOTTOM)
        
        #widgets for slicing array
        slice_title=tk.Label(self.slice_child_frame, text='Choose Variables to Slice').grid(row=0, column=0)
        slice_title_note=tk.Label(self.slice_child_frame, text='Note: The slice point input must be of the form START, STOP, SKIP\n\tie. to obtain a slice of (0.1, 0.3, 0.5) for (0.1, 0.2, 0.3, 0.4, 0.5), the slice point is 0.1, 0.5, 1', 
                                  justify=tk.LEFT, 
                                  font=('Verdana', 6)).grid(row=1, column=0)
        
        slice_checkbox=[None]*self.controller.copy['num_variables_input'] #empty array to be filled later
        slice_points_entry=[None]*self.controller.copy['num_variables_input']        
        for i in range(self.controller.copy['num_variables_input']):
            slice_checkbox[i]=tk.IntVar()
            slice_checkbox_check=tk.Checkbutton(self.slice_child_frame, 
                                                text='%s (%d)'%(self.controller.copy['matrix_dim_name'][i], 
                                                                self.controller.copy['matrix_dimensions'][i]), 
                                                variable=slice_checkbox[i])
            slice_checkbox_check.grid(row=2+i, column=0)

            slice_points=tk.Label(self.slice_child_frame, text='slice point (start, stop, skip):').grid(row=2+i, column=1)
            slice_points_entry[i]=ttk.Entry(self.slice_child_frame) #NOTE: the input must be in the form outlined in 'slice_title_note'
            slice_points_entry[i].grid(row=2+i, column=2)
        
        #Confirm/update button
        confirm_button=ttk.Button(self.slice_child_frame, text='Confirm/Update', command= lambda slice_cb=slice_checkbox, 
                                                                                                 slice_e=slice_points_entry: self.slice_array_execute(slice_cb, 
                                                                                                                                                      slice_e))
        confirm_button.grid(row=3+self.controller.copy['num_variables_input'], column=0)
            
    def slice_array_execute(self, slice_cb, slice_e):
        """executes slice array function"""
        self.reset_button.config(state=tk.NORMAL)
        
        #Retrieving inputs from widgets defined in slice_array
        slice_checkbox_input, slice_points_input=[], []       
        for i in range(self.controller.copy['num_variables_input']):
            slice_checkbox_input+=[slice_cb[i].get()]
            slice_points_input+=[slice_e[i].get()]
        
        #Prepares the matrix for slicing and updates variable ranges
        slice_list=[slice(None, None, None)]*self.controller.copy['num_variables_input'] #Empty slice list to be filled later
        delete_index=[]
        for i in range(self.controller.copy['num_variables_input']):
            if slice_checkbox_input[i]==1:
                points_range=[float(j) for j in slice_points_input[i].split(',')]
                points_range[0]=self.controller.copy['matrix_dim_range'][i].index(points_range[0]) #index for first slice value
                points_range[1]=self.controller.copy['matrix_dim_range'][i].index(points_range[1])+1 #index for last slice value
                points_range[2]=int(points_range[2])+1 #skip value
                
                slice_list[i]=slice(points_range[0], points_range[1], points_range[2]) #Creating a list that will be used to slice the matrix 
                
                if ((points_range[1]-points_range[0]-1)/points_range[2])+1>1: #if the user still wants multiple values in that variable
                    range_keep_indices=np.arange(points_range[0], points_range[1], points_range[2]) #defines the range of values the user wants to keep
                    self.controller.copy['matrix_dim_range'][i]=[self.controller.copy['matrix_dim_range'][i][k] for k in range_keep_indices]
                    self.controller.copy['matrix_dimensions'][i]=len(self.controller.copy['matrix_dim_range'][i])
                else:
                    delete_index+=[i] #if the user wants to only keep one value of a certain axis, remove the entire axis from parameters
        
        #Removes axes in which there is only one value left and updates parameters accordingly
        keep_index=[i for i in range(self.controller.copy['num_variables_input']) if i not in delete_index]
        
        self.controller.copy['matrix_dim_name']=[self.controller.copy['matrix_dim_name'][i] for i in keep_index]
        self.controller.copy['matrix_dim_unit']=[self.controller.copy['matrix_dim_unit'][i] for i in keep_index]
        self.controller.copy['matrix_dim_range']=[self.controller.copy['matrix_dim_range'][i] for i in keep_index]
        self.controller.copy['matrix_range_type']=[self.controller.copy['matrix_range_type'][i] for i in keep_index]
        self.controller.copy['matrix_dimensions']=[self.controller.copy['matrix_dimensions'][i] for i in keep_index] 
        
        #Updates the number of variables to match the slicing
        self.controller.copy['num_variables_input']=len(self.controller.copy['matrix_dimensions'])
        
        #Slices the matrix according to the inputs provided
        self.controller.copy['matrix']=self.controller.copy['matrix'][tuple(slice_list)].reshape(tuple(self.controller.copy['matrix_dimensions']))
        
        #Redisplays the updated version of widgets
        self.slice_array_widgets()
    
    def move_axis_widgets(self):  
        """creates widgets to move axis"""
        self.moveaxis_child_frame.destroy()       
        self.moveaxis_child_frame=tk.Frame(self.moveaxis_frame)
        self.moveaxis_child_frame.pack(side=tk.BOTTOM)        
        
        #Widgets for moving axis
        move_axis_title=tk.Label(self.moveaxis_child_frame, text='Current Shape').grid(row=0, column=0)
        new_shape_title=tk.Label(self.moveaxis_child_frame, text='New Shape').grid(row=2, column=0)        
        
        axis_option, axis_variable=[None]*self.controller.copy['num_variables_input'], [None]*self.controller.copy['num_variables_input']
        for i in range(self.controller.copy['num_variables_input']):
            if i==(self.controller.copy['num_variables_input']-1):
                current_axis=tk.Label(self.moveaxis_child_frame, text='%s'%(self.controller.copy['matrix_dim_name'][i])) #makes the label look pretty at the end
            else:                     
                current_axis=tk.Label(self.moveaxis_child_frame, text='%sx'%(self.controller.copy['matrix_dim_name'][i]))
            current_axis.grid(row=1, column=i)             

            axis_variable[i]=tk.StringVar()
            axis_variable[i].set(self.controller.copy['matrix_dim_name'][i])
            axis_option[i]=ttk.OptionMenu(self.moveaxis_child_frame,
                                            axis_variable[i], 
                                            self.controller.copy['matrix_dim_name'][i], 
                                            *self.controller.copy['matrix_dim_name'])
            axis_option[i].grid(row=3, column=i)
            
        #Confirm/update button  
        confirm_button=ttk.Button(self.moveaxis_child_frame, 
                                  text='Confirm/Update', 
                                  command= lambda axis_order=axis_variable: self.move_axis_execute(axis_order))
        confirm_button.grid(row=5, column=0)
    
    def move_axis_execute(self, axis_order):
        """executes move axis function"""
        self.reset_button.config(state=tk.NORMAL)

        old_pos=[]
        new_pos=[]
        for i in range(self.controller.copy['num_variables_input']):
            old_pos+=[self.controller.copy['matrix_dim_name'].index(axis_order[i].get())]
            new_pos+=[i]
        
        #Moves axes in matrix
        self.controller.copy['matrix']=np.moveaxis(self.controller.copy['matrix'], old_pos, new_pos)
        
        #Updates parameters
        self.controller.copy['matrix_dim_name']=[self.controller.copy['matrix_dim_name'][i] for i in old_pos]
        self.controller.copy['matrix_dim_unit']=[self.controller.copy['matrix_dim_unit'][i] for i in old_pos]
        self.controller.copy['matrix_dimensions']=[self.controller.copy['matrix_dimensions'][i] for i in old_pos]
        self.controller.copy['matrix_range_type']=[self.controller.copy['matrix_range_type'][i] for i in old_pos]
        self.controller.copy['matrix_dim_range']=[self.controller.copy['matrix_dim_range'][i] for i in old_pos]
            
        #Redisplays the updated version of widgets
        self.move_axis_widgets()
           
    def num_deriv_widgets(self):
        """creates widgets for performing numerical derivative"""
        self.numderiv_child_frame.destroy()
        self.numderiv_child_frame=tk.Frame(self.numderiv_frame)
        self.numderiv_child_frame.pack(side=tk.BOTTOM)        
        
        #Widgets for performing numerical derivative
        num_deriv_title=tk.Label(self.numderiv_child_frame, text='Derivative wrt....').grid(row=0, column=0)
        
        wrt_variable=tk.StringVar()
        wrt_variable.set(self.controller.copy['matrix_dim_name'][0])
        wrt_option = ttk.OptionMenu(self.numderiv_child_frame, 
                                    wrt_variable, 
                                    self.controller.copy['matrix_dim_name'][0], 
                                    *self.controller.copy['matrix_dim_name'])
        wrt_option.grid(row=0, column=1)
        
        #Confirm/update button
        confirm_button=ttk.Button(self.numderiv_child_frame, 
                                  text='Confirm/Update', 
                                  command= lambda wrt_option_input=wrt_variable: self.num_deriv_execute(wrt_option_input))
        confirm_button.grid(row=0, column=2)
    
    def num_deriv_execute(self, wrt_option_input):
        """executes numerical derivative function"""
        self.reset_button.config(state=tk.NORMAL)

        option_input_index=self.controller.copy['matrix_dim_name'].index(wrt_option_input.get())        
        wrt_dim=self.controller.copy['matrix_dim_range'][option_input_index]
        
        #Performs numerical derivative on matrix using second order central differences
        self.controller.copy['matrix']=np.gradient(self.controller.copy['matrix'], 
                                                    wrt_dim, 
                                                    edge_order=2, 
                                                    axis=option_input_index)
        
        #displays the number of derivatives the user has taken and which variable it was with respect to
        self.controller.numderiv['num_deriv_counter']='\nd(%s)x'%(wrt_option_input.get()) + self.controller.numderiv['num_deriv_counter']
        num_deriv_label=tk.Label(self.numderiv_child_frame, text=self.controller.numderiv['num_deriv_counter']).grid(row=1, column=0)

        #Changes the name of the output value and its units (for use when plotting)
        self.controller.copy['ind_var_input']=r'$d_{%s}$'%(wrt_option_input.get())+self.controller.copy['ind_var_input']
        self.controller.copy['ind_var_unit_input']+='/%s'%(self.controller.copy['matrix_dim_unit'][option_input_index])

    def fft_widgets(self):
        """creates widgets to perform fast fourier transform"""
        self.fft_child_frame.destroy()
        self.fft_child_frame=tk.Frame(self.fft_frame)
        self.fft_child_frame.pack(side=tk.BOTTOM)        
        
        #widgets to for fourier transform
        fft_note=tk.Label(self.fft_child_frame, text='NOTE: Can only perform FFT on axis with uniform range type', 
                          justify=tk.LEFT, 
                          font=('verdana', 6)).grid(row=0, column=0)
        fft_title=tk.Label(self.fft_child_frame, text='FFT along....').grid(row=1, column=0)

        fft_variable=tk.StringVar()
        fft_variable.set(self.controller.copy['matrix_dim_name'][0])
        fft_option = ttk.OptionMenu(self.fft_child_frame, 
                                    fft_variable, 
                                    self.controller.copy['matrix_dim_name'][0], 
                                    *self.controller.copy['matrix_dim_name'])
        fft_option.grid(row=1, column=1)
        
        #Confirm/update button
        confirm_button=ttk.Button(self.fft_child_frame, 
                                  text='Confirm/Update', command= lambda fft_option_input=fft_variable: self.fft_execute(fft_option_input))
        confirm_button.grid(row=1, column=2)          
        
    def fft_execute(self, fft_option_input):      
        """executes fast fourier transform"""
        self.reset_button.config(state=tk.NORMAL)

        option_input_index=self.controller.copy['matrix_dim_name'].index(fft_option_input.get())        

        #perform fast fourier transform for matrix
        yfft=np.fft.fft(self.controller.copy['matrix'], axis=option_input_index)        
        frq=np.fft.fftfreq(self.controller.copy['matrix_dimensions'][option_input_index], 
                           self.controller.copy['matrix_dim_range'][option_input_index][1]-self.controller.copy['matrix_dim_range'][option_input_index][0])       


        #updates variable parameters
        for i in range(self.controller.copy['num_variables_input']): #need to recreate list instead of changing element in list because of how python references objects
            self.controller.copy['matrix_dim_range'][i]=self.controller.copy['matrix_dim_range'][i] if i!= option_input_index else list(frq[:len(frq)/2]) #only keep second half of transform
            self.controller.copy['matrix_dimensions'][i]=self.controller.copy['matrix_dimensions'][i] if i!= option_input_index else self.controller.copy['matrix_dimensions'][i]/2
            self.controller.copy['matrix_dim_name'][i]=self.controller.copy['matrix_dim_name'][i] if i!= option_input_index else 'Frequency'
            self.controller.copy['matrix_dim_unit'][i]=self.controller.copy['matrix_dim_unit'][i] if i!= option_input_index else 'Hz'
        
        #updates matrix (only keep second half of transform)
        slice_list=[slice(None, None, None)]*self.controller.copy['num_variables_input']
        slice_list[option_input_index]=slice(0, self.controller.copy['matrix_dimensions'][option_input_index])
        self.controller.copy['matrix']=np.abs(yfft)[tuple(slice_list)].reshape(tuple(self.controller.copy['matrix_dimensions']))   

        #show results button
        show_fft_button=ttk.Button(self.fft_child_frame, 
                                   text="Show Results", 
                                   command= lambda yfft=yfft[tuple(slice_list)].reshape(self.controller.copy['matrix_dimensions']),
                                                    xfft=list(frq[:len(frq/2)]): self.show_fft(yfft,
                                                                                                xfft))
        show_fft_button.grid(row=2, column=0)
    
    def show_fft(self, yfft, xfft):
        """show results of fast fourier transofrm in new window"""
        fft_window=tk.Toplevel(self)
        
        #show frequency
        freq_label=tk.Label(fft_window, text='Frequency').grid(row=0, column=1)
        freq_text=tk.Text(fft_window, height=5, width=220)
        freq_text.grid(row=1, column=0, columnspan=3, padx=10)
        freq_text.insert(tk.END, xfft)
        
        #show full fft
        fft_label=tk.Label(fft_window, text='FFT Results (Complex)').grid(row=2, column=0, pady=(10, 0))
        fft_text=tk.Text(fft_window, height=50, width=70)
        fft_text.grid(row=3, column=0, padx=10)        
        fft_text.insert(tk.END, yfft)
        
        #show only real part of fft
        fft_real_label=tk.Label(fft_window, text='FFT Results (Real)').grid(row=2, column=1, pady=(10, 0))
        fft_real_text=tk.Text(fft_window, height=50, width=70)
        fft_real_text.grid(row=3, column=1, padx=10)
        fft_real_text.insert(tk.END, yfft.real)
        
        #show only imaginary part of fft
        fft_imag_label=tk.Label(fft_window, text='FFT Results (Imaginary)').grid(row=2, column=2, pady=(10, 0))
        fft_imag_text=tk.Text(fft_window, height=50, width=70)
        fft_imag_text.grid(row=3, column=2, padx=10)
        fft_imag_text.insert(tk.END, yfft.imag)
       
    def custom_widgets(self):
        """creates widgets for custom function"""
        self.custom_child_frame.destroy()
        self.custom_child_frame=tk.Frame(self.custom_frame)
        self.custom_child_frame.pack(side=tk.BOTTOM)
        
        #labels of current parameters
        num_var_label=tk.Label(self.custom_child_frame, text="Num Var=%d"%(self.controller.copy['num_variables_input'])).grid(row=0, column=0)
        name_label=tk.Label(self.custom_child_frame, text="Var Names=%s"%(self.controller.copy['matrix_dim_name'])).grid(row=1, column=0)
        unit_label=tk.Label(self.custom_child_frame, text="Var Units=%s"%(self.controller.copy['matrix_dim_unit'])).grid(row=2, column=0)
        dimensions_label=tk.Label(self.custom_child_frame, text="Var Dim=%s"%(self.controller.copy['matrix_dimensions'])).grid(row=3, column=0)
        range_type_label=tk.Label(self.custom_child_frame, text="Range Type=%s"%(self.controller.copy['matrix_range_type'])).grid(row=4, column=0)
        
        range_text=[len(i)>8 and [i[0], i[1], '...', i[-2], i[-1]] or i for i in self.controller.copy['matrix_dim_range']]
        range_label=tk.Label(self.custom_child_frame, text="Var Range=%s"%(range_text)).grid(row=5, column=0)
        
        #apply custom function button
        apply_custom_button=ttk.Button(self.custom_child_frame, text="Apply Custom Function", command=self.custom_execute)
        apply_custom_button.grid(row=6, column=0)

    def custom_execute(self):
        """executes custom function from custom.py"""
        self.reset_button.config(state=tk.NORMAL)        
        import custom as cstm
        
        #performs custom function from custom.py
        self.controller.copy=cstm.custom_func(dictionary=self.controller.copy) #custom_func should return dictionary with updates matrix and parameters
        
        #updates parameter labels
        self.custom_widgets()
        
        #deletes library to save space
        del sys.modules['custom']
        
    def reset(self):      
        """resets matrix and parameters to original values"""
        self.controller.copy={
            'ind_var_input': self.controller.inputs['ind_var_input'],
            'ind_var_unit_input':self.controller.inputs['ind_var_unit_input'],
            'num_variables_input':self.controller.inputs['num_variables_input'],
            'matrix_dim_name': self.controller.inputs['matrix_dim_name'],
            'matrix_dim_unit': self.controller.inputs['matrix_dim_unit'],
            'matrix_range_type': self.controller.inputs['matrix_range_type'],
            'matrix_dim_range': self.controller.inputs['matrix_dim_range'],
            'matrix_dimensions': self.controller.inputs['matrix_dimensions'],
            'matrix': self.controller.inputs['matrix']
            }        
        
        self.controller.numderiv={
            'num_deriv_counter': ' '
            }

        #resets widgets
        self.slice_child_frame.destroy()
        self.slice_child_frame=tk.Frame(self.slice_frame)
        self.slice_child_frame.pack(side=tk.BOTTOM)
        
        self.moveaxis_child_frame.destroy()       
        self.moveaxis_child_frame=tk.Frame(self.moveaxis_frame)
        self.moveaxis_child_frame.pack(side=tk.BOTTOM)        

        self.numderiv_child_frame.destroy()
        self.numderiv_child_frame=tk.Frame(self.numderiv_frame)
        self.numderiv_child_frame.pack(side=tk.BOTTOM)      
        
        self.fft_child_frame.destroy()
        self.fft_child_frame=tk.Frame(self.fft_frame)
        self.fft_child_frame.pack(side=tk.BOTTOM)    
        
        self.custom_child_frame.destroy()
        self.custom_child_frame=tk.Frame(self.custom_frame)
        self.custom_child_frame.pack(side=tk.BOTTOM)        
        
        self.plot_button_child_frame.destroy()
        self.plot_button_child_frame=tk.Frame(self.plot_button_frame)
        self.plot_button_child_frame.grid(row=1, column=0, columnspan=2)        
    
    def plot_1d(self):
        """creates widgets for plotting matrix in 1D"""
        self.plot_button_child_frame.destroy()
        self.plot_button_child_frame=tk.Frame(self.plot_button_frame)
        self.plot_button_child_frame.grid(row=1, column=0, columnspan=2)        
        #Plot One in All button
        plot_1d_oneinall_button=ttk.Button(self.plot_button_child_frame, text='Plot One in All', command=self.plot_1d_oneinall)
        plot_1d_oneinall_button.grid(row=1, column=0)
        #Plot Multiple button
        plot_1d_multiple_button=ttk.Button(self.plot_button_child_frame, text='Plot Multiple', command=self.plot_1d_multiple)
        plot_1d_multiple_button.grid(row=1, column=1)
        #Plot All in One button
        plot_1d_allinone_button=ttk.Button(self.plot_button_child_frame, text='Plot All in One', command=self.plot_1d_allinone)
        plot_1d_allinone_button.grid(row=1, column=2)
           
    def plot_1d_oneinall(self):
        """plot matrix in single 1D graphs"""
        self.canvas_child_frame.destroy()
        self.toolbar.destroy()
        
        self.canvas_child_frame=tk.Frame(self.canvas_frame)
        self.canvas_child_frame.pack()
    
        simulated_dimensions=self.shared_func.simulated_dim(self.controller.copy['matrix_dimensions'])
        if len(self.controller.copy['matrix_dimensions'])>1:    
            #formatting the plots
            self.shared_func.plot_oneinall_format(dimensions=self.controller.copy['matrix_dimensions'], 
                                                  ranges=self.controller.copy['matrix_dim_range'],
                                                    names=self.controller.copy['matrix_dim_name'],
                                                    units=self.controller.copy['matrix_dim_unit'],
                                                    ind_var=self.controller.copy['ind_var_input'],
                                                    ind_var_unit=self.controller.copy['ind_var_unit_input'])
            
            #plot data
            for i, j in itertools.product(range(simulated_dimensions[-1]/simulated_dimensions[1]), 
                                          range(self.controller.copy['matrix_dimensions'][-2])): 
                if len(self.controller.copy['matrix_dimensions'])==2:
                    self.shared_func.ax[j].plot(self.controller.copy['matrix_dim_range'][-1], 
                                                self.controller.copy['matrix'].reshape(-1, self.controller.copy['matrix_dimensions'][-1])[j], 
                                                linestyle=self.linestyle[self.connect_points.get()], 
                                                marker=self.marker[self.show_points.get()], 
                                                label=self.shared_func.plot_labels[i][j])
                    self.shared_func.ax[j].legend()            
                else:
                    self.shared_func.ax[i, j].plot(self.controller.copy['matrix_dim_range'][-1], 
                                                self.controller.copy['matrix'].reshape(-1, self.controller.copy['matrix_dimensions'][-1])[i*self.controller.copy['matrix_dimensions'][-2]+j], 
                                                linestyle=self.linestyle[self.connect_points.get()], 
                                                marker=self.marker[self.show_points.get()], 
                                                label=self.shared_func.plot_labels[i][j])                     
                    self.shared_func.ax[i, j].legend() 
                
        else:
            self.shared_func.invalid_plot()
        
        self.embed_graph(fig=self.shared_func.f, width=self.shared_func.graph_width, height=self.shared_func.graph_height)        

    def plot_1d_multiple(self):
        """plots matrix as series of lines in a series of plots"""
        self.canvas_child_frame.destroy()
        self.toolbar.destroy()
        
        self.canvas_child_frame=tk.Frame(self.canvas_frame)
        self.canvas_child_frame.pack()
               
        simulated_dimensions=self.shared_func.simulated_dim(self.controller.copy['matrix_dimensions'])       
        if len(self.controller.copy['matrix_dimensions'])>2:
            #formatting the plots
            self.shared_func.plot_multiple_format(dimensions=self.controller.copy['matrix_dimensions'], 
                                                  ranges=self.controller.copy['matrix_dim_range'],
                                                    names=self.controller.copy['matrix_dim_name'],
                                                    units=self.controller.copy['matrix_dim_unit'],
                                                    ind_var=self.controller.copy['ind_var_input'],
                                                    ind_var_unit=self.controller.copy['ind_var_unit_input'])     
                                                    
            for i, j in itertools.product(range(simulated_dimensions[-1]/simulated_dimensions[2]), 
                                          range(self.controller.copy['matrix_dimensions'][-3])):
                if len(self.controller.copy['matrix_dimensions'])==3:
                    for k in range(self.controller.copy['matrix_dimensions'][-2]):
                        self.shared_func.ax[j].plot(self.controller.copy['matrix_dim_range'][-1],
                                                    self.controller.copy['matrix'].reshape(-1, self.controller.copy['matrix_dimensions'][-1])[j*self.controller.copy['matrix_dimensions'][-2]+k], #to obtain the correct value for the index of a series of 1D lines, 
                                                                                                                                                                                                #multiply the value of the current iterator by the length of all its subsequent iterators
                                                    linestyle=self.linestyle[self.connect_points.get()], 
                                                    marker=self.marker[self.show_points.get()], 
                                                    label='%f%s'%(self.controller.copy['matrix_dim_range'][-2][k], 
                                                                  self.controller.copy['matrix_dim_unit'][-2]))                     
                    self.shared_func.ax[j].legend()                
                
                else:
                    for k in range(self.controller.copy['matrix_dimensions'][-2]):
                        self.shared_func.ax[i, j].plot(self.controller.copy['matrix_dim_range'][-1],
                                                        self.controller.copy['matrix'].reshape(-1, self.controller.copy['matrix_dimensions'][-1])[i*self.controller.copy['matrix_dimensions'][-3]*self.controller.copy['matrix_dimensions'][-2]+
                                                                                                                                                    j*self.controller.copy['matrix_dimensions'][-2]+
                                                                                                                                                    k], #to obtain the correct value for the index of a series of 1D lines, 
                                                                                                                                                    #multiply the value of the current iterator by the length of all its subsequent iterators  
                                                        linestyle=self.linestyle[self.connect_points.get()], 
                                                        marker=self.marker[self.show_points.get()], 
                                                        label='%f%s'%(self.controller.copy['matrix_dim_range'][-2][k], 
                                                                      self.controller.copy['matrix_dim_unit'][-2]))                     
                    self.shared_func.ax[i, j].legend()
                        
        else:
            self.shared_func.invalid_plot() 
        
        self.embed_graph(fig=self.shared_func.f, width=self.shared_func.graph_width, height=self.shared_func.graph_height)          

    def plot_1d_allinone(self):
        """plots matrix in one plot as series of lines"""
        self.canvas_child_frame.destroy()
        self.toolbar.destroy()
        
        self.canvas_child_frame=tk.Frame(self.canvas_frame)
        self.canvas_child_frame.pack()

        simulated_dimensions=self.shared_func.simulated_dim(self.controller.copy['matrix_dimensions'])

        #formatting the plot
        self.shared_func.plot_allinone_format(dimensions=self.controller.copy['matrix_dimensions'], 
                                                  ranges=self.controller.copy['matrix_dim_range'],
                                                    names=self.controller.copy['matrix_dim_name'],
                                                    units=self.controller.copy['matrix_dim_unit'],
                                                    ind_var=self.controller.copy['ind_var_input'],
                                                    ind_var_unit=self.controller.copy['ind_var_unit_input'])       
        
        for i in range(simulated_dimensions[-1]/simulated_dimensions[0]):
            self.shared_func.ax.plot(self.controller.copy['matrix_dim_range'][-1], 
                                     self.controller.copy['matrix'].reshape(-1, self.controller.copy['matrix_dimensions'][-1])[i], 
                                        linestyle=self.linestyle[self.connect_points.get()], 
                                        marker=self.marker[self.show_points.get()], 
                                        label=self.shared_func.plot_labels[i])                   
        self.shared_func.ax.legend()


        self.embed_graph(fig=self.shared_func.f, width=self.shared_func.graph_width, height=self.shared_func.graph_height)        
        
    def plot_2d(self):
        """creates widgets for plotting matrix in 1D"""        
        self.plot_button_child_frame.destroy()
        self.plot_button_child_frame=tk.Frame(self.plot_button_frame)
        self.plot_button_child_frame.grid(row=1, column=0, columnspan=2)
        #Plot 2D surface plot button
        d2_surface_button=ttk.Button(self.plot_button_child_frame, text='2D Surface', command=self.plot_2d_surface)
        d2_surface_button.grid(row=2, column=0)
        #Plot 2D contour plot button
        d2_contour_button=ttk.Button(self.plot_button_child_frame, text='2D Contour', command=self.plot_2d_contour)
        d2_contour_button.grid(row=2, column=1)        
        
    def plot_2d_surface(self):
        """plots 2D surface plots for matrix"""
        self.canvas_child_frame.destroy()
        self.toolbar.destroy()
        
        self.canvas_child_frame=tk.Frame(self.canvas_frame)
        self.canvas_child_frame.pack()
        
        simulated_dimensions=self.shared_func.simulated_dim(self.controller.copy['matrix_dimensions'])
        x, y=np.meshgrid(self.controller.copy['matrix_dim_range'][-1], self.controller.copy['matrix_dim_range'][-2])
        
        #multiple 2d plots
        if len(self.controller.copy['matrix_dimensions'])>2:            
            #formatting the plot
            self.shared_func.plot_multiplesurface_format(dimensions=self.controller.copy['matrix_dimensions'], 
                                                          ranges=self.controller.copy['matrix_dim_range'],
                                                            names=self.controller.copy['matrix_dim_name'],
                                                            units=self.controller.copy['matrix_dim_unit'],
                                                            ind_var=self.controller.copy['ind_var_input'],
                                                            ind_var_unit=self.controller.copy['ind_var_unit_input'])
            #reshapes matrix into array of 2d arrays
            flattened_matrix=self.controller.copy['matrix'].reshape(-1, 
                                                                    self.controller.copy['matrix_dimensions'][-2], 
                                                                    self.controller.copy['matrix_dimensions'][-1])            
            #begin plotting
            for i, j in itertools.product(range(simulated_dimensions[-1]/simulated_dimensions[2]), 
                                          range(self.controller.copy['matrix_dimensions'][-3])):
                self.shared_func.ax[i][j].plot_surface(x, y, flattened_matrix[i*self.controller.copy['matrix_dimensions'][-3]+j], rstride=1, cstride=1)                                           
        
        #single 2d plot
        elif len(self.controller.copy['matrix_dimensions'])==2:
            #formatting the plot
            self.shared_func.plot_singlesurface_format(names=self.controller.copy['matrix_dim_name'],
                                                       units=self.controller.copy['matrix_dim_unit'],
                                                        ind_var=self.controller.copy['ind_var_input'],
                                                        ind_var_unit=self.controller.copy['ind_var_unit_input'])
            #begin plotting
            self.shared_func.ax.plot_surface(x, y, self.controller.copy['matrix'], rstride=1, cstride=1)
                      
        else: 
            self.shared_func.invalid_plot()        
        
        self.embed_graph(fig=self.shared_func.f, width=self.shared_func.graph_width, height=self.shared_func.graph_height)        
        
    def plot_2d_contour(self):
        """plots 2D contour plot for matrix"""
        self.canvas_child_frame.destroy()
        self.toolbar.destroy()
        
        self.canvas_child_frame=tk.Frame(self.canvas_frame)
        self.canvas_child_frame.pack()
        
        #prepare variables for plotting later
        simulated_dimensions=self.shared_func.simulated_dim(self.controller.copy['matrix_dimensions'])
        x, y=np.meshgrid(self.controller.copy['matrix_dim_range'][-1], self.controller.copy['matrix_dim_range'][-2])        
        
        #plot multiple contour plots
        if len(self.controller.copy['matrix_dimensions'])>2: 
            width=5*self.controller.copy['matrix_dimensions'][-3]
            height=5*simulated_dimensions[-1]/simulated_dimensions[2]
            fig_size=(width, height)
            f=fig.Figure(figsize=fig_size, dpi=100)
            
            flattened_matrix=self.controller.copy['matrix'].reshape(-1, 
                                                                    self.controller.copy['matrix_dimensions'][-2], 
                                                                    self.controller.copy['matrix_dimensions'][-1])
            
            variable_counter=[0]*len(simulated_dimensions[:-1]) #empty list to be filled later        
            for i, j in itertools.product(range(simulated_dimensions[-1]/simulated_dimensions[2]), 
                                          range(self.controller.copy['matrix_dimensions'][-3])):
                    subplot_title=' ' #create subplot title
                    for m in range(len(self.controller.copy['matrix_dimensions'][:-2])):
                        if (i*self.controller.copy['matrix_dimensions'][-3]+j)%(simulated_dimensions[2+m]/simulated_dimensions[1])==0 and (i*self.controller.copy['matrix_dimensions'][-3]+j)!=0:
                            variable_counter[m]=0
                            variable_counter[m+1]+=1
                        else:
                            variable_counter[0]=(i*self.controller.copy['matrix_dimensions'][-3]+j)%self.controller.copy['matrix_dimensions'][-3] 
                        subplot_title+='%f%s,'%(self.controller.copy['matrix_dim_range'][-3-m][variable_counter[m]], self.controller.copy['matrix_dim_unit'][-3-m])
                    
                    ax=f.add_subplot(simulated_dimensions[-1]/simulated_dimensions[2], 
                                     self.controller.copy['matrix_dimensions'][-3], 
                                        i*self.controller.copy['matrix_dimensions'][-3]+j+1)   
                    #format subplots
                    ax.set_title(subplot_title)
                    ax.set_xlabel('%s (%s)'%(self.controller.copy['matrix_dim_name'][-1], self.controller.copy['matrix_dim_unit'][-1]))
                    ax.set_ylabel('%s (%s)'%(self.controller.copy['matrix_dim_name'][-2], self.controller.copy['matrix_dim_unit'][-2]))
                    
                    #create contour plot
                    contour=ax.contourf(x, y, flattened_matrix[i*self.controller.copy['matrix_dimensions'][-3]+j])
                    f.colorbar(contour)
        
        #plot single contour plot            
        elif len(self.controller.copy['matrix_dimensions'])==2:
            width=7
            height=7
            fig_size=(width, height)
            f=fig.Figure(fig_size, dpi=100)
            ax=f.add_subplot(111)
            
            #format plot
            ax.set_xlabel('%s (%s)'%(self.controller.copy['matrix_dim_name'][-1], self.controller.copy['matrix_dim_unit'][-1]))
            ax.set_ylabel('%s (%s)'%(self.controller.copy['matrix_dim_name'][-2], self.controller.copy['matrix_dim_unit'][-2]))           
            
            #create contour plot
            contour=ax.contourf(x, y, self.controller.copy['matrix'])           
            f.colorbar(contour)
        
        #plot for invalid dimensions
        else:      
            width=7
            height=7
            fig_size=(width, height)
            f=fig.Figure(fig_size, dpi=100)            
            ax=f.add_subplot(111)
            ax.text(0.5, 0.5, 'Cannot plot 2D using dimensions given')        
        
        #embed graph
        self.embed_graph(fig=f, width=width, height=height)
           
    def embed_graph(self, fig, width, height): 
        """embeds graph in Matrix_Fun page"""
        canvas_width=width*100
        canvas_height=height*100
        if canvas_width>1100:
            canvas_width=1100
        if canvas_height>800:
            canvas_height=800
            
        #canvas that contains the graph
        canvas_container=tk.Canvas(self.canvas_child_frame, width=canvas_width, height=canvas_height)
        canvas_container.grid(row=0, column=0)
        
        hbar=ttk.Scrollbar(self.canvas_child_frame, orient=tk.HORIZONTAL)
        hbar.grid(row=1, column=0)            
        vbar=ttk.Scrollbar(self.canvas_child_frame, orient=tk.VERTICAL)
        vbar.grid(row=0, column=1)
            
        hbar.config(command=canvas_container.xview)
        vbar.config(command=canvas_container.yview)
        canvas_container.config(xscrollcommand=hbar.set)
        canvas_container.config(yscrollcommand=vbar.set)
        
        #translating figure as widget
        canvas=FigureCanvasTkAgg(fig, canvas_container)
        canvas_widget=canvas.get_tk_widget()
        canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
                
        canvas_container.create_window(0, 0, window=canvas_widget)
        canvas_container.config(scrollregion=canvas_container.bbox(tk.ALL))
                
        self.toolbar=NavigationToolbar2Tk(canvas, self.canvas_frame)
        self.toolbar.pack(side=tk.BOTTOM) 
                
#Allows for editing matrix by defining an entire new variable or add values to existing variable
class Editor(tk.Frame):
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller=controller
        self.shared_func=sf.Shared_Functions()
        
        home_button=ttk.Button(self, text='Back to Home', command=lambda: self.controller.show_frame(StartPage))     
        home_button.grid(row=0, column=0, pady=20)
        
        input_button=ttk.Button(self, text="Inputs", command=lambda: self.controller.show_frame(Inputs))
        input_button.grid(row=0, column=1, pady=20)

        fun_button=ttk.Button(self, text="Matrix Fun", command=lambda: self.controller.show_frame(Matrix_Fun))
        fun_button.grid(row=0, column=2, pady=20)
        
        fit_button=ttk.Button(self, text='Function Fit', command=lambda: self.controller.show_frame(Function_Fitting))
        fit_button.grid(row=0, column=3, pady=20)
                
        #Frames
        self.matrix_text_frame=tk.Frame(self)
        self.matrix_text_frame.grid(row=1, column=1, padx=20, rowspan=2, columnspan=3)        
        
        self.edit_matrix_frame=tk.Frame(self)
        self.edit_matrix_frame.grid(row=1, column=0)
        self.edit_matrix_child_frame=tk.Frame(self.edit_matrix_frame)
        self.edit_matrix_child_frame.pack(side=tk.BOTTOM)
        
        self.def_new_var_frame=tk.Frame(self.edit_matrix_child_frame)
        self.def_new_var_frame.grid(row=0, column=0)
        self.def_new_var_child_frame=tk.Frame(self.def_new_var_frame)
        self.def_new_var_child_frame.pack(side=tk.BOTTOM)
        
        self.insert_value_frame=tk.Frame(self.edit_matrix_child_frame)
        self.insert_value_frame.grid(row=1, column=0)
        self.insert_value_child_frame=tk.Frame(self.insert_value_frame)
        self.insert_value_child_frame.pack(side=tk.BOTTOM)
        
        #beginning widgets
        edit_matrix_title=tk.Label(self.edit_matrix_frame, text='Edit Matrix').pack(side=tk.TOP)
        
        insert_value_button=ttk.Button(self.insert_value_frame, text="Insert Value", command=self.insert_value_inputs)
        insert_value_button.pack(side=tk.TOP)
        
        def_new_var_button=ttk.Button(self.def_new_var_frame, text="Define New Variable", command=self.def_new_var_inputs)
        def_new_var_button.pack(side=tk.TOP)
        
        self.matrix_text=tk.Text(self.matrix_text_frame, height=20, width=70)
        self.matrix_text.pack(side=tk.TOP)
        
        #variables to be used in this class
        self.variable_range=[None] #needs to be put in list so that a function can refer to the list initially but the element inside can change with user input
        self.range_type=['']
    
    def def_new_var_inputs(self):
        """creates widgets for user to add a new variable to the existing matrix"""
        self.def_new_var_child_frame.destroy()
        self.shared_func.reset()
        
        self.def_new_var_child_frame=tk.Frame(self.def_new_var_frame)
        self.def_new_var_child_frame.pack(side=tk.BOTTOM)
        
        #Widgets to allow user to define variable parameters
        variable_name=tk.Label(self.def_new_var_child_frame, text="Var Name").grid(row=0, column=0)            
        variable_name_entry=ttk.Entry(self.def_new_var_child_frame)
        variable_name_entry.grid(row=0, column=1)
        
        variable_unit=tk.Label(self.def_new_var_child_frame, text='Units').grid(row=0, column=2)            
        variable_unit_entry=ttk.Entry(self.def_new_var_child_frame)
        variable_unit_entry.grid(row=0, column=3)
                
        file_variable=tk.IntVar()
        file_variable_check1=tk.Radiobutton(self.def_new_var_child_frame, 
                                            text="(%s) is included in file"%(self.controller.inputs['matrix_dim_unit'][-1]), 
                                            variable=file_variable,
                                            value=1).grid(row=0, column=4, sticky=tk.W)
        if self.controller.inputs['num_variables_input']>1:
            file_variable_check2=tk.Radiobutton(self.def_new_var_child_frame, 
                                                text='(%s, %s) is included in file'%(self.controller.inputs['matrix_dim_unit'][-1], 
                                                                                    self.controller.inputs['matrix_dim_unit'][-2]), 
                                                variable=file_variable,
                                                value=2).grid(row=1, column=4, sticky=tk.W) 

        self.uniform_range_button=ttk.Button(self.def_new_var_child_frame, text='Uniform Range?')
        self.uniform_range_button.grid(row=2, column=0)
        self.custom_range_button=ttk.Button(self.def_new_var_child_frame, text='Custom Range?')
        self.custom_range_button.grid(row=3, column=0)        
        self.uniform_range_button.config(command=lambda frame=self.def_new_var_child_frame, 
                                                         row=2, 
                                                         column=1, 
                                                         uniform_button=self.uniform_range_button, 
                                                         custom_button=self.custom_range_button: self.editor_uniform_range(frame, 
                                                                                                                           row, 
                                                                                                                           column, 
                                                                                                                           uniform_button, 
                                                                                                                           custom_button))
        self.custom_range_button.config(command=lambda frame=self.def_new_var_child_frame, 
                                                        row=3, 
                                                        column=1, 
                                                        uniform_button=self.uniform_range_button, 
                                                        custom_button=self.custom_range_button: self.editor_custom_range(frame, 
                                                                                                                         row, 
                                                                                                                         column, 
                                                                                                                         uniform_button, 
                                                                                                                         custom_button)) 
        
        current_array_label=tk.Label(self.def_new_var_child_frame, text='Value of current matrix').grid(row=4, column=0, pady=(0, 10))
        current_array_entry=ttk.Entry(self.def_new_var_child_frame)
        current_array_entry.grid(row=4, column=1, pady=(0, 10))
        
        self.shared_func.file_format_widgets(frame=self.def_new_var_child_frame, row=5, column=0)        

        track_file=tk.IntVar()
        track_file_check=tk.Checkbutton(self.def_new_var_child_frame, text="Would you like to track your files?", variable=track_file)
        track_file_check.grid(row=6, column=0, columnspan=3, padx=10)
        
        #confirm button
        self.confirm_button=ttk.Button(self.def_new_var_child_frame, 
                                       text="Confirm", 
                                       command= lambda var_name=variable_name_entry, 
                                                       var_unit=variable_unit_entry, 
                                                       list_type_check=self.range_type, 
                                                       var_range=self.variable_range,
                                                       current_val=current_array_entry,
                                                       file_var=file_variable, 
                                                       track_file=track_file, 
                                                       comments=self.shared_func.comments_entry, 
                                                       delimiter=self.shared_func.delimiter_entry, 
                                                       skiprows=self.shared_func.skiprows_entry, 
                                                       use_cols=self.shared_func.usecols_entry: self.def_new_var_execute(var_name, 
                                                                                                                  var_unit, 
                                                                                                                  list_type_check, 
                                                                                                                  var_range, 
                                                                                                                  current_val,
                                                                                                                  file_var, 
                                                                                                                  track_file, 
                                                                                                                  comments, 
                                                                                                                  delimiter, 
                                                                                                                  skiprows, 
                                                                                                                  use_cols))                    
        self.confirm_button.grid(row=7, column=0)  
    
    def editor_uniform_range(self, frame, row, column, uniform_button, custom_button):
        """creates uniform range in the editor page"""
        self.shared_func.build_uniform_range(frame=frame, row=row, column=column, uniform_button=uniform_button, custom_button=custom_button, columnspan=2)
        self.variable_range[0]=self.shared_func.variable_range
        self.range_type[0]=self.shared_func.range_type
        
    def editor_custom_range(self, frame, row, column, uniform_button, custom_button):
        """creates custom range in the editor page"""
        self.shared_func.build_custom_range(frame=frame, row=row, column=column, uniform_button=uniform_button, custom_button=custom_button, columnspan=2)
        self.variable_range[0]=self.shared_func.variable_range
        self.range_type[0]=self.shared_func.range_type

    def def_new_var_execute(self, var_name, var_unit, list_type_check, var_range, current_val, file_var, track_file, comments, delimiter, skiprows, use_cols):
        """edits matrix with newly defined variable"""
        self.def_new_var_update(var_name=var_name, 
                                var_unit=var_unit,
                                list_type_check=list_type_check,
                                var_range=var_range)
      
        #prepares dimensions length and names for uploading files
        separate_array_dimensions=self.controller.inputs['matrix_dimensions'][:]
        separate_array_dimensions[0]-=1
        if file_var.get()==1:
            file_list_dimensions, file_list_dim_name=separate_array_dimensions[:-1], self.controller.inputs['matrix_dim_name'][:-1]
        elif file_var.get()==2:
            file_list_dimensions, file_list_dim_name=separate_array_dimensions[:-2], self.controller.inputs['matrix_dim_name'][:-2]           
        num_txt_files=1
        for i in range(len(file_list_dimensions)):
            num_txt_files*=file_list_dimensions[i]
        
        #upload files
        if track_file.get()==1: #checks for whether the user would like to track their files
            self.shared_func.tracker(frame=self.def_new_var_child_frame, 
                                     dimensions=file_list_dimensions, 
                                     dim_name=file_list_dim_name, 
                                     row=8, 
                                     column=0)
        else: #creates file list without tracker function           
            while len(self.shared_func.file_list)<num_txt_files:
                add_file=self.shared_func.select_files(self.shared_func.folder)
                if add_file==[]: #if user cancels adding files, assumes the user would like to start everything over
                    break
                add_file.append(add_file.pop(0)) #puts the first file selected back to the beginning because tkinter is weird like that (tkinter will put the first file selected at the end)
                self.shared_func.file_list+=add_file          
        if len(self.shared_func.file_list)!=num_txt_files: #Checks to make sure the file list is the right size
            mb.showerror("Error", "File list incompatible with amount of data specified, please reconfirm inputs")
            self.shared_func.file_list=[] #resets the define variables inputs         
            print 'Do more things'   
       
       #creates new overall matrix
        self.shared_func.create_matrix(comments=comments, 
                                       delimiter=delimiter, 
                                       skiprows=skiprows, 
                                       usecolumns=use_cols, 
                                       dimensions=separate_array_dimensions, 
                                       file_list=self.shared_func.file_list)
        
        #inserts old matrix into new one
        current_array_value=float(current_val.get()) #new variable value of old matrix
        insertion_index=0 
        for i in range(len(self.controller.inputs['matrix_dim_range'][0])):
            if current_array_value>self.controller.inputs['matrix_dim_range'][0][i]:
                insertion_index+=1 #seems trivial for a uniform range but allows for insertion into a custom range
            else:
                break       
        self.controller.inputs['matrix']=np.insert(self.shared_func.matrix, insertion_index, self.controller.inputs['matrix'], axis=0)
        self.controller.copy['matrix']=self.controller.inputs['matrix'][:]

        self.shared_func.display_matrix(frame=self.matrix_text_frame, 
                                        text_widget=self.matrix_text, 
                                        matrix=self.controller.inputs['matrix'], 
                                        ind_var=self.controller.inputs['ind_var_input'], 
                                        ind_var_unit=self.controller.inputs['ind_var_unit_input'], 
                                        num_var=self.controller.inputs['num_variables_input'],
                                        names=self.controller.inputs['matrix_dim_name'], 
                                        units=self.controller.inputs['matrix_dim_unit'], 
                                        dimensions=self.controller.inputs['matrix_dimensions'],
                                        range_type=self.controller.inputs['matrix_range_type'], 
                                        ranges=self.controller.inputs['matrix_dim_range'])    
    
    def def_new_var_update(self, var_name, var_unit, list_type_check, var_range):
        """updates parameters of new matrix"""
        self.controller.inputs['num_variables_input']+=1
        self.controller.copy['num_variables_input']+=1 #allows user to edit matrix and then continue manipulating/fitting it without closing the window               
        #edits dimensions names
        self.controller.inputs['matrix_dim_name']=[var_name.get()]+self.controller.inputs['matrix_dim_name']
        self.controller.copy['matrix_dim_name']=self.controller.inputs['matrix_dim_name'][:]
        #edits dimensions units
        self.controller.inputs['matrix_dim_unit']=[var_unit.get()]+self.controller.inputs['matrix_dim_unit']
        self.controller.copy['matrix_dim_unit']=self.controller.inputs['matrix_dim_unit'][:]
        #edits dimension range types
        self.controller.inputs['matrix_range_type']=[list_type_check[0]]+self.controller.inputs['matrix_range_type']
        self.controller.copy['matrix_range_type']=self.controller.inputs['matrix_range_type'][:]
        #edits dimensions ranges
        var_range_input=[float(j) for j in var_range[0].get().split(',')]        
        if list_type_check[0]=='uniform':
            self.controller.inputs['matrix_dim_range']=[list(np.linspace(var_range_input[0], var_range_input[1], var_range_input[2]))]+self.controller.inputs['matrix_dim_range']
            self.controller.copy['matrix_dim_range']=self.controller.inputs['matrix_dim_range'][:]
        elif list_type_check[0]=='custom':
            self.controller.inputs['matrix_dim_range']=[list(var_range_input)]+self.controller.inputs['matrix_dim_range']
            self.controller.copy['matrix_dim_range']=self.controller.inputs['matrix_dim_range'][:]       
        else:
            mb.showerror('Error', 'Please specify range and current array value')
        #edits dimensions lengths 
        self.controller.inputs['matrix_dimensions']=[len(self.controller.inputs['matrix_dim_range'][0])]+self.controller.inputs['matrix_dimensions']
        self.controller.copy['matrix_dimensions']=self.controller.inputs['matrix_dimensions'][:]
        
    def insert_value_inputs(self):
        """creates widgets for user to insert a new value into existing matrix"""
        self.insert_value_child_frame.destroy()
        self.shared_func.reset()

        self.insert_value_child_frame=tk.Frame(self.insert_value_frame)
        self.insert_value_child_frame.pack(side=tk.BOTTOM)

        #Widgets to allow user to define value parameters
        choose_variable_label=tk.Label(self.insert_value_child_frame, text='Choose Variable to Add to').grid(row=0, column=0)
        addto_variable=tk.StringVar()
        addto_variable.set(self.controller.inputs['matrix_dim_name'][0])
        addto_option = ttk.OptionMenu(self.insert_value_child_frame, addto_variable, self.controller.inputs['matrix_dim_name'][0], *self.controller.inputs['matrix_dim_name'][:-1])
        addto_option.grid(row=0, column=1)
        
        add_value_label=tk.Label(self.insert_value_child_frame, text='What value would you like to add?').grid(row=0, column=2)
        add_value_entry=ttk.Entry(self.insert_value_child_frame)
        add_value_entry.grid(row=0, column=3)
        
        file_variable=tk.IntVar()
        file_variable_check1=tk.Radiobutton(self.insert_value_child_frame, 
                                            text="(%s) is included in file"%(self.controller.inputs['matrix_dim_unit'][-1]), 
                                            variable=file_variable,
                                            value=1).grid(row=0, column=4, sticky=tk.W)
        if self.controller.inputs['num_variables_input']>1:
            file_variable_check2=tk.Radiobutton(self.insert_value_child_frame, 
                                                text='(%s, %s) is included in file'%(self.controller.inputs['matrix_dim_unit'][-1], 
                                                                                    self.controller.inputs['matrix_dim_unit'][-2]), 
                                                variable=file_variable,
                                                value=2).grid(row=1, column=4, sticky=tk.W)  

        self.shared_func.file_format_widgets(frame=self.insert_value_child_frame, row=2, column=0)

        track_file=tk.IntVar()
        track_file_check=tk.Checkbutton(self.insert_value_child_frame, text="Would you like to track your files?", variable=track_file)
        track_file_check.grid(row=3, column=1)     

        confirm_button=ttk.Button(self.insert_value_child_frame, text="Confirm", command=lambda variable=addto_variable, 
                                                                                                  value=add_value_entry, 
                                                                                                  track_file=track_file, 
                                                                                                  file_var=file_variable,
                                                                                                  comments=self.shared_func.comments_entry, 
                                                                                                  delimiter=self.shared_func.delimiter_entry, 
                                                                                                  skiprows=self.shared_func.skiprows_entry, 
                                                                                                  use_cols=self.shared_func.usecols_entry: self.insert_value_execute(variable, 
                                                                                                                                                                     value, 
                                                                                                                                                                     track_file, 
                                                                                                                                                                     file_var, 
                                                                                                                                                                     comments, 
                                                                                                                                                                     delimiter, 
                                                                                                                                                                     skiprows, 
                                                                                                                                                                     use_cols))
        confirm_button.grid(row=3, column=0)

    def insert_value_execute(self, variable, value, track_file, file_var, comments, delimiter, skiprows, use_cols):
        """edits matrix with new value"""
        variable_index=self.controller.inputs['matrix_dim_name'].index(variable.get())
        
        #Prepares dimensions and names for uploading files and tracking files
        insertion_dimensions=self.controller.inputs['matrix_dimensions'][:] #creates copy of dimensions lengths so original doesn't get changed
        del insertion_dimensions[variable_index] #when uploading files, only care about variables not being added to
        insertion_dim_name=self.controller.inputs['matrix_dim_name'][:]
        del insertion_dim_name[variable_index]
        
        if len(insertion_dimensions)-file_var.get()>=1: #when uploading files, don't consider variables that are included in the file
            file_list_dimensions, file_list_dim_name=insertion_dimensions[:-file_var.get()], insertion_dim_name[:-file_var.get()]
        else:
            file_list_dimensions, file_list_dim_name=[1], insertion_dim_name       

        num_txt_files=1
        for i in range(len(file_list_dimensions)):
            num_txt_files*=file_list_dimensions[i] #finds the product of all the unincluded dimension lengths
        
        #upload files  
        if track_file.get()==1: #checks for whether the user would like to track their files
            self.shared_func.tracker(frame=self.insert_value_child_frame, 
                                     dimensions=file_list_dimensions, 
                                     dim_name=file_list_dim_name, 
                                     row=4, column=0)
        else: #creates file list without tracker function           
            while len(self.shared_func.file_list)<num_txt_files:
                add_file=self.shared_func.select_files(self.shared_func.folder)
                if add_file==[]: #if user cancels adding files, assumes the user would like to start everything over
                    break
                add_file.append(add_file.pop(0)) #puts the first file selected back to the beginning because tkinter is weird like that (tkinter will put the first file selected at the end)
                self.shared_func.file_list+=add_file          
        if len(self.shared_func.file_list)!=num_txt_files: #Checks to make sure the file list is the right size
            mb.showerror("Error", "File list incompatible with amount of data specified, please reconfirm inputs")
            self.shared_func.file_list=[] #resets the define variables inputs         
            print 'Do more things'
        
        #creates new submatrix based on previous inputs
        self.shared_func.create_matrix(comments=comments, 
                                       delimiter=delimiter, 
                                       skiprows=skiprows, 
                                       usecolumns=use_cols, 
                                       dimensions=insertion_dimensions, 
                                       file_list=self.shared_func.file_list)
                   
        #inserts submatrix into existing matrix based on insertion value 
        insertion_value, insertion_index=float(value.get()), 0
        for i in range(len(self.controller.inputs['matrix_dim_range'][variable_index])):
            if insertion_value>self.controller.inputs['matrix_dim_range'][variable_index][i]:
                insertion_index+=1 #seems trivial for a uniform range but allows for insertion into a custom range
            else:
                break        
        self.controller.inputs['matrix']=np.insert(self.controller.inputs['matrix'], insertion_index, self.shared_func.matrix, axis=variable_index)
        self.controller.copy['matrix']=self.controller.inputs['matrix'][:]
        
        #updates matrix parameters
        self.insert_value_update(variable_index=variable_index,
                                 insertion_index=insertion_index,
                                 insertion_value=insertion_value)
        
        self.shared_func.display_matrix(frame=self.matrix_text_frame, 
                                        text_widget=self.matrix_text, 
                                        matrix=self.controller.inputs['matrix'], 
                                        ind_var=self.controller.inputs['ind_var_input'], 
                                        ind_var_unit=self.controller.inputs['ind_var_unit_input'], 
                                        num_var=self.controller.inputs['num_variables_input'],
                                        names=self.controller.inputs['matrix_dim_name'], 
                                        units=self.controller.inputs['matrix_dim_unit'], 
                                        dimensions=self.controller.inputs['matrix_dimensions'],
                                        range_type=self.controller.inputs['matrix_range_type'], 
                                        ranges=self.controller.inputs['matrix_dim_range'])

    def insert_value_update(self, variable_index, insertion_index, insertion_value):
        """updates parameters of new matrix"""
        self.controller.inputs['matrix_dimensions'][variable_index]+=1
        self.controller.copy['matrix_dimensions']=self.controller.inputs['matrix_dimensions'][:]        
        #edits matrix range
        self.controller.inputs['matrix_dim_range'][variable_index]=list(np.insert(self.controller.inputs['matrix_dim_range'][variable_index], insertion_index, insertion_value))        
        self.controller.copy['matrix_dim_range']=self.controller.inputs['matrix_dim_range'][:]        
        #edits matrix range type
        self.controller.inputs['matrix_range_type'][variable_index]='uniform'
        uniform_step=self.controller.inputs['matrix_dim_range'][variable_index][1]-self.controller.inputs['matrix_dim_range'][variable_index][0]
        for i in range(len(self.controller.inputs['matrix_dim_range'][variable_index][:-1])):
            if self.controller.inputs['matrix_dim_range'][variable_index][i+1]-self.controller.inputs['matrix_dim_range'][variable_index][i]!=uniform_step:
                self.controller.inputs['matrix_range_type'][variable_index]='custom' #if range type is not uniform, then it must be custom
                break
        self.controller.copy['matrix_range_type']=self.controller.inputs['matrix_range_type'][:]   
        
#Fits data to common 1D and 2D functions or a custom function
class Function_Fitting(tk.Frame):
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller=controller
        self.shared_func=sf.Shared_Functions()
                
        home_button=ttk.Button(self, text='Back to Home',
                          command=lambda: self.controller.show_frame(StartPage))     
        home_button.grid(row=0, column=0, pady=20)
        
        input_button=ttk.Button(self, text="Inputs", 
                               command=lambda: self.controller.show_frame(Inputs))
        input_button.grid(row=0, column=1, pady=20)

        fun_button=ttk.Button(self, text="Matrix Fun", 
                               command=lambda: self.controller.show_frame(Matrix_Fun))
        fun_button.grid(row=0, column=2, pady=20)       
        
        edit_button=ttk.Button(self, text='Editor (Beta)',
                               command=lambda: self.controller.show_frame(Editor))
        edit_button.grid(row=0, column=3, pady=20)
        
        #Frames
        self.fitting_frame=tk.Frame(self)
        self.fitting_frame.grid(row=2, column=0, sticky=tk.N)
        self.fitting_child_frame=tk.Frame(self.fitting_frame)
        self.fitting_child_frame.grid(row=1, column=0, columnspan=3)
        
        self.function_description_frame=tk.Frame(self)
        self.function_description_frame.grid(row=3, column=0)
        self.function_description_child_frame=tk.Frame(self.function_description_frame)
        self.function_description_child_frame.pack()

        self.plot_button_frame=tk.Frame(self)
        self.plot_button_frame.grid(row=1, column=1, padx=50)
        self.plot_button_child_frame=tk.Frame(self.plot_button_frame)
        self.plot_button_child_frame.grid(row=1, column=0, columnspan=2)
        
        self.canvas_frame=tk.Frame(self)
        self.canvas_frame.grid(row=2, column=1, rowspan=2, columnspan=3, padx=50)
        self.canvas_child_frame=tk.Frame(self.canvas_frame)
        self.canvas_child_frame.pack(side=tk.TOP)               

        self.plot_opt_frame=tk.Frame(self)
        self.plot_opt_frame.grid(row=6, column=1, padx=50, sticky=tk.W)
        
        self.confirm_button=ttk.Button(self.fitting_frame, text='Confirm', command=self.fit_type)
        self.confirm_button.grid(row=0, column=1)
        
        #option menu to begin fitting
        self.dim_list=['1D', '2D']
        self.fit_dim=tk.StringVar()
        self.fit_dim.set(self.dim_list[0])
        fit_dim_option=ttk.OptionMenu(self.fitting_frame, self.fit_dim, self.dim_list[0], *self.dim_list).grid(row=0, column=0)
        
        #button to display form of common functions
        self.functions1d_button=ttk.Button(self.function_description_child_frame, text='Display common 1D functions', command=self.display_common_1d)
        self.functions1d_button.grid(row=0, column=0)
        self.functions2d_button=ttk.Button(self.function_description_child_frame, text='Display common 2D functions', command=self.display_common_2d)
        self.functions2d_button.grid(row=4, column=0)
        
        #Buttons to plot array in 1 dimensions        
        self.plot_1d_button=ttk.Button(self.plot_button_frame, text='Plot 1D', command=self.plot_1d)
        self.plot_1d_button.grid(row=0, column=0)
        self.plot_1d_button.config(state=tk.DISABLED)
        
        #Buttons to plot array in 2 dimensions
        self.plot_2d_button=ttk.Button(self.plot_button_frame, text='Plot 2D', command=self.plot_2d)
        self.plot_2d_button.grid(row=0, column=1)
        self.plot_2d_button.config(state=tk.DISABLED)
        
        #Canvas that contains the graph       
        canvas_container=tk.Canvas(self.canvas_child_frame, width=700, height=700)
        canvas_container.grid(row=0, column=0)

        hbar=ttk.Scrollbar(self.canvas_child_frame, orient=tk.HORIZONTAL)
        hbar.grid(row=1, column=0)
        vbar=ttk.Scrollbar(self.canvas_child_frame, orient=tk.VERTICAL)
        vbar.grid(row=0, column=1)
        
        hbar.config(command=canvas_container.xview)
        vbar.config(command=canvas_container.yview)
        canvas_container.config(xscrollcommand=hbar.set)
        canvas_container.config(yscrollcommand=vbar.set)       
        
        #Initial blank graph
        fig_size=(7, 7)
        f=fig.Figure(fig_size, dpi=100)        
        
        #Translating the figure as a widget
        canvas=FigureCanvasTkAgg(f, canvas_container)
        canvas_widget=canvas.get_tk_widget()
        canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        canvas_container.create_window(0, 0, window=canvas_widget)
        canvas_container.config(scrollregion=canvas_container.bbox(tk.ALL))

        self.toolbar=NavigationToolbar2Tk(canvas, self.canvas_frame)
        self.toolbar.pack(side=tk.BOTTOM)
        
        self.show_points=tk.IntVar()
        self.show_points.set(1)
        show_points_check=tk.Checkbutton(self.plot_opt_frame, text="Show Datapoints", variable=self.show_points).grid(row=0, column=0)
        
        self.connect_points=tk.IntVar()
        self.connect_points.set(1)
        connect_points_check=tk.Checkbutton(self.plot_opt_frame, text="Connect Datapoints", variable=self.connect_points).grid(row=0, column=1)  

        self.only_show_fit=tk.IntVar()
        self.only_show_fit.set(0)
        only_show_fit_check=tk.Checkbutton(self.plot_opt_frame, text="Only Show Fit", variable=self.only_show_fit).grid(row=0, column=2)
        
        #Misc. lists for plotting options
        self.marker=[None, 'o']
        self.linestyle=['None', '-']

    def reset(self):
        """resets Function Fitting frame"""
        self.fitting_child_frame.destroy()
        self.fitting_child_frame=tk.Frame(self.fitting_frame)
        self.fitting_child_frame.grid(row=1, column=0, columnspan=3)
        
        self.plot_button_child_frame.destroy()
        self.plot_button_child_frame=tk.Frame(self.plot_button_frame)
        self.plot_button_child_frame.grid(row=1, column=0, columnspan=2)

        self.confirm_button.config(state=tk.NORMAL)               
        self.plot_1d_button.config(state=tk.DISABLED)
        self.plot_2d_button.config(state=tk.DISABLED)
    
    def fit_type(self):
        """creates widgets for specifying type of fit"""
        self.confirm_button.config(state=tk.DISABLED)
        self.reset_button=ttk.Button(self.fitting_frame, text='Reset', command=self.reset)
        self.reset_button.grid(row=0, column=2)
        
        if self.fit_dim.get()=='1D':
            self.function_list=['Linear Fit', 'Exponential Fit', 'Sinusoidal Fit', 'Custom Fit']
        elif self.fit_dim.get()=='2D':
            self.function_list=['Planar Fit', 'Paraboloid Fit', 'Hyperboloid Fit', 'Custom Fit']
            
        self.fit_function=tk.StringVar()
        self.fit_function.set(self.function_list[0])
        fit_function_option = ttk.OptionMenu(self.fitting_child_frame, self.fit_function, self.function_list[0], *self.function_list).grid(row=0, column=0)
        
        self.set_param_button=ttk.Button(self.fitting_child_frame, text="Set Parameters", command=self.set_param)
        self.set_param_button.grid(row=1, column=0)
            
    def set_param(self): 
        """creates widgets to set the initial parameters for fitting using regression"""
        if self.fit_dim.get()=='1D':
            flattened_matrix=self.controller.copy['matrix'].reshape(-1, self.controller.copy['matrix_dimensions'][-1])               
        elif self.fit_dim.get()=='2D':
            flattened_matrix=self.controller.copy['matrix'].reshape(-1, self.controller.copy['matrix_dimensions'][-2], self.controller.copy['matrix_dimensions'][-1])        
        
        #Widgets for Custom Fit is different from Common Fit
        if self.fit_function.get()=="Custom Fit":
            num_param=tk.Label(self.fitting_child_frame, text="Number of Parameters").grid(row=2, column=0)
            num_param_entry=ttk.Entry(self.fitting_child_frame)
            num_param_entry.grid(row=2, column=1)
            
            confirm_button=ttk.Button(self.fitting_child_frame, text="Confirm", command=lambda matrix=flattened_matrix, num_param=num_param_entry: self.custom_fit_param(matrix, num_param))
            confirm_button.grid(row=3, column=0)
            
        else:
            a_entry=[None]*len(flattened_matrix)
            b_entry=[None]*len(flattened_matrix)
            c_entry=[None]*len(flattened_matrix)
            d_entry=[None]*len(flattened_matrix)
            if self.fit_dim.get()=='2D':
                e_entry=[None]*len(flattened_matrix)
            
            for i in range(len(flattened_matrix)):
                a_label=tk.Label(self.fitting_child_frame, text='A%d='%(i+1)).grid(row=2+i, column=0)
                a_entry[i]=ttk.Entry(self.fitting_child_frame)
                a_entry[i].grid(row=2+i, column=1)
                
                b_label=tk.Label(self.fitting_child_frame, text='B%d='%(i+1)).grid(row=2+i, column=2)
                b_entry[i]=ttk.Entry(self.fitting_child_frame)
                b_entry[i].grid(row=2+i, column=3)
                
                c_label=tk.Label(self.fitting_child_frame, text='C%d='%(i+1)).grid(row=2+i, column=4)
                c_entry[i]=ttk.Entry(self.fitting_child_frame)
                c_entry[i].grid(row=2+i, column=5)
                
                d_label=tk.Label(self.fitting_child_frame, text='D%d='%(i+1)).grid(row=2+i, column=6)
                d_entry[i]=ttk.Entry(self.fitting_child_frame)
                d_entry[i].grid(row=2+i, column=7)
                
                if self.fit_dim.get()=='2D':
                    e_label=tk.Label(self.fitting_child_frame, text='E%d='%(i+1)).grid(row=2+i, column=8)
                    e_entry[i]=ttk.Entry(self.fitting_child_frame)
                    e_entry[i].grid(row=2+i, column=9)
            
            #Different actions for Common Fit depending on whether it is a 1D or 2D fit
            if self.fit_dim.get()=='1D':
                apply_common_fit_button=ttk.Button(self.fitting_child_frame, text="Apply Common Fit", command=lambda matrix=flattened_matrix, a=a_entry, b=b_entry, c=c_entry, d=d_entry: 
                                                                                                        self.apply_common_fit(matrix, a, b, c, d))
                apply_common_fit_button.grid(row=i+3, column=0)           
            elif self.fit_dim.get()=='2D':
                apply_common_2Dfit_button=ttk.Button(self.fitting_child_frame, text='Apply Common Fit', command=lambda matrix=flattened_matrix, a=a_entry, b=b_entry, c=c_entry, d=d_entry, e=e_entry:
                                                                                                        self.apply_common_2Dfit(matrix, a, b, c, d, e))
                apply_common_2Dfit_button.grid(row=i+3, column=0)
                
    def custom_fit_param(self, matrix, num_param):
        """creates widgets to specify parameters for custom function"""
        self.param_num=int(num_param.get()) #number of parameters for the custom fit
        self.entry_list=[[None]*self.param_num]*len(matrix)          
        for i, j in itertools.product(range(len(matrix)), range(self.param_num)):
            entry_label=tk.Label(self.fitting_child_frame, text='%d-%d'%(i+1, j+1)).grid(row=i+4, column=2*j)
            self.entry_list[i][j]=ttk.Entry(self.fitting_child_frame)
            self.entry_list[i][j].grid(row=i+4, column=2*j+1)
        apply_custom_fit_button=ttk.Button(self.fitting_child_frame, text="Apply Custom Fit", command=
                                                                                            lambda matrix=matrix: self.apply_custom_fit(matrix))
        apply_custom_fit_button.grid(row=len(matrix)+4, column=0)
        
    def apply_custom_fit(self, matrix):
        """applies fit for custom function"""
        self.popt=[None]*len(matrix)
        self.pcov=[None]*len(matrix)
        
        if self.fit_dim.get()=='1D':
            self.plot_1d_button.config(state=tk.NORMAL)
            
            self.xdata=self.controller.copy['matrix_dim_range'][-1]
            for i in range(len(matrix)):
                self.popt[i], self.pcov[i]=opt.curve_fit(f=self.custom_func_wrapper, xdata=self.xdata, ydata=matrix[i], p0=[float(self.entry_list[i][j].get()) for j in range(self.param_num)])
                self.popt[i], self.pcov[i]=list(self.popt[i]), list(self.pcov[i])         

        elif self.fit_dim.get()=='2D':
            self.plot_2d_button.config(state=tk.NORMAL)   
            
            #create 2D grid for fitting function of 2 dimensions
            xgrid=[]
            for i, j in itertools.product(self.controller.copy['matrix_dim_range'][-2], self.controller.copy['matrix_dim_range'][-1]):
                xgrid+=[[i, j]]
            xgrid=np.array(xgrid)
            
            self.xdata=xgrid
            for i in range(len(matrix)):
                self.popt[i], self.pcov[i]=opt.curve_fit(f=self.custom_func_wrapper, xdata=self.xdata, ydata=matrix[i].flatten(), p0=[float(self.entry_list[i][j].get()) for j in range(self.param_num)])
                self.popt[i], self.pcov[i]=list(self.popt[i]), list(self.pcov[i])
            
        show_button=ttk.Button(self.fitting_child_frame, text="Show Results", command=lambda matrix=matrix: self.show_results(matrix))
        show_button.grid(row=len(matrix)+5, column=0)
    
    def custom_func_wrapper(self, *args):
        """wrapper for custom_func due to unknown number of parameters"""
        return self.custom_func(args[0], args[1:])    
    
    def custom_func(self, x, p):
        """imports custom function defined in custom.py"""
        import custom as cstm
        y=cstm.custom_fit(x, p)
        del sys.modules['custom']
        return y
   
    def apply_common_fit(self, matrix, a, b, c, d):
        """applies fit for common functions of one dimension"""
        self.popt=[None]*len(matrix)
        self.pcov=[None]*len(matrix)
        
        self.xdata=self.controller.copy['matrix_dim_range'][-1]
        for i in range(len(matrix)):
            self.popt[i], self.pcov[i]=opt.curve_fit(f=self.common_func, xdata=self.xdata, ydata=matrix[i], p0=[float(a[i].get()) if a[i].get()!='' else 1, 
                                                                                                                float(b[i].get()) if b[i].get()!='' else 1, 
                                                                                                                float(c[i].get()) if c[i].get()!='' else 1, 
                                                                                                                float(d[i].get()) if d[i].get()!='' else 1])
            self.popt[i], self.pcov[i]=list(self.popt[i]), list(self.pcov[i])

        self.plot_1d_button.config(state=tk.NORMAL)               
        show_button=ttk.Button(self.fitting_child_frame, text="Show Results", command=lambda matrix=matrix: self.show_results(matrix))
        show_button.grid(row=len(matrix)+3, column=0)
    
    def common_func(self, x, a, b, c, d):
        """common functions of 1 dimensions chosen using self.fit_function"""
        if self.fit_function.get()=="Linear Fit":
            return a*np.array(x)+b
        elif self.fit_function.get()=="Exponential Fit":
            return a*(np.exp(b*np.array(x)+c))+d
        elif self.fit_function.get()=="Sinusoidal Fit":
            return a*(np.sin(b*np.array(x)+c))+d    
    
    def apply_common_2Dfit(self, matrix, a, b, c, d, e):
        """applies fit for common functions of two dimensions"""
        self.popt=[None]*len(matrix)
        self.pcov=[None]*len(matrix)
        
        #create 2D grid for fitting function of 2 dimensions
        xgrid=[]
        for i, j in itertools.product(self.controller.copy['matrix_dim_range'][-2], self.controller.copy['matrix_dim_range'][-1]):
            xgrid+=[[i, j]]
        xgrid=np.array(xgrid)
            
        self.xdata=xgrid
        for i in range(len(matrix)):
            self.popt[i], self.pcov[i]=opt.curve_fit(f=self.common_2Dfunc, xdata=self.xdata, ydata=matrix[i].flatten(), p0=[float(a[i].get()) if a[i].get()!='' else 1, 
                                                                                                                            float(b[i].get()) if b[i].get()!='' else 1, 
                                                                                                                            float(c[i].get()) if c[i].get()!='' else 1, 
                                                                                                                            float(d[i].get()) if d[i].get()!='' else 1, 
                                                                                                                            float(e[i].get()) if e[i].get()!='' else 1])
            self.popt[i], self.pcov[i]=list(self.popt[i]), list(self.pcov[i])
        
        self.plot_2d_button.config(state=tk.NORMAL)        
        show_button=ttk.Button(self.fitting_child_frame, text="Show Results", command=lambda matrix=matrix: self.show_results(matrix))
        show_button.grid(row=len(matrix)+3, column=0) 
    
    def common_2Dfunc(self, x, a, b, c, d, e):
        """common functions of 2 dimensions; chosen using self.fit_function"""
        if self.fit_function.get()=='Planar Fit':
            return a*x[:, 0]+b*x[:, 1]+c
        elif self.fit_function.get()=='Paraboloid Fit':
            return a*(x[:,0]+b)**2+c*(x[:,1]+d)**2+e
        elif self.fit_function.get()=='Hyperboloid Fit':
            return np.sqrt(a*(x[:,0]+b)**2+c*(x[:,1]+d)**2)+e
   
    def show_results(self, matrix):
        """show results of fit and goodness of fit in new window"""
        results_window=tk.Toplevel(self)
        
        #frames for new window
        results_frame=tk.Frame(results_window)
        results_frame.pack()
        stat_frame=tk.Frame(results_window)
        stat_frame.pack()

        #shape matrix differently for 2D fit        
        if self.fit_dim.get()=='2D':
            matrix=matrix.reshape((len(matrix), self.controller.copy['matrix_dimensions'][-2]*self.controller.copy['matrix_dimensions'][-1]))
        
        #show results of fit
        fit_error=[None]*len(matrix)        
        if self.fit_function.get()=="Custom Fit":
            for i in range(len(matrix)):
                for j in range(self.param_num):
                    results=tk.Label(results_frame, text="%d-%d=%.3E,"%(i+1, j+1, self.popt[i][j])).grid(row=i, column=j)
                fit_error[i]=matrix[i]-self.custom_func(self.xdata, self.popt[i])
        else:
            for i in range(len(matrix)):
                a_results=tk.Label(results_frame, text="A%d=%.3E,"%(i+1, self.popt[i][0])).grid(row=i, column=0)
                b_results=tk.Label(results_frame, text="B%d=%.3E,"%(i+1, self.popt[i][1])).grid(row=i, column=1)
                c_results=tk.Label(results_frame, text="C%d=%.3E,"%(i+1, self.popt[i][2])).grid(row=i, column=2)
                d_results=tk.Label(results_frame, text="D%d=%.3E,"%(i+1, self.popt[i][3])).grid(row=i, column=3)
                if self.fit_dim.get()== '1D':
                    fit_error[i]=matrix[i]-self.common_func(self.xdata, self.popt[i][0], self.popt[i][1], self.popt[i][2], self.popt[i][3])                                
                elif self.fit_dim.get()=='2D':
                    e_results=tk.Label(results_frame, text="E%d=%.3E,"%(i+1, self.popt[i][4])).grid(row=i, column=4)              
                    fit_error[i]=matrix[i]-self.common_2Dfunc(self.xdata, self.popt[i][0], self.popt[i][1], self.popt[i][2], self.popt[i][3], self.popt[i][4])
        
        #show measurements for goodness of fit
        for i in range(len(matrix)):
            abs_max_error=tk.Label(stat_frame, text="%d. Max Absolute Error=%.3E,"%(i+1, np.max(np.abs(fit_error[i])))).grid(row=0, column=i, sticky=tk.W)            
            
            abs_mean_error=tk.Label(stat_frame, text="%d. Mean Absolute Error=%.3E,"%(i+1, np.mean(np.abs(fit_error[i])))).grid(row=1, column=i, sticky=tk.W)            
            
            mean_error=tk.Label(stat_frame, text="%d. Mean Error=%.3E,"%(i+1, np.mean(fit_error[i]))).grid(row=2, column=i, sticky=tk.W)            
            
            std=tk.Label(stat_frame, text="%d. Std Deviation=%.3E,"%(i+1, np.sqrt(np.sum(fit_error[i]**2)/(len(fit_error[i])-1)))).grid(row=3, column=i, sticky=tk.W)         
            
            r_squared=tk.Label(stat_frame, text="%d. R squared=%.3E"%(i+1, 1-(np.sum(fit_error[i]**2)/np.sum((matrix[i]-matrix[i].mean())**2)))).grid(row=4, column=i, sticky=tk.W)

    def display_common_1d(self):
        """displays form of common 1D functions"""
        linear_label=tk.Label(self.function_description_child_frame, text='Linear Fit: y=Ax+B').grid(row=1, column=0)
        exponential_label=tk.Label(self.function_description_child_frame, text='Exponential Fit: y=Ae^(Bx+C)+D').grid(row=2, column=0)
        sinusoidal_label=tk.Label(self.function_description_child_frame, text='Sinusoidal Fit: y=Asin(Bx+C)+D').grid(row=3, column=0)
        
    def display_common_2d(self):
        """displays form of common 2D functions"""
        planar_label=tk.Label(self.function_description_child_frame, text='Planar Fit: z=Ax+By+C').grid(row=5, column=0)
        paraboloid_label=tk.Label(self.function_description_child_frame, text='Paraboloid Fit: z=A(x+B)^2 + C(y+D)^2 + E').grid(row=6, column=0)
        hyperboloid_label=tk.Label(self.function_description_child_frame, text='Hyperboloid Fit: z=[A(x+B)^2 + C(x+D)^2]^(1/2) + E').grid(row=7, column=0)
        
    def plot_1d(self):
        """creates widgets for plotting matrix in 1D"""
        self.plot_button_child_frame.destroy()
        self.plot_button_child_frame=tk.Frame(self.plot_button_frame)
        self.plot_button_child_frame.grid(row=1, column=0, columnspan=2)        
        #Plot One in All button
        plot_1d_oneinall_button=ttk.Button(self.plot_button_child_frame, text='Plot One in All', command=self.plot_1d_oneinall)
        plot_1d_oneinall_button.grid(row=0, column=0)
        #Plot Multiple button
        plot_1d_multiple_button=ttk.Button(self.plot_button_child_frame, text='Plot Multiple', command=self.plot_1d_multiple)
        plot_1d_multiple_button.grid(row=0, column=1)
        #Plot All in One button
        plot_1d_allinone_button=ttk.Button(self.plot_button_child_frame, text='Plot All in One', command=self.plot_1d_allinone)
        plot_1d_allinone_button.grid(row=0, column=2)
    
    def plot_1d_oneinall(self):
        """plot raw data and fit in single 1D graphs"""
        self.canvas_child_frame.destroy()
        self.toolbar.destroy()
        
        self.canvas_child_frame=tk.Frame(self.canvas_frame)
        self.canvas_child_frame.pack()
    
        simulated_dimensions=self.shared_func.simulated_dim(self.controller.copy['matrix_dimensions'])
        if len(self.controller.copy['matrix_dimensions'])>1:    
            #formatting the plots
            self.shared_func.plot_oneinall_format(dimensions=self.controller.copy['matrix_dimensions'], 
                                                  ranges=self.controller.copy['matrix_dim_range'],
                                                    names=self.controller.copy['matrix_dim_name'],
                                                    units=self.controller.copy['matrix_dim_unit'],
                                                    ind_var=self.controller.copy['ind_var_input'],
                                                    ind_var_unit=self.controller.copy['ind_var_unit_input'])
            
            #plot data
            for i, j in itertools.product(range(simulated_dimensions[-1]/simulated_dimensions[1]), 
                                          range(self.controller.copy['matrix_dimensions'][-2])): 
                if len(self.controller.copy['matrix_dimensions'])==2:
                    if self.only_show_fit.get()==0: #plot raw data
                        self.shared_func.ax[j].plot(self.xdata, 
                                                    self.controller.copy['matrix'].reshape(-1, self.controller.copy['matrix_dimensions'][-1])[j], 
                                                    linestyle=self.linestyle[self.connect_points.get()], 
                                                    marker=self.marker[self.show_points.get()], 
                                                    label=self.shared_func.plot_labels[i][j])
                    if self.fit_function.get()=='Custom Fit':
                        self.shared_func.ax[j].plot(self.xdata, self.custom_func(self.xdata, self.popt[j]), label='%s fit'%(self.shared_func.plot_labels[i][j]))
                    elif self.fit_function.get()!='Custom Fit':
                        self.shared_func.ax[j].plot(self.xdata, 
                                                    self.common_func(self.xdata, 
                                                                     self.popt[j][0], 
                                                                        self.popt[j][1], 
                                                                        self.popt[j][2], 
                                                                        self.popt[j][3]), 
                                                    label='%s fit'%(self.shared_func.plot_labels[i][j]))
                    self.shared_func.ax[j].legend()
            
                else:
                    if self.only_show_fit.get()==0: #plot raw data
                        self.shared_func.ax[i, j].plot(self.xdata, 
                                                    self.controller.copy['matrix'].reshape(-1, self.controller.copy['matrix_dimensions'][-1])[i*self.controller.copy['matrix_dimensions'][-2]+j], 
                                                    linestyle=self.linestyle[self.connect_points.get()], 
                                                    marker=self.marker[self.show_points.get()], 
                                                    label=self.shared_func.plot_labels[i][j])
                    if self.fit_function.get()=='Custom Fit':
                        self.shared_func.ax[i, j].plot(self.xdata, self.custom_func(self.xdata, self.popt[i*self.controller.copy['matrix_dimensions'][-2]+j]), label='%s fit'%(self.shared_func.plot_labels[i][j]))                            
                    elif self.fit_function.get()!='Custom Fit':
                        self.shared_func.ax[i, j].plot(self.xdata, 
                                                        self.common_func(self.xdata, 
                                                                         self.popt[i*self.controller.copy['matrix_dimensions'][-2]+j][0], 
                                                                            self.popt[i*self.controller.copy['matrix_dimensions'][-2]+j][1], 
                                                                            self.popt[i*self.controller.copy['matrix_dimensions'][-2]+j][2], 
                                                                            self.popt[i*self.controller.copy['matrix_dimensions'][-2]+j][3]), 
                                                        label='%s fit'%(self.shared_func.plot_labels[i][j]))                        
                    self.shared_func.ax[i, j].legend() 
                
        else:
            self.shared_func.invalid_plot()
        
        self.embed_graph(fig=self.shared_func.f, width=self.shared_func.graph_width, height=self.shared_func.graph_height)

    def plot_1d_multiple(self):
        """plots raw data and fit as series of lines in a series of plots"""
        self.canvas_child_frame.destroy()
        self.toolbar.destroy()
        
        self.canvas_child_frame=tk.Frame(self.canvas_frame)
        self.canvas_child_frame.pack()
               
        simulated_dimensions=self.shared_func.simulated_dim(self.controller.copy['matrix_dimensions'])       
        if len(self.controller.copy['matrix_dimensions'])>2:
            #formatting the plots
            self.shared_func.plot_multiple_format(dimensions=self.controller.copy['matrix_dimensions'], 
                                                  ranges=self.controller.copy['matrix_dim_range'],
                                                    names=self.controller.copy['matrix_dim_name'],
                                                    units=self.controller.copy['matrix_dim_unit'],
                                                    ind_var=self.controller.copy['ind_var_input'],
                                                    ind_var_unit=self.controller.copy['ind_var_unit_input'])     
                                                    
            for i, j in itertools.product(range(simulated_dimensions[-1]/simulated_dimensions[2]), 
                                          range(self.controller.copy['matrix_dimensions'][-3])):
                if len(self.controller.copy['matrix_dimensions'])==3:
                    for k in range(self.controller.copy['matrix_dimensions'][-2]):
                        if self.only_show_fit.get()==0: #plot raw data
                            self.shared_func.ax[j].plot(self.xdata,
                                                        self.controller.copy['matrix'].reshape(-1, self.controller.copy['matrix_dimensions'][-1])[j*self.controller.copy['matrix_dimensions'][-2]+k], #to obtain the correct value for the index of a series of 1D lines, 
                                                                                                                                                                                                    #multiply the value of the current iterator by the length of all its subsequent iterators
                                                        linestyle=self.linestyle[self.connect_points.get()], 
                                                        marker=self.marker[self.show_points.get()], 
                                                        label='%f%s'%(self.controller.copy['matrix_dim_range'][-2][k], 
                                                                      self.controller.copy['matrix_dim_unit'][-2]))
                        
                        if self.fit_function.get()=='Custom Fit':
                            self.shared_func.ax[j].plot(self.xdata, 
                                                        self.custom_func(self.xdata, 
                                                                         self.popt[j*self.controller.copy['matrix_dimensions'][-2]+k]), 
                                                        label='%f%s fit'%(self.controller.copy['matrix_dim_range'][-2][k], 
                                                                          self.controller.copy['matrix_dim_unit'][-2]))                                
                        elif self.fit_function.get()!='Custom Fit':
                            self.shared_func.ax[j].plot(self.xdata, 
                                                        self.common_func(self.xdata, 
                                                                         self.popt[j*self.controller.copy['matrix_dimensions'][-2]+k][0], 
                                                                            self.popt[j*self.controller.copy['matrix_dimensions'][-2]+k][1], 
                                                                            self.popt[j*self.controller.copy['matrix_dimensions'][-2]+k][2], 
                                                                            self.popt[j*self.controller.copy['matrix_dimensions'][-2]+k][3]), 
                                                        label='%f%s fit'%(self.controller.copy['matrix_dim_range'][-2][k], 
                                                                          self.controller.copy['matrix_dim_unit'][-2]))                        
                    self.shared_func.ax[j].legend()                
                
                else:
                    for k in range(self.controller.copy['matrix_dimensions'][-2]):
                        if self.only_show_fit.get()==0: #plot raw data
                            self.shared_func.ax[i, j].plot(self.xdata,
                                                            self.controller.copy['matrix'].reshape(-1, self.controller.copy['matrix_dimensions'][-1])[i*self.controller.copy['matrix_dimensions'][-3]*self.controller.copy['matrix_dimensions'][-2]+
                                                                                                                                                        j*self.controller.copy['matrix_dimensions'][-2]+
                                                                                                                                                        k], #to obtain the correct value for the index of a series of 1D lines, 
                                                                                                                                                        #multiply the value of the current iterator by the length of all its subsequent iterators  
                                                            linestyle=self.linestyle[self.connect_points.get()], 
                                                            marker=self.marker[self.show_points.get()], 
                                                            label='%f%s'%(self.controller.copy['matrix_dim_range'][-2][k], 
                                                                          self.controller.copy['matrix_dim_unit'][-2]))
                        if self.fit_function.get()=='Custom Fit':
                            self.shared_func.ax[i, j].plot(self.xdata, 
                                                            self.custom_func(self.xdata, 
                                                                             self.popt[i*self.controller.copy['matrix_dimensions'][-3]*self.controller.copy['matrix_dimensions'][-2]+
                                                                                         j*self.controller.copy['matrix_dimensions'][-2]+
                                                                                         k]), 
                                                                                label='%f%s fit'%(self.controller.copy['matrix_dim_range'][-2][k], 
                                                                                                  self.controller.copy['matrix_dim_unit'][-2]))                               
                        elif self.fit_function.get()!='Custom Fit':
                            self.shared_func.ax[i, j].plot(self.xdata, 
                                                            self.common_func(self.xdata, 
                                                                             self.popt[i*self.controller.copy['matrix_dimensions'][-3]*self.controller.copy['matrix_dimensions'][-2]+
                                                                                         j*self.controller.copy['matrix_dimensions'][-2]+
                                                                                         k][0], 
                                                                                self.popt[i*self.controller.copy['matrix_dimensions'][-3]*self.controller.copy['matrix_dimensions'][-2]+
                                                                                            j*self.controller.copy['matrix_dimensions'][-2]+
                                                                                            k][1], 
                                                                                self.popt[i*self.controller.copy['matrix_dimensions'][-3]*self.controller.copy['matrix_dimensions'][-2]+
                                                                                            j*self.controller.copy['matrix_dimensions'][-2]+
                                                                                            k][2], 
                                                                                self.popt[i*self.controller.copy['matrix_dimensions'][-3]*self.controller.copy['matrix_dimensions'][-2]+
                                                                                            j*self.controller.copy['matrix_dimensions'][-2]+
                                                                                            k][3]), 
                                                            label='%f%s fit'%(self.controller.copy['matrix_dim_range'][-2][k], 
                                                                              self.controller.copy['matrix_dim_unit'][-2]))                      
                    self.shared_func.ax[i, j].legend()

                        
        else:
            self.shared_func.invalid_plot() 
        
        self.embed_graph(fig=self.shared_func.f, width=self.shared_func.graph_width, height=self.shared_func.graph_height)          

    def plot_1d_allinone(self):
        """plots raw data and fit in one plot as series of lines"""
        self.canvas_child_frame.destroy()
        self.toolbar.destroy()
        
        self.canvas_child_frame=tk.Frame(self.canvas_frame)
        self.canvas_child_frame.pack()

        simulated_dimensions=self.shared_func.simulated_dim(self.controller.copy['matrix_dimensions'])

        #formatting the plot
        self.shared_func.plot_allinone_format(dimensions=self.controller.copy['matrix_dimensions'], 
                                                  ranges=self.controller.copy['matrix_dim_range'],
                                                    names=self.controller.copy['matrix_dim_name'],
                                                    units=self.controller.copy['matrix_dim_unit'],
                                                    ind_var=self.controller.copy['ind_var_input'],
                                                    ind_var_unit=self.controller.copy['ind_var_unit_input'])       
        for i in range(simulated_dimensions[-1]/simulated_dimensions[0]):
            if self.only_show_fit.get()==0: #plot raw data
                self.shared_func.ax.plot(self.xdata, 
                                         self.controller.copy['matrix'].reshape(-1, self.controller.copy['matrix_dimensions'][-1])[i], 
                                            linestyle=self.linestyle[self.connect_points.get()], 
                                            marker=self.marker[self.show_points.get()], 
                                            label=self.shared_func.plot_labels[i])            
            if self.fit_function.get()=='Custom Fit':
                self.shared_func.ax.plot(self.xdata, self.custom_func(self.xdata, self.popt[i]), label='%s fit'%(self.shared_func.plot_labels[i]))                
            elif self.fit_function.get()!='Custom Fit':
                self.shared_func.ax.plot(self.xdata, 
                                         self.common_func(self.xdata, 
                                                          self.popt[i][0], 
                                                            self.popt[i][1], 
                                                            self.popt[i][2], 
                                                            self.popt[i][3]), 
                                            label='%s fit'%(self.shared_func.plot_labels[i]))        
        self.shared_func.ax.legend()

        self.embed_graph(fig=self.shared_func.f, width=self.shared_func.graph_width, height=self.shared_func.graph_height)
        
    def plot_2d(self):
        """creates widgets for plotting matrix in 2D"""
        self.plot_button_child_frame.destroy()
        self.plot_button_child_frame=tk.Frame(self.plot_button_frame)
        self.plot_button_child_frame.grid(row=1, column=0, columnspan=2)
        #Plot 2D wireframe button
        d2_wireframe_button=ttk.Button(self.plot_button_child_frame, text='2D Wireframe', command=self.plot_2d_wireframe)
        d2_wireframe_button.grid(row=0, column=0)        

    def plot_2d_wireframe(self):
        """plots 2d wireframe plots for raw data and fit"""
        self.canvas_child_frame.destroy()
        self.toolbar.destroy()
        
        self.canvas_child_frame=tk.Frame(self.canvas_frame)
        self.canvas_child_frame.pack()
        
        simulated_dimensions=self.shared_func.simulated_dim(self.controller.copy['matrix_dimensions'])
        x, y=np.meshgrid(self.controller.copy['matrix_dim_range'][-1], self.controller.copy['matrix_dim_range'][-2])
        
        #multiple 2d plots
        if len(self.controller.copy['matrix_dimensions'])>2:            
            #formatting the plot
            self.shared_func.plot_multiplesurface_format(dimensions=self.controller.copy['matrix_dimensions'], 
                                                          ranges=self.controller.copy['matrix_dim_range'],
                                                            names=self.controller.copy['matrix_dim_name'],
                                                            units=self.controller.copy['matrix_dim_unit'],
                                                            ind_var=self.controller.copy['ind_var_input'],
                                                            ind_var_unit=self.controller.copy['ind_var_unit_input'])
            #reshapes matrix into array of 2d arrays
            flattened_matrix=self.controller.copy['matrix'].reshape(-1, 
                                                                    self.controller.copy['matrix_dimensions'][-2], 
                                                                    self.controller.copy['matrix_dimensions'][-1])            
            #begin plotting
            for i, j in itertools.product(range(simulated_dimensions[-1]/simulated_dimensions[2]), 
                                          range(self.controller.copy['matrix_dimensions'][-3])):
                if self.only_show_fit.get()==0: #plot raw data
                    self.shared_func.ax[i][j].plot_wireframe(x, y, flattened_matrix[i*self.controller.copy['matrix_dimensions'][-3]+j], rstride=1, cstride=1, label='data')                                           
                if self.fit_function.get()=='Custom Fit':
                    self.shared_func.ax[i][j].plot_wireframe(x, 
                                                            y, 
                                                            self.custom_func(self.xdata, 
                                                                             self.popt[i*self.controller.copy['matrix_dimensions'][-3]+j]).reshape((self.controller.copy['matrix_dimensions'][-2], 
                                                                                                                                                    self.controller.copy['matrix_dimensions'][-1])), 
                                                            color='green', 
                                                            label='fit')                    
                elif self.fit_function.get()!='Custom Fit':
                    self.shared_func.ax[i][j].plot_wireframe(x, 
                                                             y, 
                                                             self.common_2Dfunc(self.xdata, 
                                                                                self.popt[i*self.controller.copy['matrix_dimensions'][-3]+j][0], 
                                                                                self.popt[i*self.controller.copy['matrix_dimensions'][-3]+j][1],
                                                                                self.popt[i*self.controller.copy['matrix_dimensions'][-3]+j][2], 
                                                                                self.popt[i*self.controller.copy['matrix_dimensions'][-3]+j][3], 
                                                                                self.popt[i*self.controller.copy['matrix_dimensions'][-3]+j][4]).reshape((self.controller.copy['matrix_dimensions'][-2], 
                                                                                                                                                            self.controller.copy['matrix_dimensions'][-1])), 
                                                            color='green', 
                                                            label='fit')
                self.shared_func.ax[i][j].legend()
        
        #single 2d plot
        elif len(self.controller.copy['matrix_dimensions'])==2:
            #formatting the plot
            self.shared_func.plot_singlesurface_format(names=self.controller.copy['matrix_dim_name'],
                                                       units=self.controller.copy['matrix_dim_unit'],
                                                        ind_var=self.controller.copy['ind_var_input'],
                                                        ind_var_unit=self.controller.copy['ind_var_unit_input'])
            #begin plotting
            if self.only_show_fit.get()==0: #plot raw data
                self.shared_func.ax.plot_wireframe(x, y, self.controller.copy['matrix'], rstride=1, cstride=1, label='data')
            if self.fit_function.get()=='Custom Fit':
                self.shared_func.ax.plot_wireframe(x, 
                                                   y, 
                                                   self.custom_func(self.xdata, self.popt).reshape((self.controller.copy['matrix_dimensions'][-2], 
                                                                                                    self.controller.copy['matrix_dimensions'][-1])), 
                                                    color='green', 
                                                    label='fit')               
            elif self.fit_function.get()!='Custom Fit':
                self.shared_func.ax.plot_wireframe(x, 
                                                   y, 
                                                   self.common_2Dfunc(self.xdata, 
                                                                      self.popt[0][0], 
                                                                        self.popt[0][1], 
                                                                        self.popt[0][2], 
                                                                        self.popt[0][3], 
                                                                        self.popt[0][4]).reshape((self.controller.copy['matrix_dimensions'][-2], 
                                                                                                    self.controller.copy['matrix_dimensions'][-1])), 
                                                  color='green', 
                                                  label='fit')
            self.shared_func.ax.legend()
                     
        else: 
            self.shared_func.invalid_plot()        
        
        self.embed_graph(fig=self.shared_func.f, width=self.shared_func.graph_width, height=self.shared_func.graph_height)
        
    def embed_graph(self, fig, width, height): 
        """embeds graph in Function_Fitting page"""
        canvas_width=width*100
        canvas_height=height*100
        if canvas_width>900:
            canvas_width=900
        if canvas_height>800:
            canvas_height=800
            
        #canvas that contains the graph
        canvas_container=tk.Canvas(self.canvas_child_frame, width=canvas_width, height=canvas_height)
        canvas_container.grid(row=0, column=0)        
        hbar=ttk.Scrollbar(self.canvas_child_frame, orient=tk.HORIZONTAL)
        hbar.grid(row=1, column=0)            
        vbar=ttk.Scrollbar(self.canvas_child_frame, orient=tk.VERTICAL)
        vbar.grid(row=0, column=1)
                
        hbar.config(command=canvas_container.xview)
        vbar.config(command=canvas_container.yview)
        canvas_container.config(xscrollcommand=hbar.set)
        canvas_container.config(yscrollcommand=vbar.set)
        
        #translating the figure as a widget
        canvas=FigureCanvasTkAgg(fig, canvas_container)
        canvas_widget=canvas.get_tk_widget()
        canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)                
        canvas_container.create_window(0, 0, window=canvas_widget)
        canvas_container.config(scrollregion=canvas_container.bbox(tk.ALL))
                
        self.toolbar=NavigationToolbar2Tk(canvas, self.canvas_frame)
        self.toolbar.pack(side=tk.BOTTOM) 


#Execute application    
app=Data_Analysis()
app.mainloop()