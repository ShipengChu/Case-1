import numpy as np
import pandas as pd
from global_variable import *
import copy

def outPutCalibrated(calibratedResult):
    _measured_calibrated={}
    _demand_calibrated={}
    _demand_vairance_calibrated={}
    _Nodal_Pressure_calibrated={}
    _Pipe_Flow_calibrated={}

    for id in TOTAL_SENSOR_ID:
        _measured_calibrated[id]=[]

    for i in range(DEMAND_NUM):
        _demand_calibrated[i]=[]
        _demand_vairance_calibrated[i]=[]
        _Nodal_Pressure_calibrated[i]=[]

    for i in range(Number_PIPES):
        _Pipe_Flow_calibrated[i]=[]



    for result in calibratedResult:
        for id in TOTAL_SENSOR_ID:
            if id in ResID:
                _measured_calibrated[id].append(result.cali_sensor['Res'][id])
            if id in PreID:
                _measured_calibrated[id].append(result.cali_sensor['P'][id])
            if id in FloID:
                _measured_calibrated[id].append(result.cali_sensor['F'][id])
        for i in range(DEMAND_NUM):
            _demand_calibrated[i].append(result.cali_demand_values[i])
            _demand_vairance_calibrated[i].append(result.cali_demand_variance[i][i])
            _Nodal_Pressure_calibrated[i].append(result.cali_nodal_p[i])
        for i in range(Number_PIPES):
            _Pipe_Flow_calibrated[i].append(result.cali_pipe_f[i])

    pd.DataFrame(_measured_calibrated).to_csv(PATH+'\\Measured_calibrated_B.csv')
    pd.DataFrame(_demand_calibrated).to_csv(PATH+'\\Demand_calibrated_B.csv')
    pd.DataFrame(_demand_vairance_calibrated).to_csv(PATH+'\\Demand_vairance_calibrated_B.csv')
    pd.DataFrame(_Nodal_Pressure_calibrated).to_csv(PATH+'\\Nodal_Pressure_calibrated_B.csv')
    pd.DataFrame(_Pipe_Flow_calibrated).to_csv(PATH+'\\Pipe_Flow_calibrated_B.csv')


def outPutMeasured(meauredResult):
    _measured_STD={}
    for id in TOTAL_SENSOR_ID:
        _measured_STD[id]=[]

    for result in meauredResult:
        for id in TOTAL_SENSOR_ID:
            if id in ResID:
                _measured_STD[id].append(result.R['Res'][id])
            if id in PreID:
                _measured_STD[id].append(result.R['P'][id])
            if id in FloID:
                _measured_STD[id].append(result.R['F'][id])
    pd.DataFrame(_measured_STD).to_csv(PATH+'\\Measured_VAR_B.csv')