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

# encountersDataset = defaultdict(lambda:None)
# ## Load encounters
# for entry in os.scandir(datasetpath + r'/encounters'):
#     if entry.path.endswith(".json") and entry.is_file():
#         with open(entry, "r") as f:
#             encounters = json.load(f)
#             for encounter in encounters["entry"]:
#                 encid = encounter["resource"]["id"]
#                 encdate = encounter["resource"]["period"]["end"]
#                 encountersDataset[encid] = encdate

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
                        # encid = observation["resource"]["context"]["reference"].replace('Encounter/', '')
                        # date = encountersDataset[encid]
                        reference = observation["resource"]["subject"]["reference"].replace('urn:uuid:', '')
                        if not dataset[reference]:
                            dataset[reference] = {'date': date, 'value': value}
                        else:
                            dateold = datetime.datetime.strptime(dataset[reference]["date"], '%Y-%m-%dT%H:%M:%S%z')
                            datenew = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S%z')
                            # print("RECORDED: ", dateold)
                            # print("NEW ENTRY: ", datenew)
                            if datenew > dateold:
                                # print("Overwrite: ", datenew)
                                dataset[reference] = {'date': date, 'value': value}
                                
print("Ready!")
tests = int(input())
maxQueries = 0
fin = False
fakePatients = []
gleft = []
gright = []

def findFake(g, sus): 
    global fin
    global fakePatients
    global maxQueries
    global gleft
    global gright
    #print(maxQueries)
    ## Base cases
    glen = len(g)
    #if maxQueries <= 0:
        #fin = True ; return
    if fin or maxQueries <= 0:
        return
    if glen <= 3: ## Find patient in the smaller zones
        if glen == 2:
            if sus == 2:
                fakePatients = g
            else:
                maxQueries -= 1
                print('Q', 1, 1, g[0][0], g[1][0])
                response = input()
                if response == "FINISH":
                    fin = True ; return
                if response == "LEFT":
                    fakePatients.append(g[0])
                elif response == "RIGHT":
                    fakePatients.append(g[1])
        elif glen == 3:
            maxQueries -= 1
            print('Q', 1, 1, g[0][0], g[1][0])
            response = input()
            if response == "FINISH":
                fin = True ; return
            if response == "LEFT":
                if sus == 1:
                    fakePatients.append(g[0])
                else:
                    fakePatients.append(g[0])
                    fakePatients.append(g[2])
            elif response == "RIGHT":
                if sus == 1:
                    fakePatients.append(g[1])
                else:
                    fakePatients.append(g[1])
                    fakePatients.append(g[2])
            elif sus == 2:
                fakePatients.append(g[0])
                fakePatients.append(g[1])
            else:
                fakePatients.append(g[2])
        return
    
    ## Start recursion
    middleIndex = int(glen / 2)
    gleft = [g[index] for index in range(middleIndex)]
    gright = [g[index] for index in range(middleIndex, glen)]
    
    leftlen = len(gleft)
    rightlen = len(gright)
    patientStorage = None
    ## CANNOT HAVE UNEVEN PATIENTS ON L R if sus == 2
    if sus == 2:
        if rightlen > leftlen:
            patientStorage = gright.pop(0)
            rightlen -= 1
    
    # leftPatients = [gleft[index][0] for index in range(leftlen)]
    # rightPatients = [gright[index][0] for index in range(rightlen)]
    leftPatients = ""
    rightPatients = ""
    for pat in gright:
        rightPatients += pat[0] + " "
    for pat in gleft:
        leftPatients += pat[0] + " "
    rightPatients.strip()
    leftPatients.strip()
    print('Q', leftlen, rightlen, leftPatients, rightPatients)
    response = input()
    maxQueries -= 1
    if response != "FINISH" and response != "LEFT" and response != "RIGHT" and response != "EQUAL":
        raise TypeError("failed to read judge")
    if response == "FINISH":
        fin = True ; return
    
    ## Deal with patient taken out to make even query
    if patientStorage is not None:
        if response == "LEFT":
            gleft.append(patientStorage)
            findFake(gleft, 2)
        elif response == "RIGHT":
            gright.append(patientStorage)
            findFake(gright, 2)
    else:
        if response == "LEFT":
            if sus == 2:
                findFake(gleft, 2)
            else:
                findFake(gleft, 1)
        elif response == "RIGHT":
            if sus == 2:
                findFake(gright, 2)
            else:
                findFake(gright, 1)
    if response == "EQUAL":
        findFake(gleft, 1)
        findFake(gright, 1)
        
for x in range(tests):
    fakePatients = []
    fin = False
    lr = input().split()
    l = float(lr[0])
    r = float(lr[1])
    ## Add patients with values between LR to a list
    group = [] #group[][] [0]=patient ID [1]=value
    
    for patient in dataset:
        entry = dataset[patient]
        value = float(entry["value"])
        if value > r or value < l:
            continue
        group.append([patient,value])
    p = len(group)
    
    maxQueries = int(math.log(((p*(p-1)) / 2), 3)) + 3
    
    findFake(group, 2)
    
    #print(fakePatients)
    patlen = len(fakePatients)
    if not fin and patlen >= 2:
            print('A', fakePatients[0][0], fakePatients[1][0])
    else:
        for i in range(2-patlen):
            fakePatients.append(gright[i])
        print('A',fakePatients[0][0], fakePatients[1][0]) ## Print some random stuff if fake patients list is not 2
   