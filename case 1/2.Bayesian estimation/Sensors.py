import numpy as np
import pandas as pd
import copy
from global_variable import *

def sensor_initial():
    MeaData=sensors()
    MeaData.t=Sensor_T
    MeaData.dim=SENSOR_NUM
    MeaData.ID_Res=ResID
    MeaData.ID_P=PreID
    MeaData.ID_F=FloID
    MeaData.alpha=10
#initial fai
    MeaData.fai['Res']={}
    MeaData.fai['P']={}
    MeaData.fai['F']={}
    for id in ResID:
        MeaData.fai['Res'][id]=100
    for id in PreID:
        MeaData.fai['P'][id]=100
    for id in FloID:
        MeaData.fai['F'][id]=100
    MeaData.fai_predict=copy.deepcopy(MeaData.fai)
#initial R
    MeaData.R['Res']={}
    MeaData.R['P']={}
    MeaData.R['F']={}
    for id in ResID:
        MeaData.R['Res'][id]=0.25
    for id in PreID:
        MeaData.R['P'][id]=0.04
    for id in FloID:
        MeaData.R['F'][id]=0.25
    return MeaData

def getfai_l(fai_predict,ResidulSqure):
    fai_l={}
    fai_l['Res']={}
    fai_l['P']={}
    fai_l['F']={}
    for id in ResID:
        fai_l['Res'][id]=fai_predict['Res'][id]+ResidulSqure['Res'][id]
    for id in PreID:
        fai_l['P'][id]=fai_predict['P'][id]+ResidulSqure['P'][id]
    for id in FloID:
        fai_l['F'][id]=fai_predict['F'][id]+ResidulSqure['F'][id]
    return fai_l


def getR( fai_l,alpha):
    R={}
    R['Res']={}
    R['P']={}
    R['F']={}
    for id in ResID:
        R['Res'][id]=fai_l['Res'][id]/(alpha-SENSOR_NUM-1)
    for id in PreID:
        R['P'][id]=fai_l['P'][id]/(alpha-SENSOR_NUM-1)
    for id in FloID:
        R['F'][id]=fai_l['F'][id]/(alpha-SENSOR_NUM-1)
    return R



class sensors:
    def __init__(self):
        self.currentTime=0
        self.dim=0
        self.t=0.99#IW分布全局参数
        self.alpha=0  #IW分布参数
        self.fai={} #IW分布参数
        self.R={}#协方差
        self.alpha_predict={}  #IW分布参数
        self.fai_predict={} #IW分布参数
        self.ID_Res=[]
        self.ID_P=[]    #pressure sensor ID
        self.ID_F=[]    #Flow sensor ID
        self.Data={} #measured values
    def updateMeasured(self,Res,Pressure,Flow,time):
        self.currentTime=time
        self.Data['Res']={}
        self.Data['P']={}
        self.Data['F']={}
        for id in self.ID_Res:        #save the real time measurement to the class sensor
            self.Data['Res'][id]=Res.loc[time,id]

        for id in self.ID_P:
            self.Data['P'][id]=Pressure.loc[time,id]

        for id in self.ID_F:
            self.Data['F'][id]=Flow.loc[time,id]
        

    def predict(self):#prior value
        self.alpha_predict=self.t*(self.alpha-self.dim-1)+self.dim+1
        for id in ResID:
            self.fai_predict['Res'][id]=self.fai['Res'][id]*self.t*self.t
        for id in PreID:
            self.fai_predict['P'][id]=self.fai['P'][id]*self.t*self.t
        for id in FloID:
            self.fai_predict['F'][id]=self.fai['F'][id]*self.t*self.t

    def updatePara(self,alpha,fai_l):
        self.fai=copy.deepcopy(fai_l)
        for id in ResID:
            self.R['Res'][id]=fai_l['Res'][id]/(alpha-SENSOR_NUM-1)
        for id in PreID:
            self.R['P'][id]=fai_l['P'][id]/(alpha-SENSOR_NUM-1)
        for id in FloID:
            self.R['F'][id]=fai_l['F'][id]/(alpha-SENSOR_NUM-1)




