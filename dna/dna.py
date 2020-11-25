import csv
from sys import argv
import sys

with open(argv[1]) as f:
    reader = csv.reader(f)
    headers = next(reader)
    headers.remove('name')

    headcount = 0
    for row in reader:
        headcount += 1

with open (argv[2], "r") as sequence:
    dna = sequence.read()
    #print(dna, end = "")

dnadict = { z : 0 for z in headers }


def check(j, i):

    run = 0
    subset = dna[j :]

    while True:
        for x in range(len(dna)):
            if subset[x * seq : (x * seq ) + seq] == headers[i]:
                #print(subset[x * seq : (x * seq ) + seq])
                run += 1
            else:
                #print(subset[x * seq : (x * seq ) + seq])
                return run

#For every STR
for i in range(len(headers)):
    seq = len(headers[i])
    #Check each letter in DNA
    for j in range(len(dna)):
        #If a sequence matches an STR
        if dna[j : j+seq] == headers[i]:
            #Check how long it repeats for
            run = check(j, i)
            if run > dnadict[headers[i]]:
                dnadict[headers[i]] = run

#Compare DNA
def dnascan(person_num, seq_num):

    person_name = list_of_rows[person_num][0]
    STR_name = list_of_rows[0][seq_num]

    dna_count = int(list_of_rows[person_num][seq_num])

    if dna_count == dnadict[STR_name]:
        #print("MATCH")
        if seq_num == len(headers):
            print(person_name)
            sys.exit()
        else:
            dnascan(person_num, seq_num + 1)
    return False

found = False

with open(argv[1]) as f:
    reader = csv.reader(f)

    list_of_rows = list(reader)
    #For every person in the CSV file
    for i in range(len(list_of_rows)):
        if i > 0:
            found = dnascan(i, 1)
    #print(list_of_rows[1])

#print(found)
if found == False:
    print("No Match")
#print(headers)
#print(dnadict)