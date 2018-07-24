import datetime
from openpyxl import Workbook
from openpyxl import load_workbook
from jira import JIRA
import numpy as np
import os
import time 

#---------------------------------------------------------------
def find_HLS_duplicates(HLS):
    lines = len(HLS)
    print(lines)
    for i in range(0,lines,1):
        if str(HLS[i][3]) != '':
            for j in range((i+1),lines,1):
                if str(HLS[j][3]) != '':
                    str1 = str(HLS[i][3])
                    str1 = str1.upper()
                    str2 = str(HLS[j][3])
                    str2 = str2.upper()
                    if str1 == str2:
                        print(HLS[j][3], "is duplicate")
                        HLS[i].append('')
                        HLS[j].append('')

                        HLS[i][4] = "Duplicate on file"
                        HLS[j][4] = "Duplicate on file"
    return HLS
#---------------------------------------------------------------
def find_TotalData_duplicates(TotalData):
    lines = len(TotalData)
    print(lines)
    for i in range(0,lines,1):
        if str(TotalData[i][3]) != '':
            for j in range((i+1),lines,1):
                if str(TotalData[j][3]) != '':
                    str1 = str(TotalData[i][3])
                    str1 = str1.upper()
                    str2 = str(TotalData[j][3])
                    str2 = str2.upper()
                    if str1 == str2:
                        print(TotalData[j][3], "is duplicate")
                        TotalData[i].append('')
                        TotalData[j].append('')

                        TotalData[i][4] = "Duplicate on file"
                        TotalData[j][4] = "Duplicate on file"
    return TotalData
def ReadVDD(newVDDpath):
    wb = load_workbook(filename = newVDDpath)


    return wb