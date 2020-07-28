from epanettools import epanet2 as et
from epanettools.examples import simple
from global_variable import *
import numpy as np
import pandas as pd
from epanet import *
import copy
class priorDistributon:
    def _init_(self):
        self.prior_values=0
        self.prior_variance=0
        self.pred_values=0
        self.pred_variance=0
        self.node_id=[]
    def predictUpdate(self,result_previous):#使用前一个时刻数据得到预测分布
        self.pred_values=result_previous.cali_demand_values

        predictVar=np.identity(DEMAND_NUM)
        for i in range(DEMAND_NUM):
            predictVar[i][i]=DEMAND_PREDICT_STD[i]**2
        self.pred_variance=result_previous.cali_demand_variance+ predictVar

    def updatePrior(self,Measured_Demand,time):

        self.prior_variance=0*np.identity(DEMAND_NUM)
        variance_measured=0*np.identity(DEMAND_NUM)
        for i in range(DEMAND_NUM):
            variance_measured[i][i]=MEASURED_DEMAND_STD[i]**2

        inv_variance_measured=np.linalg.pinv(variance_measured)
        inv_variance_predict=np.linalg.pinv(self.pred_variance)

        self.prior_variance=np.linalg.pinv(inv_variance_measured+inv_variance_predict)

        priorValue=[]
        measured_value=Measured_Demand.loc[time].values.tolist()[0:DEMAND_NUM]

        mean_measured=np.array(measured_value).reshape(DEMAND_NUM,1)
        mean_predict=np.array(self.pred_values).reshape(DEMAND_NUM,1)

        priorValue=inv_variance_measured.dot(mean_measured)+inv_variance_predict.dot(mean_predict)
        priorValue=self.prior_variance.dot(priorValue)
        self.prior_values=priorValue

    def updatePriorVariance(self,Measured_Demand,time):
        measured_value=Measured_Demand.loc[time]
        self.prior_variance=[0]*DEMAND_NUM
        for i in range(DEMAND_NUM):
            variance_measured=MEASURED_DEMAND_STD[i]**2
            variance_predict=self.pred_variance[i]
            self.prior_variance[i]=(variance_measured* variance_predict)/(variance_measured+ variance_predict)


def generatePriorDist():
    PriorDist=priorDistributon()
    PriorDist.pred_values=0
    PriorDist.pred_variance=0
    PriorDist.prior_values=0
    PriorDist.prior_variance=100
    PriorDist.node_id=[]
    errcode=et.ENopen(Inp,"BUFF.rpt","")
    for i in range(DEMAND_NUM):
        [errcode,id]=et.ENgetnodeid(i+1)
        PriorDist.node_id.append(id)
    errcode=et.ENclose()

    return PriorDist

def generateInputFile(measured,prior):
    fp=open(InputData,mode='w')

    fp.writelines('[TANK]\n')
    for id in ResID:
        string=id+'\t'+str(measured.Data['Res'][id])+'\t'+str(measured.R['Res'][id]**0.5)+'\n'
        fp.writelines(string)

    fp.writelines('[JUNCTIONS]\n')
    for id in PreID:
        string=id+'\t'+str(measured.Data['P'][id])+'\t'+str(measured.R['P'][id]**0.5)+'\n'
        fp.writelines(string)

    fp.writelines('[PIPES]\n')
    for id in FloID:
        string=id+'\t'+str(measured.Data['F'][id])+'\t'+str(measured.R['F'][id]**0.5)+'\n'
        fp.writelines(string)

    fp.writelines('[JUNDEMANDS]\n')
    for i in range(DEMAND_NUM):
        id=prior.node_id[i]
        value=prior.prior_values[i][0]
        variance=prior.prior_variance[i][i]
        string=id+'\t'+str(value)+'\t'+str(variance**0.5)+'\n'
        fp.writelines(string)

    fp.close()