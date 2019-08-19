# A3MD- application for aggregating and analyzing multivariable data
An application written in Python with a GUI written in Tkinter that aggregates 
experimental data dependant on multiple variables into a nested array. From the 
nested array, multiple modes of analysis and visualization can be performed. For
a more detailed list of its capabilities, please see below.

## Technologies
Project is created with:
Python version: 2.7
### Libraries:
NumPy version: 1.15.3
Matplotlib version: 2.2.3
SciPy version: 0.15.1
Tkinter version: 8.5

## Capabilities for data manipulation and analysis:
1. Slicing the array along different axes
2. Moving the axes to different positions
3. Performing numerical derivatives along any axes
4. Performing a fast fourier transform along any axis
5. Performing a custom function that is hard coded by the user (see 'custom.py')
6. Fitting the array to a series of linear, exponential, or sinusoidal functions
7. Fitting the array to a series of planar, paraboloid, or hyperboloid functions
8. Fitting the array to a series of custom 1D or 2D functions (see 'custom.py')
 
## Capabilities for data visualization
1. Plotting the array as a series of single line subplots
2. Plotting the array as a series of subplots containing multiple lines
3. Plotting the entire array in a single subplot
4. Plotting the array as a single or multiple 2D surface plots
5. Plotting the array as a single or multiple 2D contour plots

## main.py
Main Python file which launches the application as a GUI. Needs Shared_Functions.py in the 
same directory to perform properly. Contains 6 different classes. 5 of the 6 classes are 
pages that the user sees and interacts with. One of the classes acts as a controller class 
which allows interaction between the other pages.
### Data_Analysis Class
Controller class that contains dictionaries for variables that are shared between pages. 
Contains show_frame function that allows use to switch between different pages (coded as 
different frames in Tkinter).
### StartPage Class
First page that user sees when opening the program.
### Inputs Class
First page that user interacts with. Allows user to manually input parameters for their 
nested array as well as upload .txt or .csv data files to create the nested array. User 
can also load in a previously created nested array.
### Matrix_Fun Class
Page for user to manipulate and analyze data. Performs first five points described in 
"Capabilities for data manipulation and analysis". See 'custom.py' for more details on 
performing a custom function. Also performs all functions described in "Capabilities for 
data visualization".
### Editor Class (Beta)
Page for user to add data to a nested array after it's already been created. Currently in beta
stage. Currently capable of adding an extra new dimension (Define New Variable) or inserting 
a new entry into an already existing dimension (Insert Value). Need to add ability to reset
inputs because if the user makes a mistake adding an input in its current stage, the user
will have to close the entire program to continue.
### Function_Fitting Class
Page for user to fit data to common or custom functions. Performs last three points 
described in "Capabilities for data manipulation and analysis". See 'custom.py' for more 
details on fitting to a custom function. Also performs all functions described in 
"Capabilities for data visualization".

## Shared_Function.py
Python file that contains functions that multiple classes in 'main.py' uses. Should be in
same directory as 'main.py'.
### Shared_Functions Class
Contains all the functions that are shared between classes in 'main.py'. Defined as a class
within the file so each page in 'main.py' can call an instance of it without the __init__ 
variables affecting each other. Essentially allows classes in 'main.py' to share functions
without sharing certain variables.

## custom.py
Python file for user to hard code custom functions for data manipulation/analysis or fitting.
This is meant for users who have experience coding in Python and would like to perform a
function not included in "Capabilities for data manipulation and analysis". 
### custom_func function
Function included in Matrix_Fun Class for manipulating/analyzing nested array. The dictionary
refers to the copy dictionary found in the Controller Class. Included in the dictionary is:
the name of the output variable, the unit of the output variable, the number of input variables,
a list containing the names of the input variables, a list containing the units of the input
variables, a list containing whether the values of the input variables are uniform, a nested
list of all the values in each input variable, a list containing the number of values in each
input variable, and the nested output array.
### custom_fit function
Function inluded in Function_Fitting Class for defining a custom function to fit the data to. 
Can be a one dimensional or two dimensional function.

## Status
The Editor Class/page is still in the beta stage. Although it works correctly, there are no 
failsafes in case the user adds in an unreasonable input. Another thing to add is the
ability to define parameters such as variable name or variable values by reading from a file
instead of manually defining them all.
