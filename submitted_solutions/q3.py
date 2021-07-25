# -*- coding: utf-8 -*-
"""
Created on Wed Jun 30 22:56:16 2021

@author: akhsi
"""

import os
import json
from collections import defaultdict
import datetime
import math

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
                    if coding["code"] == '8302-2':
                        ## Add all Height observations to dataset
                        value = observation["resource"]["valueQuantity"]["value"]
                        date = observation["resource"]["effectiveDateTime"]
                        reference = observation["resource"]["subject"]["reference"].replace('urn:uuid:', '')
                        if not dataset[reference]:
                            dataset[reference] = {'date': date, 'height': value}
                        else:
                            dateold = datetime.datetime.strptime(dataset[reference]["date"], '%Y-%m-%dT%H:%M:%S%z')
                            datenew = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S%z')
                            if datenew > dateold:
                                dataset[reference] = {'date': date, 'height': value}
## Returns 2D list of groups
def findMinC(group, n, d, length):
    n -= 1 ## n = people in each group, -1 for indexing purpose
    breaknext = False
    total = 0
    minTotal = 0
    runningPositive = [None] * 2
    runningCount = 0
    groups = [] # stores the groups of heights 1 group = 1 generalisation 
    i = 0
    while True:
        if i + n > length-1: ## if remaining in group is less than n, add to current
            n = length-1 - i
            breaknext = True
        if i + n - length-1 == 1: ## if remaining in group = 1, add to current
            n += 1
            breaknext = True
        p1 = group[i]
        p2 = group[i+n]
        ha = p1[0]
        hb = p2[0]
        # print(group[i][1], group[i+n][1])
        # print(ha, hb)
        c = math.log(abs(ha-hb)/(d*n))
        
        if c > 0:
            if runningPositive[0] is None:
                runningPositive[0] = p1
                runningCount += 1
            runningPositive[1] = p2
            runningCount += n
        else:
            if runningPositive[0] is not None:
                prevc = math.log(abs(runningPositive[0][0] - runningPositive[1][0]) / (d*runningCount))
                total += prevc
                groups.append([runningPositive[0], runningPositive[1]])
            minTotal += c
            total += c
            runningPositive[0] = None
            runningCount = 0
            groups.append([p1, p2])
        
        if breaknext or (i+n >= length-1):
            if runningPositive[0] is not None:
                prevc = math.log(abs(runningPositive[0][0] - runningPositive[1][0]) / (d*runningCount))
                total += prevc
                groups.append([runningPositive[0], runningPositive[1]])
            break
        i += n
        
    # print("n = ", n)
    # print("running count = ", runningCount)
    # print("pos ha = ", runningPositive[0])
    # print("pos hb = ", runningPositive[1])
    # print("min total = ", minTotal)
    # print("total = ", total)
    # print("groups = ", groups)
    return [total, groups]

print("Ready!")
tests = int(input())
for x in range(tests):
    line = input().split()
    d = float(line[0])
    plength = int(line[1])
    patients = input().split()
    ## Fill List
    group = [] #group[][] [0] = height [1] = patient ID
    for patient in patients:
        entry = dataset[patient]
        value = entry["height"]
        group.append([value, patient])
    group = sorted(group, key=lambda x:x[0], reverse = True)
    
    bestGroup = None
    bestIndex = 0
    bestSum = float("inf")
    
    for i in range(2, int(plength/2)):
        result = findMinC(group, i, d, plength)
        cSum = result[0]
        if cSum < bestSum:
            bestIndex = i
            bestSum = cSum
            bestGroup = result[1]
    print(len(bestGroup))
    for g in bestGroup:
        print(g[0][1], g[1][1])
    
    ## Find C in 2 generalizations
    # ha = group[0][0]
    # hb = group[plength-1][0]
    # n = plength
    # c = math.log(abs(ha-hb)/(d*n))
    # print(2)
    # middleindex = int(plength/2)
    # print(group[0][1], group[middleindex][1])
    # print(group[middleindex][1], group[plength-1][1])
    #print(c)
    # numrequired = int(1/d) + 1
    ## Formula c = math.log(abs(ha-hb)/(d*n))
        
    # print("d = ", d)
    # print(group)
    
