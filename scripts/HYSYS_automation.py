# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import os
import time
import numpy as np
import win32com.client as win32
from platypus import Problem, Real, NSGAII
import pyKriging
from pyKriging.krige import kriging
from pyKriging.samplingplan import samplingplan

class HYSYSopt():
        def __init__(self,hysys):
            #super(HYSYSopt, self).__init__(1,1,1)
            print("Creating the Solver Class")
            #self.types[:]= [Real(1.8,2.6)]              #Bound
            #self.constraints[:] = "<=0"
            self.hyapp = hysys
            # Check if object can be called upon initialisation
            
            self.sep1t = 0 
            self.sep1p = 0 
            self.sep2p = 0 
            self.sep3t = 0 
            self.sep3p = 0 
            self.scu1t = 0 
            self.scu2t = 0 
            self.scu3t = 0 
            self.refrig = 0 
            self.boostp = 0 
            self.power= 0 
            self.rvp= 0
            #self.dewpoint=0 
            #self.profit=0 
            self.crude_flow= 0 
            #self.gas_flow=out_sheet = 0 
            #self.co2=out_sheet = 0 
            self.fname = "Z:\\Academia\\DWSIM\\Optim.hsc"
            self.load_simcase()
            
            
        def update_factors(self):
            sp_sheet=self.sheet.Operations.Item('Input')
             
            sp_sheet.Cell(1,1).CellValue = self.sep1t
            sp_sheet.Cell(2,1).CellValue = self.sep1p
            sp_sheet.Cell(2,2).CellValue = self.sep2p
            sp_sheet.Cell(1,3).CellValue = self.sep3t
            sp_sheet.Cell(2,3).CellValue = self.sep3p
            sp_sheet.Cell(1,4).CellValue = self.scu1t
            sp_sheet.Cell(1,5).CellValue = self.scu2t
            sp_sheet.Cell(1,6).CellValue = self.scu3t
            sp_sheet.Cell(1,8).CellValue = self.refrig
            sp_sheet.Cell(2,9).CellValue = self.boostp
            
        
        def update_responses(self):
            out_sheet=self.sheet.Operations.Item('Objectives')
            
            self.power=out_sheet.Cell(1,3).CellValue
            self.rvp=(out_sheet.Cell(1,10).CellValue)/100*14.5 # kPa to psia
            #self.dewpoint=out_sheet.Cell(1,11).CellValue
            #self.profit=out_sheet.Cell(1,9).CellValue
            self.crude_flow=out_sheet.Cell(1,12).CellValue*3600 # kmole / h 
            #self.gas_flow=out_sheet.Cell(1,2).CellValue*3600*24 # Sm3/s to Sm3/d
            #self.co2=out_sheet.Cell(1,8).CellValue*3600 # kg/s to kg/h
    
        def powernotchanged(self):
            out_sheet=self.sheet.Operations.Item('Objectives')
            if self.power!=out_sheet.Cell(1,3).CellValue:
                return False
            else:
                return True

        def load_simcase(self):
            try:
                self.simcase = win32.GetObject(self.fname)
            except:
                self.simcase = self.hyapp.ActiveDocument
            
            self.simcase.Visible = True
            self.sheet = self.simcase.Flowsheet
            self.solver = self.simcase.Solver
            
        def convergence_check(self):
            rcl_sheet=self.sheet.Operations.Item('Recycle')
            if rcl_sheet.Cell(1,6).CellValue!=1: #or abs(rcl_sheet.Cell(2,5).CellValue)>0.1: 
                raise
        
        def __call__(self,x):
            self.sep1t=x[0]
            self.sep1p= (1.013+x[1])*100
            self.sep2p= (1.013+x[2])*100
            self.sep3t= x[3]
            self.sep3p=(1.013+x[4])*100
            self.scu1t=x[5]
            self.scu2t=x[6]
            self.scu3t=x[7]
            self.boostp=(1.013+x[8])*100
            self.refrig=x[9]                      
            
            # Hold solver before setting/changing multiple parameters
            self.solver.Cansolve = False
            self.update_factors()
            
            # Start the flowsheet solver
            #try: wrap solver and reset recycle streams on exception
            try:
                self.solver.CanSolve = True
                
                #Wait until solver is done before reading any values
                while self.solver.issolving: #or self.powernotchanged():
                    time.sleep(1)
                    print("waiting for solver")
                 
                    
                self.update_responses()
                #self.convergence_check()
                
            except:
                print("!!!!!!!Solver failed - resetting!!!!!!!!!!!")
                self.solver.CanSolve = False
                
                rcl_sheet=self.sheet.Operations.Item('Recycle')
                rcl_sheet.Cell(0,0).CellValue=100
                rcl_sheet.Cell(0,1).CellValue=100
                rcl_sheet.Cell(0,1).CellValue=100
                
                try:
                    self.solver.CanSolve = True
                    while self.solver.issolving: #or self.powernotchanged():
                        time.sleep(1)
                        print("waiting for solver")
                        
                    self.update_responses()
                    self.convergence_check()
                    
                except:
                    self.simcase.close()
                    self.load_simcase()
                                        
                    print("????? Reset failed - restarting ?????")
                    self.solver.CanSolve = False
                    self.update_factors()
                    
                    
                    self.solver.CanSolve = True
                    while self.solver.issolving: #or self.powernotchanged():
                        time.sleep(1)
                        print("waiting for solver")
                      
                    self.update_responses()
                    self.convergence_check()
            
            self.update_responses()      
            return np.asarray([self.crude_flow, self.power, self.rvp])

#        def evaluate(self, solution):
#            print "Called evaluate"
#
#            x = solution.variables
#            
#            
#            f,g,fail = self(x)
#            
#            solution.objectives = f
#            solution.constraints = g

def scaleSamplingPlan(X, limits):
    X_n = np.zeros(X.shape)
    i=0
    for lim in limits:
        mid=sum(lim)/len(lim)
        range=max(lim)-min(lim)
        
        X_n[:,i] = X[:,i]*range+min(lim)
        i+=1
        
    return X_n      

n_var=10    
n_fact=3
n_sample=20
hyapp = win32.Dispatch('HYSYS.Application.v11.0')
#hyapp = win32.Dispatch('UniSimDesign.Application')

hyapp.Visible = True

hycalc=HYSYSopt(hyapp) # Maybe not needed, maybe just the the simcase?

xlimits=[(50,70),(11,32),(2.5,10),(40,75),(0.5,2),(25,40),(25,40),(25,40),(60,90),(-5,28)] 

X_n=np.loadtxt("scaled_testplan.csv",delimiter=",")
Y=np.zeros((len(X_n),3))
        
for i in range(len(X_n)):
    print("Running simulation no: ", i, " out of", len(X_n))
    Y[i,:] = hycalc(X_n[i,:])

np.savetxt("HYSYS_result.csv",Y,delimiter=",")
# sp = samplingplan(n_var)
# X = sp.optimallhc(n_sample*n_var)
# X_n=scaleSamplingPlan(X,xlimits)
# #
# Y=np.zeros((len(X_n),n_fact))
# #
# t1= time.time()

# ## make something that creates a restart if simulation failed.
# title=['crudeflow','power','rvp','sep1t','sep1p','sep2p','sep3t','sep3p','scu1t','scu2t','scu3t','boostp','refrig']


# for i in range(len(X_n)):
#     #print "Progress", float(i)/len(X_n)*100, "%, Power",  #"%, x: ", X_n[i,:]
#     try:
#         hycalc=HYSYSopt(hyapp)
#         Y[i,:] = hycalc(X_n[i,:])
#         #hycalc.simcase.close()
#     except:
#         Y[i,:] = np.asarray([np.NaN,np.NaN,np.NaN])
#     print("Progress", float(i)/len(X_n)*100, "%, Power",  Y[i,1])#"%, x: ", X_n[i,:]
#     np.savetxt("Z:/Academia/AUE/Projects/General_simulation_optimisation/results_timing.csv", np.concatenate((Y,X_n),axis=1), delimiter=',',header=','.join(title))

# t2= time.time()
# print("Sim time: ", t2-t1)
