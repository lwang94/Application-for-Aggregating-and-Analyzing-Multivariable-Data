# -*- coding: utf-8 -*-
"""
Created on Thu Oct 18 13:42:37 2018

@author: lawre
"""

import numpy as np
import matplotlib.figure as fig

import Tkinter as tk
import ttk
import tkFileDialog as fd
import tkMessageBox as mb
import os
import itertools

from mpl_toolkits.mplot3d import Axes3D

#Object containing functions that are shared between multiple pages
class Shared_Functions():
    def __init__(self):
        self.variable_range=None
        self.range_type=None
        self.file_list=[]
        self.matrix=[]
        
        self.comments_entry=None
        self.delimiter_entry=None
        self.skiprows_entry=None
        self.usecols_entry=None
        
        self.save_button=None
        self.folder=''
        
        self.f=None
        self.ax=None
        self.graph_width=None
        self.graph_height=None
        self.plot_labels=None
        
    def reset(self):
        """resets variables within class"""
        self.variable_range=None
        self.range_type=None
        self.file_list=[]
        self.matrix=[]
        
        self.comments_entry=None
        self.delimiter_entry=None
        self.skiprows_entry=None
        self.usecols_entry=None   
        
        self.save_button=None
        self.folder=''
        
        self.f=None
        self.ax=None
        self.graph_width=None
        self.graph_height=None
        self.plot_labels=None
    
    def select_files(self, directory):
        """selects multiple files from the directory"""
        filenames_loc=fd.askopenfilenames(initialdir=directory, title='Select files', filetypes=(('text files', '*.txt'), ('all files', '*.*')))
        filenames_loc=list(filenames_loc)
        
        if len(filenames_loc)>0: #prevents error from ocurring if user doesn't actually select any files
            self.folder=os.path.dirname(filenames_loc[0]) #remembers last used directory
        
        return filenames_loc  
    
    def simulated_dim(self, dimensions):
        """returns list that simulates the size of the matrix with each increase in dimension/variable"""
        sim_dim=[1]
        for j in range(len(dimensions), 0, -1):
            sim_dim+=[dimensions[j-1]*sim_dim[-1]]
        return sim_dim[1:]
        
    def build_uniform_range(self, frame, row, column, uniform_button, custom_button, variable_range_input=None, columnspan=1):
        """creates widgets to generate axes of uniformly spaced values"""
        uniform_array_label=tk.Label(frame, 
                                     text="Please specify uniform range as START, STOP, NUM DATAPOINTS").grid(row=row, column=column, columnspan=columnspan)
        
        self.variable_range=ttk.Entry(frame)
        if variable_range_input!=None: #for when matrix is loaded into application
            self.variable_range.insert(tk.END, '%f, %f, %f'%(variable_range_input[0], variable_range_input[-1], len(variable_range_input)))
        self.variable_range.grid(row=row, column=column+columnspan)
        
        self.range_type='uniform'
        uniform_button.config(state=tk.DISABLED)
        custom_button.config(state=tk.DISABLED)
        
    def build_custom_range(self, frame, row, column, uniform_button, custom_button, variable_range_input=None, columnspan=1):
        """creates widgets to generate axes based on custom values inputted by user"""
        custom_array_label=tk.Label(frame, 
                                    text='Please specify custom range').grid(row=row, column=column, columnspan=columnspan)
        
        self.variable_range=ttk.Entry(frame)
        if variable_range_input!=None: #for when matrix is loaded into application
            entry_input=''.join('%f,'%(i) for i in variable_range_input)
            self.variable_range.insert(tk.END, entry_input)
        self.variable_range.grid(row=row, column=column+columnspan)
        
        self.range_type='custom'
        uniform_button.config(state=tk.DISABLED)
        custom_button.config(state=tk.DISABLED)       
    
    def tracker(self, frame, dimensions, dim_name, row, column):    
        """creates widgets to track files when creating matrix"""
        matrix_label='Dimensions='+''.join('%sx'%(i) for i in dim_name)[:-1]
        tracker_title=tk.Label(frame, text=matrix_label).grid(row=row, column=column)
        
        #variables to use in the rest of the function
        simulated_dimensions=self.simulated_dim(dimensions)
        tracker_variable_label=[]
        for i in range(len(dimensions), 0, -1): #counts backwards
            tracker_variable_label+=[dim_name[i-1]]                
        variable_counter=[0]*(len(simulated_dimensions)+1) #every variable starts at 0
       
        while len(self.file_list)<simulated_dimensions[-1]:
            add_file=self.select_files(directory=self.folder)
            if add_file==[]: #if the user cancels inputting files, assumes the user would like to start over completely
                break
            add_file.append(add_file.pop(0))
            self.file_list+=add_file 
            
            for i in range(len(dimensions)):
                #This section ensures user does not exceed indicated dimensions
                floor_division_list=[(len(self.file_list)-len(add_file))//simulated_dimensions[i],
                                     len(self.file_list)//simulated_dimensions[i]]
                if floor_division_list[0]!=floor_division_list[1] and len(self.file_list)%simulated_dimensions[i]!=0:
                    file_length_warning=mb.askyesno("Warning", "File length has exceeded the indicated dimension for %s. Would you like to continue?"%(tracker_variable_label[i]))
                    if file_length_warning==False:
                        self.file_list=[] #resets file_list
                        mb.showinfo("Reset", "Your file list has been reset")
                
                #This section generates counter for keeping track of files
                if len(self.file_list)%simulated_dimensions[i]==0:
                    variable_counter[i]=0
                    variable_counter[i+1]+=1
                else:
                    variable_counter[0]=len(self.file_list)%simulated_dimensions[0]
                
                #This section generates widgets displaying tracker
                if variable_counter[0:i+1]==[0]*(i+1) and variable_counter[i+1]!=0:
                    counter_label=tk.Label(frame, text='%s=FULL'%(tracker_variable_label[i])).grid(row=row+i+1, column=column)
                else:
                    counter_label=tk.Label(frame, text='%s= %s'%(tracker_variable_label[i], 
                                                                 str(variable_counter[i]).zfill(3))).grid(row=row+i+1, column=column)
    
    def create_matrix(self, comments, delimiter, skiprows, usecolumns, dimensions, file_list):
       """creates matrix based on .txt files and user inputs""" 
       use_columns=usecolumns.get().split(',')
       use_cols=[]
       for i in range(len(use_columns)):
           if '-' in use_columns[i]:
               column_range=[int(j) for j in use_columns[i].split('-')]
               use_cols+=range(column_range[0]-1, column_range[1]) 
           else:
               use_cols+=[int(use_columns[i])-1]

       #Creates a one-dimensional array that will be later converted to a matrix of n-dimensions using np.reshape
       unshaped_matrix=[]
       for i in range(len(file_list)):
           if len(use_cols)==1:
               data=np.loadtxt(file_list[i], comments=comments.get(), delimiter=delimiter.get(), skiprows=int(skiprows.get()), usecols=tuple(use_cols*2), unpack=True)
               data=list(data[0])
           else:
               data=np.loadtxt(file_list[i], comments=comments.get(), delimiter=delimiter.get(), skiprows=int(skiprows.get()), usecols=tuple(use_cols)) #NOTE: does not unpack in order to keep the rowxcolumn dimension the same
               data=data.tolist()
           unshaped_matrix+=data    
        
       self.matrix=np.array(unshaped_matrix).reshape(tuple(dimensions)) #shapes matrix

    def display_matrix(self, frame, text_widget, matrix, ind_var, ind_var_unit, num_var, names, units, dimensions, range_type, ranges):      
       """displays matrix in text widget and creates save matrix button"""
       text_widget.insert(tk.END, matrix)
       
       self.save_button=ttk.Button(frame, text='Save Matrix', command=
                                                         lambda matrix=matrix, 
                                                         ind_var=ind_var, 
                                                         ind_var_unit=ind_var_unit, 
                                                         num_var=num_var, 
                                                         names=names, 
                                                         units=units, 
                                                         dimensions=dimensions, 
                                                         range_type=range_type, 
                                                         ranges=ranges:
                                                         self.save_matrix(matrix, 
                                                                          ind_var, 
                                                                          ind_var_unit, 
                                                                          num_var, 
                                                                          names, 
                                                                          units, 
                                                                          dimensions, 
                                                                          range_type, 
                                                                          ranges))
       self.save_button.pack(side=tk.BOTTOM)
    
    def save_matrix(self, matrix, ind_var, ind_var_unit, num_var, names, units, dimensions, range_type, ranges):
        """saves matrix as .npy file and parameters in separate .txt file"""
        matrix_file=fd.asksaveasfilename(initialdir=self.folder, title='Save Matrix')
        np.save(matrix_file, matrix)
        
        #save parameters in separate .txt file
        parameters=[names]+[units]+[dimensions]+[range_type]
        parameter_file=fd.asksaveasfile(initialdir=self.folder, title='Save Parameters', defaultextension='.txt')
        parameter_file.write('%s, %s, %d\n'%(ind_var, ind_var_unit, num_var))
        for i in range(4):
            for j in range(num_var):
                parameter_file.write('%s,'%(parameters[i][j]))
            parameter_file.write('\n')
        parameter_file.write('###################\n')
        
        for i in range(num_var):
            for j in range(len(ranges[i])):
                parameter_file.write('%f,'%(ranges[i][j]))
            parameter_file.write('\n')
        parameter_file.close()
        
    def file_format_widgets(self, frame, row, column):
        """creates widgets for reading input .txt files"""
        comments=tk.Label(frame, text='comment char').grid(row=row, column=column)
        self.comments_entry=ttk.Entry(frame)
        self.comments_entry.grid(row=row, column=column+1)

        delimiter=tk.Label(frame, text="delimiter char").grid(row=row, column=column+2)
        self.delimiter_entry=ttk.Entry(frame)
        self.delimiter_entry.grid(row=row, column=column+3)

        skiprows=tk.Label(frame, text='skiprows').grid(row=row, column=column+4)
        self.skiprows_entry=ttk.Entry(frame)
        self.skiprows_entry.grid(row=row, column=column+5)

        usecols=tk.Label(frame, text='Output value columns').grid(row=row, column=column+6)
        self.usecols_entry=ttk.Entry(frame)
        self.usecols_entry.grid(row=row, column=column+7)
      
    def plot_oneinall_format(self, dimensions, ranges, names, units, ind_var, ind_var_unit): 
        """creates figures, axes and formats labels for plotting the entire matrix in single 1D plots"""
        simulated_dimensions=self.simulated_dim(dimensions)
        self.graph_width, self.graph_height=5*dimensions[-2], 5*simulated_dimensions[-1]/simulated_dimensions[1]
        fig_size=(self.graph_width, self.graph_height)
        self.f=fig.Figure(figsize=fig_size, dpi=100)
        self.ax=self.f.subplots(simulated_dimensions[-1]/simulated_dimensions[1], dimensions[-2], sharex='col')     
        
        variable_counter=[0]*len(simulated_dimensions)  
        self.plot_labels=[([None]*dimensions[-2]) for i in range(simulated_dimensions[-1]/simulated_dimensions[1])]       
        for i, j in itertools.product(range(simulated_dimensions[-1]/simulated_dimensions[1]),
                                      range(dimensions[-2])):              
            plot_label=' ' #name of line in legend ie. the value of the variables not being plotted
            for m in range(len(dimensions[:-1])):
                if (i*dimensions[-2]+j)%(simulated_dimensions[1+m]/simulated_dimensions[0])==0 and (i*dimensions[-2]+j)!=0:
                    variable_counter[m]=0
                    variable_counter[m+1]+=1
                else:
                    variable_counter[0]=(i*dimensions[-2]+j)%dimensions[-2]
                plot_label+='%f%s,'%(ranges[-2-m][variable_counter[m]], units[-2-m]) 
            
            #sets the format
            if len(dimensions)==2:
                self.plot_labels[i][j]=plot_label
                self.ax[j].set_xlabel('%s (%s)'%(names[-1], units[-1]))
                self.ax[0].set_ylabel('%s (%s)'%(ind_var, ind_var_unit))
            else: 
                self.plot_labels[i][j]=plot_label
                self.ax[(simulated_dimensions[-1]/simulated_dimensions[1])-1, j].set_xlabel('%s (%s)'%(names[-1], units[-1]))
                self.ax[i, 0].set_ylabel('%s (%s)'%(ind_var, ind_var_unit))

    def plot_multiple_format(self, dimensions, ranges, names, units, ind_var, ind_var_unit):
        """creates figures, axes and formats labels for plotting a series of lines into a series of plots"""
        simulated_dimensions=self.simulated_dim(dimensions)        
        self.graph_width, self.graph_height=5*dimensions[-3], 5*simulated_dimensions[-1]/simulated_dimensions[2]
        fig_size=(self.graph_width, self.graph_height)
        self.f=fig.Figure(figsize=fig_size, dpi=100)       
        self.ax=self.f.subplots(simulated_dimensions[-1]/simulated_dimensions[2], dimensions[-3], sharex='col')  
          
        variable_counter=[0]*len(simulated_dimensions[:-2])            
        for i, j in itertools.product(range(simulated_dimensions[-1]/simulated_dimensions[2]), range(dimensions[-3])):                  
            if len(dimensions)==3:
                self.ax[j].set_xlabel('%s (%s)'%(names[-1], units[-1]))
                self.ax[0].set_ylabel('%s (%s)'%(ind_var, ind_var_unit))
                self.ax[j].set_title('%s=%f%s'%(names[-3], ranges[-3][j], units[-3]))
            else:
                subplot_title=' '
                for m in range(len(dimensions[:-2])):
                    if (i*dimensions[-3]+j)%(simulated_dimensions[2+m]/simulated_dimensions[1])==0 and (i*dimensions[-3]+j)!=0:
                        variable_counter[m]=0
                        variable_counter[m+1]+=1
                    else:
                        variable_counter[0]=(i*dimensions[-3]+j)%dimensions[-3]
                    subplot_title+='%f%s,'%(ranges[-3-m][variable_counter[m]], units[-3-m])            
                
                #sets the format
                self.ax[i, j].set_title(subplot_title)
                self.ax[(simulated_dimensions[-1]/simulated_dimensions[2])-1, j].set_xlabel('%s (%s)'%(names[-1], units[-1]))
                self.ax[i, 0].set_ylabel('%s (%s)'%(ind_var, ind_var_unit))
                        
    def plot_allinone_format(self, dimensions, ranges, names, units, ind_var, ind_var_unit):      
        """creates figures, axes and format labels for plotting the entire matrix as a series of lines in one plot"""
        simulated_dimensions=self.simulated_dim(dimensions)
        self.graph_width, self.graph_height=7, 7
        fig_size=(self.graph_width, self.graph_height)
        self.f=fig.Figure(fig_size, dpi=100)
        self.ax=self.f.add_subplot(111)
        
        variable_counter=[0]*len(simulated_dimensions)
        self.plot_labels=[]
        for i in range(simulated_dimensions[-1]/simulated_dimensions[0]):
            plot_label=' ' #name of line in legend ie. value of variables not being plotted
            for m in range(len(dimensions[:-1])):
                if i%(simulated_dimensions[1+m]/simulated_dimensions[0])==0 and i!=0:
                    variable_counter[m]=0
                    variable_counter[m+1]+=1
                else:
                    variable_counter[0]=i%dimensions[-2]
                plot_label+='%f%s,'%(ranges[-2-m][variable_counter[m]], units[-2-m]) 
            self.plot_labels+=[plot_label]
                   
        self.ax.set_xlabel('%s (%s)'%(names[-1], units[-1]))
        self.ax.set_ylabel('%s (%s)'%(ind_var, ind_var_unit))
    
    def plot_multiplesurface_format(self, dimensions, ranges, names, units, ind_var, ind_var_unit):
        """creates figures, axes and subplot titles for plotting multiple 2d surface plots"""
        simulated_dimensions=self.simulated_dim(dimensions)
        variable_counter=[0]*len(simulated_dimensions[:-1])  
        self.graph_width, self.graph_height=5*dimensions[-3], 5*simulated_dimensions[-1]/simulated_dimensions[2]
        fig_size=(self.graph_width, self.graph_height)
        self.f=fig.Figure(figsize=fig_size, dpi=100)
        self.ax=[([None]*dimensions[-3]) for i in range(simulated_dimensions[-1]/simulated_dimensions[2])]
        
        for i, j in itertools.product(range(simulated_dimensions[-1]/simulated_dimensions[2]), 
                                      range(dimensions[-3])):
            self.ax[i][j]=self.f.add_subplot(simulated_dimensions[-1]/simulated_dimensions[2], #number of rows
                                            dimensions[-3], #number of columns
                                            i*dimensions[-3]+j+1, #index of subplot
                                            projection='3d')
            subplot_title=' '
            for m in range(len(dimensions[:-2])):
                if (i*dimensions[-3]+j)%(simulated_dimensions[2+m]/simulated_dimensions[1])==0 and (i*dimensions[-3]+j)!=0:
                    variable_counter[m]=0
                    variable_counter[m+1]+=1
                else:
                    variable_counter[0]=(i*dimensions[-3]+j)%dimensions[-3]
                subplot_title+='%f%s,'%(ranges[-3-m][variable_counter[m]], units[-3-m])

            self.ax[i][j].set_title(subplot_title)
            self.ax[i][j].set_xlabel('%s (%s)'%(names[-1], units[-1]))
            self.ax[i][j].set_ylabel('%s (%s)'%(names[-2], units[-2]))
            self.ax[i][j].set_zlabel('%s (%s)'%(ind_var, ind_var_unit))
        
    def plot_singlesurface_format(self, names, units, ind_var, ind_var_unit):
        """creates figures and axes for plotting a single 2d surface plot"""
        self.graph_width, self.graph_height=7, 7
        fig_size=(self.graph_width, self.graph_height)
        self.f=fig.Figure(fig_size, dpi=100)

        self.ax=self.f.add_subplot(111, projection='3d')
        self.ax.set_xlabel('%s (%s)'%(names[-1], units[-1]))
        self.ax.set_ylabel('%s (%s)'%(names[-2], units[-2]))
        self.ax.set_zlabel('%s (%s)'%(ind_var, ind_var_unit))

    def invalid_plot(self): 
        """creates a figure explaining the chosen option cannot be plotted"""   
        self.graph_width, self.graph_height=7, 7
        fig_size=(self.graph_width, self.graph_height)
        self.f=fig.Figure(fig_size, dpi=100)
        self.ax=self.f.add_subplot(111)
        self.ax.text(0.5, 0.5, 'Cannot make plot given current dimensions') 