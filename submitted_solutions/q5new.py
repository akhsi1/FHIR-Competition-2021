import os
import json
from collections import defaultdict
import datetime
from fractions import Fraction

## Main
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

## Finds minimum sized subarray of size = n
def findMinSubarray(pmvlist, n, patients):
    mindiff = float("inf")
    
    for i in range(patients):
        rangediff = pmvlist[i+n] - pmvlist[i]
        mindiff = min(rangediff, mindiff)
        
        if i+1 + n > patients-1:
            break
    return mindiff
            

## Loop through each group of patients
for x in range(tests):
    line = input().split()
    nVal = int(line[0])
    patients = int(line[1])
    
    ## PMV = Platelet Mean Volume
    maxPMV = 0
    minPMV = float("inf")
    
    plist = []
    ## Loop through each patient and add PMV values to a sorted list
    for j in range(0, patients):
        patientId = line[j+2]
        plist.append(dataset[patientId]["PMV"])
    pmvlist = sorted(plist, key=float)
    
    ## Algorithm to find maximum number of patients who can take the vaccine
    count = patients-1
    while True:
        
        mindiff = findMinSubarray(pmvlist, count, patients)
        
        # minPMV = pmvlist[startingIndex]
        # maxPMV = pmvlist[startingIndex + x]
        pr = Fraction((mindiff)**2 / (30*nVal))
        # print(count)
        # print("pr: ", pr)
        # print("ppls <3: ", 3/pr)
        if pr*(count+1) <= 3:
            print(count+2)
            break
        # if 3/pr > count :
        #     print(count+1)
        #     # print("pr: ", pr)
        #     # print("ppls <3: ", 3/pr)
        #     break
        count-=1