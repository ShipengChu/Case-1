import numpy as np
import pandas as pd
import copy
from Sensors import *
from global_variable import *

from priorDistribution import *
from epanet import *
from calibration import *
from outPut import *

#read the data

Measured_Demand=pd.read_csv(PATH+'\\measuredDemand.csv')
Res_Sensor=pd.read_csv(PATH+'\\measuredRes.csv')
Pressure_Sensor=pd.read_csv(PATH+'\\measuredPressure.csv')
Folw_Sensor=pd.read_csv(PATH+'\\measuredFlow.csv')

Measured_Demand.set_index(["time"], inplace=True)
Res_Sensor.set_index(["time"], inplace=True)
Pressure_Sensor.set_index(["time"], inplace=True)
Folw_Sensor.set_index(["time"], inplace=True)
#initial the Measurements and particles

MeaData=sensor_initial()
result_previous=generateEstimateDemandResult()
priorDist=generatePriorDist()

for time in range(SIM_TIME):

    print('time:'+str(time))
    ##update measurements
    MeaData.updateMeasured(Res_Sensor,Pressure_Sensor,Folw_Sensor,time)        #save the real time measurement to the class sensor
    ##update prior distribution
    priorDist.predictUpdate(result_previous)
    priorDist.updatePrior(Measured_Demand,time)

#start calibration

    generateInputFile(MeaData,priorDist)#更新input data
    WDS_Calibration(exePath,Inp,InputData,ResultInp)#最大化step 1

#summary result
    SUMMARY_R.append(copy.deepcopy(MeaData))

    result_previous.time=time
    result_previous.updateResult(ResultInp)
    result_previous.readDemandVariance(DemandVariance)
    result_previous.measuredResid(MeaData)
    SUMMARY_RESULT.append(copy.deepcopy(result_previous))

#    print('Measurement std:'+str(MeaData.R**0.5))
    print('Resid_Measured:'+str(result_previous.cali_resid))
    print('#############################################')
    if(time%100==0):
        try:
            outPutCalibrated(SUMMARY_RESULT)
            outPutMeasured(SUMMARY_R)
        except:
            print('error')
outPutCalibrated(SUMMARY_RESULT)
outPutMeasured(SUMMARY_R)



