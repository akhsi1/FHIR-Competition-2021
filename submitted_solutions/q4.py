# -*- coding: utf-8 -*-
"""
Created on Thu Jul  1 00:34:32 2021

@author: akhsi
########################################################
### Don't try to understand this code. It's a mess. ####
########################################################
"""

import os
import json
from collections import defaultdict
import datetime
import random
from decimal import Decimal

datasetpath = input()
datasetpath = r'D:\Desktop\FHIR Competition\sample_dataset\build'

dataset = defaultdict(lambda: None)

## Load dataset for observations
for entry in os.scandir(datasetpath + r'/observations'):
    if entry.path.endswith(".json") and entry.is_file():
        with open(entry, "r") as f:
            observations = json.load(f)
            for observation in observations["entry"]:
                for coding in observation["resource"]["code"]["coding"]:
                    if coding["code"] == '55284-4':
                        ## Add all Blood Pressure data to dataset
                        patient = observation["resource"]["subject"]["reference"].replace('urn:uuid:', '')
                        db = None
                        sb = None
                        date = observation["resource"]["effectiveDateTime"]
                        for component in observation["resource"]["component"]:
                            if component["code"]["coding"][0]["code"] == '8462-4':
                                db = Decimal(component["valueQuantity"]["value"])
                            if component["code"]["coding"][0]["code"] == '8480-6':
                                sb = Decimal(component["valueQuantity"]["value"])
                        if not dataset[patient]:
                            dataset[patient] = {'date': date, 'db': db, 'sb': sb}
                        else:
                            dateold = datetime.datetime.strptime(dataset[patient]["date"], '%Y-%m-%dT%H:%M:%S%z')
                            datenew = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S%z')
                            if datenew > dateold:
                                dataset[patient] = {'date': date, 'db': db, 'sb': sb}
patientList = defaultdict(lambda:None)
## Returns [0] = Hamming Distance [1..n] = patient IDs
def getBestGroup(patient):
    p = patientList.pop(patient)
    group = []
    group.append(0) ## placeholder for final hamming distance
    group.append(patient)
    db = p["db"]
    sb = p["sb"]
    maxsb = sb
    maxdb = db
    minsb = sb
    mindb = db
    hamCost = 0
    counter = len(patientList)
    patientStorage = defaultdict(lambda:None)
    randomlist = list(patientList.keys())
    for k in list(randomlist):
        if not patientList[k]:
            continue
        pcur = patientList[k]
        dbcur = pcur["db"]
        sbcur = pcur["sb"]
        maxsbcur = max(maxsb, sbcur)
        maxdbcur = max(maxdb, dbcur)
        minsbcur = min(minsb, sbcur)
        mindbcur = min(mindb, dbcur)
        tempHamDist = maxsbcur - minsbcur + maxdbcur - mindbcur
        tempHamCost = tempHamDist**Decimal(1.5)
        
        ## g = (counter/4.5)**2 ## Try and find a nice balance between whether to allow higher ham cost threshold (Only tweaked with max patients = 30)
        g = 0
        if len(group) > 1:
            g = (len(group)-1)*10
        else:
            g = 10
        if tempHamCost < g  or tempHamCost <= hamCost:
            pk = patientList.pop(k)
            patientStorage[k] = pk
            group.append(k)
            maxsb = maxsbcur
            maxdb = maxdbcur
            minsb = minsbcur
            mindb = mindbcur
            hamCost = max(hamCost, tempHamCost)
            group[0] = tempHamDist
        counter-=1
    # hamDist = maxsb - minsb + maxdb - mindb
    # hamCost = hamDist**Decimal(1.5)
    if group[0]**Decimal(1.5) > (len(group)-1)*10:
        patientList.update(patientStorage)
        return [0, patient]
    
    return group

print("Ready!")
tests = int(input())
for x in range(tests):
    patientInput = input().split()
    patientCount = len(patientInput)
    patientList = defaultdict(lambda: None)
    
    for patient in patientInput:
        patientList[patient] = dataset[patient]
    originalList = patientList.copy()
    
    ## Hamming Cost = (maxsb - minsb + maxdb - mindb)**1.5
    ## Find out whether any combination of patients have hamming cost < 10
    bestgroup = []
    minCost = float("inf")
    
    for i in range(50):
        groups = []
        randomlist = list(patientList.keys())
        random.shuffle(randomlist)
        totalCost = 0
        for k in randomlist:
            if patientList[k]:
                result = getBestGroup(k)
                groups.append(result)
                totalCost += 10
                totalCost += result[0]**Decimal(1.5)
        if totalCost < minCost:
            minCost = totalCost
            bestgroup = groups
        patientList = originalList.copy()
            
    ## Output
    print(len(bestgroup))
    for g in bestgroup:
        # patientString = ""
        # glen = len(g)
        # for i in range(1, glen):
        #     patientString += g[i] + " "
        print('C', g[0], 'P', *g)