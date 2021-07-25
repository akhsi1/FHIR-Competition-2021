# -*- coding: utf-8 -*-
"""
Created on Tue Jun 29 14:20:53 2021

@author: akhsi
"""

import os
import json
from collections import defaultdict
import datetime

datasetpath = input()
datasetpath = r'D:\Desktop\FHIR Competition\sample_dataset\build'

bionicEnhancements = defaultdict(lambda: None)

## Load dataset for observations
for entry in os.scandir(datasetpath + r'/observations'):
    if entry.path.endswith(".json") and entry.is_file():
        with open(entry, "r") as f:
            observations = json.load(f)
            for observation in observations["entry"]:
                for coding in observation["resource"]["code"]["coding"]:
                    if coding["code"] == '94235-3':
                        ## Add all Bionic observations to dataset
                        value = observation["resource"]["valueQuantity"]["value"]
                        date = observation["resource"]["effectiveDateTime"] ## Change to Issued date if test case fail
                        patient = observation["resource"]["subject"]["reference"].replace('urn:uuid:', '')
                        if not bionicEnhancements[patient]:
                            bionicEnhancements[patient] = {'date': date, 'value': value}
                        else:
                            dateold = datetime.datetime.strptime(bionicEnhancements[patient]["date"], '%Y-%m-%dT%H:%M:%S%z')
                            datenew = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S%z')
                            if datenew > dateold:
                                bionicEnhancements[patient] = {'date': date, 'value': value}

gpdataset = defaultdict(lambda: None)                       

## Load dataset for patients
for entry in os.scandir(datasetpath + r'/patients'):
    if entry.path.endswith(".json") and entry.is_file():
        with open(entry, "r") as f:
            patients = json.load(f)
            for patient in patients["entry"]:
                patientId = patient["resource"]["id"]
                for gp in patient["resource"]["generalPractitioner"]:
                    gpid = gp["reference"].replace('urn:uuid:', '')
                    if not gpdataset[gpid]:
                        gpdataset[gpid] = [patientId]
                    else:
                        gpdataset[gpid].append(patientId)
print("Ready!")

tests = int(input())

def findDupes(seta, setb):
    dupes = []
    for val in seta:
        if val == "Eye Color Change":
            continue
        tempset.add(value)
    for val in setb:
        if val == "Eye Color Change":
            continue
        if val in tempset:
            dupes.append(val)
    return dupes

## Loop through each test group
for x in range(tests):
    line = input().split()
    nVal = int(line[0]) ## n - number of practitioners
    kVal = int(line[1]) ## k - max number of patients who can be asked to change preferences
    dVal = int(line[2]) ## D - cost per day of running the facility
    cVal = int(line[3]) ## C - cost of asking a patient to change their preference
    line = input().split()
    originalK = kVal
    patients = set()
    practitionersNotFound = 0
    
    for practitionerId in line:
        if gpdataset[practitionerId]:
            ## add patients to dictionary
            for patient in gpdataset[practitionerId]:
                patients.add(patient)
        else:
            practitionersNotFound += 1
    
    requiredBE = []
    
    ## Fill List
    for patient in patients:
        entry = bionicEnhancements[patient]
        dateString = entry["date"]
        value = entry["value"]
        requiredBE.append([dateString, value])
    requiredBE = sorted(requiredBE, key=lambda x:x[0])
    
    length = len(patients)
    
    tempset = set()
    days = 0
    switchCost = 0
    setlist = []
    
    ## Create groups of unique sets (1 group = 1 day)
    for i in range(length):
        value = requiredBE[i][1]
        if value == "Eye Color Change":
            if i == length-1:
                setlist.append(tempset)
                break
            continue
        if value not in tempset:
            tempset.add(value)
        else:
            setlist.append(tempset)
            tempset = set()
            tempset.add(value)
            
    end = False
    while not end:
        x = 1 ## Merge groups with 'x' duplicates by removing a duplicate from setlist
        if x*cVal >= dVal:  ## Don't bother with changing patient preference if cost is higher than daily
            end = True; break
        if kVal < 1: ## Also don't bother with changing patient preference if K is 0
            end = True; break
        setlistSize = len(setlist)
        i = 0
        while i < setlistSize-1:
            tempset = set()
            seta = setlist[i]
            setb = setlist[i+1]
            dupes = findDupes(seta, setb) ## list
            if len(dupes) > x:
                continue
            else:
                for val in dupes:
                    setb.discard(val)
                tempset = setlist.pop(i+1)
                setlist[i].update(tempset)
                kVal -= 1 ## Reduce times patients can change preference
                setlistSize -= 1 ## remember to reduce the setlist size
                i -= 1 ## Check for dupes at current index again
            i += 1
            if kVal < 1:
                end = True; break
        x += 1
        if kVal < x:
            end = True ; break
        
    remaining = len(setlist[len(setlist)-1])
    if remaining <= kVal and remaining*cVal < dVal:
        days -= 1
        
    days += len(setlist)
    switchCost = (originalK - kVal)*cVal
    print(days*dVal + switchCost)
        
    
    # for i in range(length):
    #     value = requiredBE[i][1]
    #     if value not in tempset:
    #         tempset.add(value)
    #     else:
    #         remainingPatients = length-i
    #         print("Remaining Patients: ", remainingPatients)
    #         print("Day: ", days)
    #         if cVal < dVal:
    #             if remainingPatients <= kVal:
    #                 switchCost = remainingPatients * cVal
    #                 break
    #         days += 1
    #         tempset = set()
            
    print("days: ", days)
    print("Cost: ", days*dVal + switchCost)

    print("n, Number of Practitioners: ", nVal)
    print("k, max ppl before: ", originalK)
    print("k, maximum ppl who can change preferences after: ", kVal)
    print("D, Cost per day of running the facility: ", dVal)
    print("C, Cost of asking a patient to change: ", cVal)
    print("Total Number of patients: ", len(patients))
    print("Failed to find: ", practitionersNotFound, " practitioners")
    # print("List of patients preferred Bionic Enhancements: ", requiredBE)
    

