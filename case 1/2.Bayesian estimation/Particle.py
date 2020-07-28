import os
from epanettools import epanet2 as et
from epanettools.examples import simple
import numpy as np
import pandas as pd
from global_variable import *
import copy
def openEPANET(INP):
    errcode=et.ENopen(INP,"BUFF.rpt","")
    if(errcode>100):
        print('error in open INP')

def saveInpfile(fileName):
    errcode=et.ENsaveinpfile(fileName)

def closeEPANET():
    errcode=et.ENclose()


def particle_initial():
    Particles=[]
    for i in range(NUM_PARTS):#particles initizlation
        part=demands()
        part.pred_values=0
        part.pred_variance=0
        part.currentTime=0
        part.dim=PART_DIM

        part.sensorID_Res=ResID
        part.sensorID_P=PreID
        part.sensorID_F=FloID
        part.weight=1/NUM_PARTS
        part.pred_std=PART_PREDICE_STD
        part.measured_sim={}
        part.values=[]
        for j in range(PART_DIM):
            part.values.append(average_demand+np.random.normal(0, PART_PREDICE_STD ))
        Particles.append(part)
    return Particles

def updateParticlesWeight(particles,weight_all):
    for i in range(len(weight_all)):
        particles[i].weight=copy.deepcopy(weight_all[i])

def reSampling(particles):
    newParticles=[]
    weight=[]
    n=len(particles)
    for part in particles:
        weight.append(part.weight)
    CDF=[0.]+[sum(weight[:i+1])for i in range(n)]#Cumulative probability density for the particles


    u0,j=np.random.rand(),0
    for u in [(u0+i)/n for i in range(n)]:
        while u>CDF[j]:#碰到小粒子，跳过
            j=j+1
        newpart=particles[j-1]
        newpart.weight=1/n
        newParticles.append(newpart)
    return newParticles



def getEstimatedParameters(particles):
    para_expection=[0]*PART_DIM
    part_all=[]
    weight_all=[]
    for part in particles:
        part_all.append(part.values)
        weight_all.append(part.weight)
        for i in range(PART_DIM):
            para_expection[i]=para_expection[i]+part.values[i]*part.weight
    
    cov=np.zeros((PART_DIM,PART_DIM))
    part_all=np.array(part_all)
    for i in range(len(part_all)):
        part_value=part_all[i]
        res=np.array(part_value-para_expection).reshape(PART_DIM,1)
        cov=cov+res.dot(res.T)*weight_all[i]

    return para_expection,cov



class demands:
    def _init_(self):
        self.currentTime=0
        self.dim=0
        self.weight=0
        self.values=[]
        self.pred_values=0
        self.pred_variance=0
        self.para=[] #Nodal demand
        self.sim_nodal_p=[]  #nodal pressure
        self.sim_pipe_f=[]  #pipe flow
        self.sensorID_Res=[]
        self.sensorID_P=[]    #pressure sensor ID
        self.sensorID_F=[]    #Flow sensor ID
        self.measured_sim={} #simulated values corresponding to the measurements
        self.resid=[]
    def hyd_simulation(self):
        for index in range(self.dim):
            index=index+1
            value=self.values[index-1]+0.0
            errcode=et.ENsetnodevalue(index,et.EN_BASEDEMAND,self.values[index-1])
        et.ENsolveH()

    def getSensorValue(self):
        self.hyd_simulation()
        Res={}
        P={}
        F={}

        for id in self.sensorID_Res:
            [errcode,index]=et.ENgetnodeindex(id)
            [errcode,demand]=et.ENgetnodevalue(index,et.EN_DEMAND)
            Res[id]=demand
        for id in self.sensorID_P:
            [errcode,index]=et.ENgetnodeindex(id)
            [errcode,pressure]=et.ENgetnodevalue(index,et.EN_PRESSURE)
            P[id]=pressure

        for id in self.sensorID_F:
            [errcode,index]=et.ENgetlinkindex(id)
            [errcode,flow]=et.ENgetlinkvalue(index,et.EN_FLOW)
            F[id]=flow
        self.measured_sim['Res']=Res
        self.measured_sim['P']=P#Save the simulated sensor pressure
        self.measured_sim['F']=F#Save the simulated sensor flow

    def getResidul(self,MeaData):
        self.resid=[]
        self.getSensorValue()
        for id in self.sensorID_Res:
            self.resid.append(MeaData.Data['Res'][id]-self.measured_sim['Res'][id])
        for id in self.sensorID_P:
            self.resid.append(MeaData.Data['P'][id]-self.measured_sim['P'][id])
        for id in self.sensorID_F:
            self.resid.append(MeaData.Data['F'][id]-self.measured_sim['F'][id])
    


    def sampleFromPrior(self,priorDist):
        #np.random.seed(0)
        self.weight=1/self.dim

        for i in range(len(self.values)):
            randvalue=np.random.normal(0,priorDist.prior_variance[i][i]**0.5,1)
            randvalue=randvalue.tolist()[0]
            self.values[i]=priorDist.prior_values[i]+randvalue


class estimateDemandResult:
    def _init_(self):
        self.time=0
        self.demand_dim=0
        self.sensorID_Res=[]
        self.sensorID_P=[]    #pressure sensor ID
        self.sensorID_F=[]    #Flow sensor ID

        self.cali_demand_values=[]#外部更新
        self.cali_demand_variance=[]#外部更新

        self.cali_nodal_p=[]  #nodal pressure
        self.cali_pipe_f=[]  #pipe flow
        self.measured_sensor={}
        self.cali_sensor={}
        self.cali_resid={}

    def hyd_simulation(self):
        for index in range(self.demand_dim):
            index=index+1
            errcode=et.ENsetnodevalue(index,et.EN_BASEDEMAND,self.cali_demand_values[index-1])
        et.ENsolveH()

    def updateResult(self):
        self.hyd_simulation()
        #########update the calibrated value at sensors#########
        Res={}
        P={}
        F={}

        for id in self.sensorID_Res:
            [errcode,index]=et.ENgetnodeindex(id)
            [errcode,demand]=et.ENgetnodevalue(index,et.EN_DEMAND)
            Res[id]=demand
        for id in self.sensorID_P:
            [errcode,index]=et.ENgetnodeindex(id)
            [errcode,pressure]=et.ENgetnodevalue(index,et.EN_PRESSURE)
            P[id]=pressure

        for id in self.sensorID_F:
            [errcode,index]=et.ENgetlinkindex(id)
            [errcode,flow]=et.ENgetlinkvalue(index,et.EN_FLOW)
            F[id]=flow
        self.cali_sensor['Res']=Res
        self.cali_sensor['P']=P#Save the simulated sensor pressure
        self.cali_sensor['F']=F#Save the simulated sensor flow
        #########update the calibrated nodal pressure and pipe flow rate#########
        for index in range(self.demand_dim):
            [errcode,pressure]=et.ENgetnodevalue(index+1,et.EN_PRESSURE)
            self.cali_nodal_p.append(pressure)
        for index in range(Number_PIPES):
            [errcode,flow]=et.ENgetlinkvalue(index+1,et.EN_FLOW)
            self.cali_pipe_f.append(flow)

        self.getResidul()

    def updateMeasured(self,Res,Pressure,Flow,time):

        self.measured_sensor['Res']={}
        self.measured_sensor['P']={}
        self.measured_sensor['F']={}
        for id in self.sensorID_Res:        #save the real time measurement to the class sensor
            self.measured_sensor['Res'][id]=Res.loc[time,id]

        for id in self.sensorID_P:
            self.measured_sensor['P'][id]=Pressure.loc[time,id]

        for id in self.sensorID_F:
            self.measured_sensor['F'][id]=Flow.loc[time,id]
        

    def getResidul(self):
        self.cali_resid=[]
        for id in self.sensorID_Res:
            self.cali_resid.append(self.cali_sensor['Res'][id]-self.measured_sensor['Res'][id])
        for id in self.sensorID_P:
            self.cali_resid.append(self.cali_sensor['P'][id]-self.measured_sensor['P'][id])
        for id in self.sensorID_F:
            self.cali_resid.append(self.cali_sensor['F'][id]-self.measured_sensor['F'][id])



class priorDistributon:
    def _init_(self):
        self.prior_values=0
        self.prior_variance=0
        self.pred_values=0
        self.pred_variance=0
    def predictUpdate(self,result_previous):#使用前一个时刻数据得到预测分布
        self.pred_values=result_previous.cali_demand_values
        self.pred_variance=result_previous.cali_demand_variance
        for i in range(PART_DIM):#前一个时刻方差加上预测方差
            self.pred_variance[i][i]=self.pred_variance[i][i]+PART_PREDICE_STD**2
    def updatePriorValue(self,Measured_Demand,time):
        priorValue=[]
        measured_value=Measured_Demand.loc[time]
        for i in range(PART_DIM):
            mean_measured=measured_value[i]
            mean_predict=self.pred_values[i]
            variance_measured=MEASURED_DEMAND_STD[i]**2
            variance_predict=self.pred_variance[i][i]

            value=(mean_measured*variance_predict+mean_predict*variance_measured)/(variance_measured+variance_predict)
            priorValue.append(value)
        self.prior_values=priorValue

    def updatePriorVariance(self,Measured_Demand,time):
        measured_value=Measured_Demand.loc[time]
        self.prior_variance=np.zeros((PART_DIM,PART_DIM))
        for i in range(PART_DIM):
            variance_measured=MEASURED_DEMAND_STD[i]**2
            variance_predict=self.pred_variance[i][i]
            self.prior_variance[i][i]=(variance_measured* variance_predict)/(variance_measured+ variance_predict)


def generatePriorDist():
    PriorDist=priorDistributon()
    PriorDist.pred_values=0
    PriorDist.pred_variance=0
    PriorDist.prior_values=0
    PriorDist.prior_variance=0
    return PriorDist


def generateEstimateDemandResult():

    result=estimateDemandResult()
    result.time=0
    result.demand_dim=PART_DIM
    result.sensorID_Res=ResID
    result.sensorID_P=PreID    #pressure sensor ID
    result.sensorID_F=FloID    #Flow sensor ID

    result.cali_demand_values=[0]*PART_DIM
    result.cali_demand_variance=10000000000000*np.ones((PART_DIM,PART_DIM))
    result.cali_nodal_p=[]  #nodal pressure
    result.cali_pipe_f=[]  #pipe flow

    result.measured_sensor={}
    result.cali_sensor={}
    result.cali_resid={}
    return result
