import pythoncom
pythoncom.CoInitialize()

import numpy as np
import clr
import lhsmdu

from System.IO import Directory, Path, File

dwsimpath = "C:\\Users\\ANRA\\AppData\\Local\\DWSIM7\\"

clr.AddReference(dwsimpath + "CapeOpen.dll")
clr.AddReference(dwsimpath + "DWSIM.Automation.dll")
clr.AddReference(dwsimpath + "DWSIM.Interfaces.dll")
clr.AddReference(dwsimpath + "DWSIM.GlobalSettings.dll")
clr.AddReference(dwsimpath + "DWSIM.SharedClasses.dll")
clr.AddReference(dwsimpath + "DWSIM.Thermodynamics.dll")
clr.AddReference(dwsimpath + "DWSIM.UnitOperations.dll")

clr.AddReference(dwsimpath + "DWSIM.Inspector.dll")
clr.AddReference(dwsimpath + "DWSIM.MathOps.dll")
clr.AddReference(dwsimpath + "TcpComm.dll")
clr.AddReference(dwsimpath + "Microsoft.ServiceBus.dll")

from DWSIM.Interfaces.Enums.GraphicObjects import ObjectType
from DWSIM.Thermodynamics import Streams, PropertyPackages
from DWSIM.UnitOperations import UnitOperations
from DWSIM.Automation import Automation2
from DWSIM.GlobalSettings import Settings

Directory.SetCurrentDirectory("C:\\Users\\ANRA\\Documents\\GitHub\\dwsim-paper\\")#dwsimpath)

sim_file_path = "C:\\Users\\ANRA\\Documents\\GitHub\\dwsim-paper\\simulations\\optimisation.dwxmz"

class DWSIM:
    def __init__(self, sim_file_path):
        self.sim_file_path = sim_file_path
        self.interf = Automation2()
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
        self.power = 0 
        self.rvp= 0
        self.crude_flow = 0
        self.vap_ratio = 0 
        self.load_simulation()

    def __call__(self,x):
        # vars in Pa (abs) and K
        self.sep1t=x[0]+273.15
        self.sep1p= (1.013+x[1])*1e5
        self.sep2p= (1.013+x[2])*1e5
        self.sep3t= x[3]+273.15
        self.sep3p=(1.013+x[4])*1e5
        self.scu1t=x[5]+273.15
        self.scu2t=x[6]+273.15
        self.scu3t=x[7]+273.15
        self.boostp=(1.013+x[8])*1e5
        self.refrig=x[9]+273.15              
        
        self.update_factors()
        
        err = self.interf.CalculateFlowsheet2(self.sim)
        err = self.interf.CalculateFlowsheet2(self.sim)

        if self.sim.Solved is False:
            err = self.interf.CalculateFlowsheet2(self.sim)
            if self.sim.Solved is False:
                self.load_simulation()
                self.update_factors()
                err = self.interf.CalculateFlowsheet2(self.sim)
                err = self.interf.CalculateFlowsheet2(self.sim)
                if self.sim.Solved is False:
                    self.update_wrong_responses()
            else:
                self.update_responses()    
        else:
            self.update_responses()
        
        print("Errors:",err)
        return np.asarray([self.crude_flow, self.power, self.rvp, self.vap_ratio])

    def load_simulation(self):
        self.sim = self.interf.LoadFlowsheet(self.sim_file_path)

    def update_wrong_responses(self):
        self.rvp = -9999
        self.power = -9999
        self.crude_flow = -9999

    def update_responses(self):
        self.rvp = self.sim.GetFlowsheetSimulationObject("MSTR-63").GetPressure() / 1e5 * 14.5
        p1 = self.sim.GetFlowsheetSimulationObject("23-KA-01").DeltaQ
        p2 = self.sim.GetFlowsheetSimulationObject("23-KA-02").DeltaQ
        p3 = self.sim.GetFlowsheetSimulationObject("23-KA-03").DeltaQ
        p4 = self.sim.GetFlowsheetSimulationObject("27-KA-01").DeltaQ
        p5 = self.sim.GetFlowsheetSimulationObject("21-PA-01").DeltaQ 
        self.power = p1 + p2 + p3 + p4 + p5
        self.crude_flow = self.sim.GetFlowsheetSimulationObject("MSTR-21").GetMolarFlow() * 3.600  # kmole/h
        #self.crude_flow = self.sim.GetFlowsheetSimulationObject("MSTR-22").GetPhase("OverallLiquid").Properties.volumetric_flow * 3600 
    
    def update_factors(self):
        self.sim.GetFlowsheetSimulationObject("MSTR-01").SetPressure(self.sep1p)
        self.sim.GetFlowsheetSimulationObject("20-HA-01").OutletTemperature = self.sep1t 
        self.sim.GetFlowsheetSimulationObject("VALV-01").OutletPressure = self.sep2p + 0.5e5
        self.sim.GetFlowsheetSimulationObject("VALV-02").OutletPressure = self.sep3p + 0.5e5
        #self.sim.GetFlowsheetSimulationObject("MSTR-32").SetPressure(self.sep3p + 0.5e5)
        self.sim.GetFlowsheetSimulationObject("20-HA-03").OutletTemperature = self.sep3t 
        self.sim.GetFlowsheetSimulationObject("23-HA-01").OutletTemperature = self.scu1t 
        self.sim.GetFlowsheetSimulationObject("23-HA-02").OutletTemperature = self.scu2t 
        self.sim.GetFlowsheetSimulationObject("23-HA-03").OutletTemperature = self.scu3t 
        self.sim.GetFlowsheetSimulationObject("23-KA-01").CalcMode =  UnitOperations.Compressor.CalculationMode.Delta_P
        self.sim.GetFlowsheetSimulationObject("23-KA-01").DeltaP = self.boostp - self.sep1p + 1.5e5
        self.sim.GetFlowsheetSimulationObject("25-HA-02").OutletTemperature = self.refrig

        self.vap_ratio = self.sim.GetFlowsheetSimulationObject("MSTR-63").GetPhase("Vapor").Properties.volumetric_flow / self.sim.GetFlowsheetSimulationObject("MSTR-63").GetPhase("OverallLiquid").Properties.volumetric_flow        

def scale_sampling_plan(X, limits):
    X_n = np.zeros(X.shape)
    i=0
    for lim in limits:
        mid=sum(lim)/len(lim)
        range=max(lim)-min(lim)
        
        X_n[:,i] = X[:,i]*range+min(lim)
        i+=1
        
    return X_n

if __name__=="__main__":
    dwsim=DWSIM(sim_file_path)

    #Uncomment next lines if generating a NEW sampling plan
    #xlimits=[(40,70),(11,32),(3,10),(50,75),(0.5,2),(25,40),(25,40),(25,40),(60,90),(-5,28)] 
    #X=lhsmdu.createRandomStandardUniformMatrix(100,10)
    #X_n=scale_sampling_plan(X,xlimits)
    #np.savetxt("raw_testplan.csv",X,delimiter=",")
    #np.savetxt("scaled_testplan.csv",X_n,delimiter=",")
    
    # Loading already existing sampling plan
    X_n = np.loadtxt("data\\scaled_testplan.csv",delimiter=",")
    Y=np.zeros((len(X_n),4))
        
    for i in range(len(X_n)):
        Y[i,:] = dwsim(X_n[i,:])
        print("Finished simulation no: ", i, " out of", len(X_n), " Vap ratio: ", dwsim.vap_ratio)
    
    np.savetxt("DWSIM_result.csv",Y,delimiter=",")