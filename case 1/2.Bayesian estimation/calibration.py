import win32event
import win32process


def WDS_Calibration(exePath,inpfile,inputdata,resultInp):
    param = inpfile+" "+inputdata+" "+resultInp#空格区分参数
    handle = win32process.CreateProcess(exePath,
    param, None , None , 0 ,win32process. CREATE_NO_WINDOW ,
     None , None ,    win32process.STARTUPINFO())
    data=win32event.WaitForSingleObject(handle[0], -1)
    print('calibration over')

