# -*- coding: utf-8 -*-
"""
Created on Fri Jul  2 10:54:10 2021

@author: akhsi
"""

import os
import json
from collections import defaultdict
import datetime

datasetpath = input()
datasetpath = r'D:\Desktop\FHIR Competition\sample_dataset\build'

encountersDataset = defaultdict(lambda:None)
## Load encounters
for entry in os.scandir(datasetpath + r'/encounters'):
    if entry.path.endswith(".json") and entry.is_file():
        with open(entry, "r") as f:
            encounters = json.load(f)
            for encounter in encounters["entry"]:
                encid = encounter["resource"]["id"]
                encdate = encounter["resource"]["period"]["end"]
                encountersDataset[encid] = encdate

dataset = defaultdict(lambda: None)
## Load dataset for observations
for entry in os.scandir(datasetpath + r'/observations'):
    if entry.path.endswith(".json") and entry.is_file():
        with open(entry, "r") as f:
            observations = json.load(f)
            for observation in observations["entry"]:
                for coding in observation["resource"]["code"]["coding"]:
                    if coding["code"] == '29463-7':
                        ## Add all Weight observations to dataset
                        value = observation["resource"]["valueQuantity"]["value"]
                        # date = observation["resource"]["effectiveDateTime"]
                        encid = observation["resource"]["context"]["reference"].replace('Encounter/', '')
                        date = encountersDataset[encid]
                        reference = observation["resource"]["subject"]["reference"].replace('urn:uuid:', '')
                        if not dataset[reference]:
                            dataset[reference] = {'date': date, 'weight': value}
                        else:
                            dateold = datetime.datetime.strptime(dataset[reference]["date"], '%Y-%m-%dT%H:%M:%S%z')
                            datenew = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S%z')
                            # print("RECORDED: ", dateold)
                            # print("NEW ENTRY: ", datenew)
                            if datenew > dateold:
                                # print("Overwrite: ", datenew)
                                dataset[reference] = {'date': date, 'weight': value}
                                
print("Ready!")
tests = int(input())

for x in range(tests):
    lr = input().split()
    l = float(lr[0])
    r = float(lr[1])
    ## Add patients with weight values between LR to a sorted list by weight
    group = [] #group[][] [0]=weight [1]=patient ID
    for patient in dataset:
        entry = dataset[patient]
        value = float(entry["weight"])
        if value > r or value < l:
            continue
        group.append([value, patient])
    group = sorted(group, key=lambda x:x[0])
    glen = len(group)
    #print(group)
    
    testPatient = group[0][1]
    ## Find Correct Machine Outputs (correctOutputs.size = 7)
    correctOutputs = [] # SAFE/DANGEROUS
    for i in range(7):
        print('Q', testPatient) ## always DANGEROUS
        response = input()
        if response == "SAFE":
            correctOutputs.append("DANGEROUS")
        else:
            correctOutputs.append("SAFE")
    ## Binary search for patient inside the range: SAFE = go left, DANGEROUS = go right
    #print(correctOutputs)
    remainingDays = []
    for days in range(23):
        remainingDays.append(correctOutputs[days%7])
    # print(remainingDays)
    
    curIndex = int((glen-1)/2)
    minIndex = 0
    maxIndex = glen-1
    results = [None]*glen
    for index in range(23):
        ## On first loop, process first and last index
        if index == 0:
            results[minIndex] = "DANGEROUS"
            ## Check Max
            print('Q', group[maxIndex][1])
            response = input()
            day = remainingDays.pop(0)
            ratInfested = True if day == "DANGEROUS" else False
            if (response == "DANGEROUS" and ratInfested == False) or (response == "SAFE" and ratInfested == True):
                results[maxIndex] = "DANGEROUS"
                print('A', group[maxIndex][1])
                break
            else:
                results[maxIndex] = "SAFE"
                
        ## Check Current Index
        print('Q', group[curIndex][1])
        response = input()
        if not remainingDays:
            break
        day = remainingDays.pop(0)
        ratInfested = True if day == "DANGEROUS" else False
        safe = bool()
        if response == "FINISHED":
            break
        elif (response == "DANGEROUS" and ratInfested == False) or (response == "SAFE" and ratInfested == True):
            results[curIndex] = "DANGEROUS"
            safe = False
        else: ## (response == "SAFE" and ratInfested == True) or (response == "DANGEROUS" and ratInfested == False):
            results[curIndex] = "SAFE"
            safe = True
        
        if curIndex-1 == minIndex:
            if results[curIndex] == "SAFE":
                print('A', group[minIndex][1])
                break
        if curIndex+1 == maxIndex:
            if results[maxIndex] == "DANGEROUS":
                print('A', group[maxIndex][1])
                break
            else:
                print('A', group[curIndex][1])
                break
        if safe: ## Search left if safe
            maxIndex = curIndex
        else: ## if dangerous, search right
            minIndex = curIndex
        curIndex = minIndex + int((maxIndex - minIndex) / 2)
    #print(results)