#!/usr/bin/env python

import json
import os
import requests
import subprocess
import time

from subprocess import Popen, PIPE

ip = "inverter"
imgName = "ethminer.exe"

def getOsTasks(name):
    r = os.popen('tasklist /v').read().strip().split('\n')
    for i in range(len(r)):
        if name in r[i]:
            return r[i]
    return []

def getIverterData(hostname, dataRequest):
    try:
        url = "http://" + hostname + dataRequest
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.Timeout: # inverter off
        print("Request: {} failed".format(url))
    except requests.exceptions.RequestException as e:
        print("Request failed with {}".format(e))
        
def getPowerFlowRealtimeData():
    dataRq = '/solar_api/v1/GetPowerFlowRealtimeData.fcgi'
    return getIverterData(ip, dataRq)

def prepareMsiAfterburner():
    subprocess.run([
        "C:\Program Files (x86)\MSI Afterburner\MSIAfterburner.exe",
        "-Profile1"
    ])

def restoreMsiAfterburner():
    subprocess.run([
        "C:\Program Files (x86)\MSI Afterburner\MSIAfterburner.exe",
        "-Profile2"
    ])

def stopProcess():
    os.system("taskkill /im " + imgName + " /F")

def main():
    data = getPowerFlowRealtimeData()
    
    if data == None:
        return
    
    wattage = data['Body']['Data']['Inverters']['1']['P']

    # handle error
    r = getOsTasks(imgName)

    if wattage > 200:
        if r:
            exit()        

        subprocess.run([
            "C:\Program Files\ethminer\ethminer.exe",
            "--farm-recheck",
            "200",
            "-U",
            "-P",
            "stratum://0x5F60Ed141133BA91b68f4bBfFD2E0dbd686Fa387.miner:" + 
            "m3ntalsp00n@asia1.ethermine.org:4444"
        ])
    else: # less than 200
        if r:
            stopProcess()

if __name__ == "__main__":
    main() 