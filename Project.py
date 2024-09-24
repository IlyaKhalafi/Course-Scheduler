''' 
 Student fullname :
       Ilya Khalafi
 Student ID:
       9913039
'''

'''
 Make sure pandas and pulp are installed...
 use the command below to install pulp and pandas using pip:
 pip install pulp pandas openpyxl
'''

# Importing dependencies
import pandas as pd
from pulp import *
from Models import *
import time

# Reading data from excel file
teachers_data = pd.read_excel('Data.xlsx', sheet_name='Teachers')
classes_data = pd.read_excel('Data.xlsx', sheet_name='Classes')
courses_data = pd.read_excel('Data.xlsx', sheet_name='Courses')

# Making objects
Days = {(k+1):day for k,day in enumerate(teachers_data.columns.tolist()[-6:])}
MAX = 1e6

Teachers = {(i+1):Teacher(
      teachers_data['Name'][i],
      teachers_data['Knowledge'][i],
      teachers_data['Salary/Class'][i],
      teachers_data['Max Class'][i],
      {
      # Accessibility of teacher in each day
      k:
            {
                  (t+1):[float(x) for x in s.split(',')]
                  for t,s in enumerate(teachers_data[Days[k]][i].split())
            }
      for k in Days
      },
      0
      )
      for i in teachers_data.index}

cancel_flag = Teacher('Cancel', MAX, 0, MAX, {i:{1:[8,12], 2:[15,20]} for i in Days}, 1)
Teachers[len(Teachers)+1] = cancel_flag

Courses = {(j+1):Course(
      courses_data['Title'][j],
      courses_data['Level'][j],
      courses_data['Fee'][j]
      )
      for j in courses_data.index}

Classes = {(j+1):Class(
      classes_data['Code'][j],
      Courses[classes_data['Course'][j]],
      classes_data['Students count'][j],
      classes_data['Sessions per Week'][j]
      )
      for j in classes_data.index}

# making model object
lp = LpProblem("Language_Center", LpMaximize)

# Defining decision variables
x = {
      i: 
      {
            (j):LpVariable(f'x{i},{j}', cat=const.LpBinary) 
            for j in Classes
      } 
      for i in Teachers}

d = {
      i:
      {
            j: 
            {
                  k:LpVariable(f'd{i},{j},{k}', cat=const.LpBinary) 
                  for k in Days
            } 
            for j in Classes
      }
      for i in Teachers}

s = {
    i:
    {
        j:
        {
            k: 
            {
                  t:LpVariable(f's{i},{j},{k},{t}', cat=const.LpBinary) 
                  for t in Teachers[i].accessibility
            }
            for k in Days
        }
        for j in Classes
    }
    for i in Teachers}

b = {j:LpVariable(f'b{j}', lowBound=0) for j in Classes}

e = {j:LpVariable(f'e{j}', lowBound=0) for j in Classes}

# Adding objective function to the model
lp += (
      + lpSum([Classes[j].course.fee * Classes[j].students_count * x[i][j] * (1-Teachers[i].dummy)
               for i in Teachers for j in Classes]) # Total fee
      
      - lpSum([Teachers[i].salary * x[i][j] * (1-Teachers[i].dummy)
               for i in Teachers for j in Classes]) # Total salary
      
      - lpSum([Teachers[i].insurance*lpSum(
            [d[i][j][k] for j in Classes for k in Days]
            ) *1.5 /44 /52 * (1-Teachers[i].dummy) # Insurance needs Working 44 hours in a week and 52 weeks in a year
            for i in Teachers]) # Total insurance
      )

# Adding constraints to the model
for j in Classes:
      lp += lpSum([x[i][j] for i in Teachers]) <= 1 # Each class has at most one teacher
      
      # Neccessary Teacher knowledge level
      lp += lpSum([Teachers[i].knowledge * x[i][j] for i in Teachers]) >= Classes[j].course.level
      
      lp += b[j] <= e[j] # beginning <= end for each class period
      
      for i in Teachers:
            lp += lpSum([d[i][j][k] for k in Days]) == Classes[j].sessions * x[i][j] # Amount of class sessions
            
            for k in Days:
                  # Class should be in exactly one of accessibilty period of teacher in each day
                  # If the class won't be in that day, then d[i][j][k] will be 0 and no period will contain the class
                  lp += lpSum([s[i][j][k][t] for t in Teachers[i].accessibility[k]]) == d[i][j][k]
                  
                  for t in Teachers[i].accessibility[k]:
                  
                        # If a period of accessibility is selected for the class
                        # then beginning of class period should be after the beginning of the period
                        lp += s[i][j][k][t]*Teachers[i].accessibility[k][t][0] <= b[j]
                        # Also end of class period should be before the end of the period
                        lp += s[i][j][k][t]*Teachers[i].accessibility[k][t][1] + (1-s[i][j][k][t])*24 >= e[j] + 1.5
            
for i in Teachers:
      lpSum([x[i][j] for j in Classes]) <= Teachers[i].max_class # Maximum number of classes for teacher

# Printing model details
print('-' * 50)
print(f'Total Number of Variables : {len(lp.variables())}')
print(f'Total Number of Constraints : {len(lp.constraints)}')

# Solving the model
start = time.perf_counter()
lp.solve(PULP_CBC_CMD(msg=False))
totalTime = time.perf_counter() - start
# If you want to see the pulp messages, use the following line instead...
# lp.solve()

# Printing model status
print('-' * 50)
print(f'Total Calculation Time : {totalTime}')
print(f'Model\'s Result : {LpStatus[lp.status]}')

# Printing the optimized value
print('-' * 50)
print(f'z* = {value(lp.objective)}')

# Printing the values of the variables
print('-' * 50)
print('Print optimal value for all variables? (y,n)', end=' ')
if input().lower() == 'y':
      for var in lp.variables():
            print(f'{var.name}* = {var.varValue}')

# Printing human readable solution
print('-' * 50)
print('Print human readable solution? (y,n)', end=' ')
if input().lower() == 'y':
    for j in Classes:
            for i in Teachers:
                  if x[i][j].varValue == 1:
                        if Teachers[i].name == 'Cancel':
                            print(f'{Classes[j].course.title} with Code {Classes[j].code} Should be canceled\n')
                        else:
                              print(
                                    f"Class {Classes[j].course.title} with Code {Classes[j].code}" 
                                    f"\nshould be taught by {Teachers[i].name} \ncan be held on {[Days[k] for k in Days if d[i][j][k].varValue == 1]}"
                                    f"\nat anytime in range of {b[j].varValue} to {e[j].varValue}\n"
                                    )
                              hasTeacher = True
                        break


# Avoiding the program to exit
# so you can just click this file to run the code
print('-' * 50)
a = input('Press any key to exit...')
