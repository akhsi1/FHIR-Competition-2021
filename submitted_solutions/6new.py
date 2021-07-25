# -*- coding: utf-8 -*-
"""
Created on Sat Jul  3 15:48:57 2021

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
                    if coding["code"] == '718-7':
                        ## Add all Hemoglobin Volume observations to dataset
                        value = observation["resource"]["valueQuantity"]["value"]
                        date = observation["resource"]["effectiveDateTime"]
                        # date = encountersDataset[encid]
                        reference = observation["resource"]["subject"]["reference"].replace('urn:uuid:', '')
                        if not dataset[reference]:
                            dataset[reference] = {'date': date, 'value': value}
                        else:
                            dateold = datetime.datetime.strptime(dataset[reference]["date"], '%Y-%m-%dT%H:%M:%S%z')
                            datenew = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S%z')
                            if datenew > dateold:
                                dataset[reference] = {'date': date, 'value': value}
                                
print("Ready!")
tests = int(input())
maxQueries = 0
fin = False
fakePatients = []
remainingPool = []

def findTwo(g):
    global fin
    global fakePatients
    global maxQueries
    global remainingPool
    glen = len(g)
    print(g)
    
    if fin or maxQueries <= 1:
        remainingPool = g
        return
    
    if glen <= 3: ## Find patient in the smaller zones
        if glen == 2:
            fakePatients = g
        elif glen == 3:
            maxQueries -= 1
            print('Q', 1, 1, g[0], g[1])
            response = input()
            if response == "FINISH":
                fin = True
                return
            if response == "LEFT":
                fakePatients.append(g[0])
                fakePatients.append(g[2])
            elif response == "RIGHT":
                fakePatients.append(g[1])
                fakePatients.append(g[2])
            elif response == "EQUAL":
                fakePatients.append(g[0])
                fakePatients.append(g[1])
        return
    else:
        ## Start algo
        middleIndex = int(glen / 2)
        gleft = [g[index] for index in range(middleIndex)]
        gright = [g[index] for index in range(middleIndex, glen)]
        
        leftlen = len(gleft)
        rightlen = len(gright)
        patientStorage = None
        
        ## CANNOT HAVE UNEVEN PATIENTS ON L R if TWO FAKES
        leftPatients = ""
        rightPatients = ""
        if rightlen > leftlen:
            patientStorage = gright.pop(0)
            rightlen -= 1
        for pat in gright:
            rightPatients += pat + " "
        for pat in gleft:
            leftPatients += pat + " "
        rightPatients.strip()
        leftPatients.strip()
        print('Q', leftlen, rightlen, leftPatients, rightPatients)
        response = input()
        maxQueries -= 1
        if response != "FINISH" and response != "LEFT" and response != "RIGHT" and response != "EQUAL":
            raise ValueError("failed to read judge")
        if response == "FINISH":
            fin = True
            return
        
        ## Deal with patient taken out to make even query
        if patientStorage is not None:
            if response == "LEFT":
                gleft.append(patientStorage)
            elif response == "RIGHT":
                gright.append(patientStorage)
        if response == "LEFT":
                findTwo(gleft)
        elif response == "RIGHT":
                findTwo(gright)
        elif response == "EQUAL": # Find based on one fake 
            findOne(gleft)
            findOne(gright)
    
def findOne(g):
    global fin
    global fakePatients
    global maxQueries
    global remainingPool
    glen = len(g)
    print(glen)
    print(g)
    
    if fin or maxQueries <= 1:
        remainingPool = g
        return
    
    if glen <= 3: ## Find patient in the smaller zones
        if glen == 1:
            fakePatients.append(g[0])
            return
        maxQueries -= 1
        print('Q', 1, 1, g[0], g[1])
        response = input()
        if response == "FINISH":
            fin = True
            return
            
        if glen == 2:
            if response == "LEFT":
                fakePatients.append(g[0])
            elif response == "RIGHT":
                fakePatients.append(g[1])
        if glen == 3:
            if response == "LEFT":
                fakePatients.append(g[0])
            elif response == "RIGHT":
                fakePatients.append(g[1])
            elif response == "EQUAL":
                fakePatients.append(g[2])
        return
    ## Start algo
    else:
        aThird = int(round(glen/3))
        gleft = []
        gright = []
        gStorage = []
        for index in range(glen):
            if index < aThird:
                gleft.append(g[index])
            elif index < aThird*2:
                gright.append(g[index])
            else:
                gStorage.append(g[index])
        leftPatients = ""
        rightPatients = ""
        for pat in gright:
            rightPatients += pat + " "
        for pat in gleft:
            leftPatients += pat + " "
        rightPatients.strip()
        leftPatients.strip()
        print('Q', len(gleft), len(gright), leftPatients, rightPatients)
        response = input()
        maxQueries -= 1
        if response == "FINISH":
            fin = True
            return
        if response == "LEFT":
            findOne(gleft)
        elif response == "RIGHT":
            findOne(gright)
        elif response == "EQUAL":
            findOne(gStorage)
            
for x in range(tests):
    fakePatients = []
    remainingPool = []
    fin = False
    lr = input().split()
    l = float(lr[0])
    r = float(lr[1])
    ## Add patients with values between LR to a list
    group = [] 
    realBlood = None
    for patient in dataset:
        entry = dataset[patient]
        value = float(entry["value"])
        if (value > r or value < l) and realBlood is None:
            realBlood = patient
            continue
        group.append(patient)
    p = len(group)
    
    maxQueries = int(math.log(((p*(p-1)) / 2), 3)) + 3
    
    ## Find Two
    findTwo(group)
    
    patlen = len(fakePatients)
    if not fin and patlen >= 2:
        print('A', fakePatients[0], fakePatients[1])
        print(fakePatients)
    elif not fin:
        for pat in remainingPool:
            fakePatients.append(pat)
        print('A',fakePatients[0], fakePatients[1]) ## Print from remaining pool if patients is not equal to 2