# -*- coding: utf-8 -*-
"""
Created on Mon Jun 28 18:22:44 2021

@author: akhsi
"""

import os
import json
from collections import defaultdict
import datetime
from decimal import Decimal
from fractions import Fraction


datasetpath = input()
datasetpath = r'D:\Desktop\FHIR Competition\sample_dataset\build'

dataset = defaultdict(lambda: None)

## Load dataset for observations
for entry in os.scandir(datasetpath + r'/observations'):
    if entry.path.endswith(".json") and entry.is_file():
        with open(entry, "r") as f:
            observations = json.load(f)
            PMVCode = '32623-1'
            for observation in observations["entry"]:
                for coding in observation["resource"]["code"]["coding"]:
                    if coding["code"] == PMVCode:
                        ## Add all PMV observations to dataset
                        value = observation["resource"]["valueQuantity"]["value"]
                        date = observation["resource"]["effectiveDateTime"]
                        reference = observation["resource"]["subject"]["reference"].replace('urn:uuid:', '')
                        if not dataset[reference]:
                            dataset[reference] = {'date': date, 'PMV': value}
                        else:
                            dateold = datetime.datetime.strptime(dataset[reference]["date"], '%Y-%m-%dT%H:%M:%S%z')
                            datenew = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S%z')
                            if datenew > dateold:
                                dataset[reference] = {'date': date, 'PMV': value}
print("Ready!")
tests = int(input())

## Finds minimum distanced subarray of size = n
def findMinSubarray(pmvlist, n, patients):
    mindiff = Decimal(99999999)
    
    for i in range(patients):
        rangediff = Decimal(pmvlist[i+n] - pmvlist[i])
        mindiff = Decimal(min(rangediff, mindiff))
        
        if i+1 + n > patients-1:
            break
    return mindiff
            

## Loop through each test case
for x in range(tests):
    line = input().split()
    patients = int(line[1])
    nVal = float(line[0])
    ## PMV = Platelet Mean Volume
    plist = []
    ## Loop through each patient and add PMV values to a sorted list
    for j in range(0, patients):
        patientId = line[j+2]
        plist.append(dataset[patientId]["PMV"])
    pmvlist = sorted(plist, key=float)
    
    ## Algorithm to find maximum number of patients who can take the vaccine
    count = patients-1
    while True:
        mindiff = float(findMinSubarray(pmvlist, count, patients))
        pr = Fraction((mindiff)**2 / (30*nVal))
        if pr == 0:
            print(0)
            break
        # print("######")
        # print("pr: ", pr)
        # print("pr: ", (mindiff)**2 / (30*nVal))
        # print("Peoples: ", 3/((mindiff)**2 / (30*nVal)))
        # print("MIN DIFFERENCE: ", mindiff)
        # print("People tested: ", count+1)
        # print("min index:", minIndex)
        
        if 3/pr >= count:
            print(count+1)
            break
        count-=1
        if(count < 0):
            print(0)
            break


