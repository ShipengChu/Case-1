import numpy as np
import pandas as pd
import os
#define the GLOBAL variable
PATH=os.path.abspath('.')+'\\data files_3_1'
#define particle parameters
SIM_TIME=1500
VB_ITERS=2
#define the hyd_demand
DEMAND_NUM=8   #Number of nodal water demands
SENSOR_NUM=4#6
Number_PIPES=11
#define std
SCALE_Predict=1
#DEMAND_PREDICT_STD=[0.4*SCALE_Predict,0.53*SCALE_Predict,1.47*SCALE_Predict,0.13*SCALE_Predict,0.93*SCALE_Predict,0.8*SCALE_Predict,0.93*SCALE_Predict,1.47*SCALE_Predict]  #absult value,这个就是该概念，用来调整相对大小

DEMAND_PREDICT_STD=[1.5]*8  #absult value,这个就是该概念，用来调整相对大小
SCALE_Measured=1.5
MEASURED_DEMAND_STD=[0.4*SCALE_Measured,0.53*SCALE_Measured,1.47*SCALE_Measured,0.13*SCALE_Measured,0.93*SCALE_Measured,0.8*SCALE_Measured,0.93*SCALE_Measured,1.47*SCALE_Measured]#absult value
average_demand=6.25

#define IW patamerer
Sensor_T=0.99
Sensor_B=Sensor_T*np.identity(SENSOR_NUM)
#define the sensor id
ResID=['N9']
PreID=['N3','N5','N7']
#FloID=['L4','L10']
FloID=[]
TOTAL_SENSOR_ID=ResID+PreID+FloID
#define the calibration file
Inp='case_1.inp'  # 不能有模式
exePath = "iterative Sh-Mo_CUDA.exe"
InputData='case_1.obs'
ResultInp='result.inp'
DemandVariance='demand_var.csv'
JacobyMat='jacoby.csv'
#define Bayesian calibration outputs


#define the result
SUMMARY_RESULT=[]
SUMMARY_R=[]

