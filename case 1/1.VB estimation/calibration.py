import win32event
import win32process


def WDS_Calibration(exePath,inpfile,inputdata,resultInp):
    inf=win32process.STARTUPINFO()
    inf.wShowWindow=1
    param = inpfile+" "+inputdata+" "+resultInp#空格区分参数
    handle = win32process.CreateProcess(exePath,
    param, None , None , 0 ,win32process. CREATE_NO_WINDOW ,
     None , None ,   inf)
    data=win32event.WaitForSingleObject(handle[0], -1)
    print('calibration over')

