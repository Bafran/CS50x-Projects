# TODO
from cs50 import SQL
import csv
from sys import argv

if len(argv) != 2:
    print("Two arguments only")
    exit

db = SQL("sqlite:///students.db")

with open(argv[1], "r") as students:
    
    reader = csv.DictReader(students)
    
    for row in reader:
        
        name = row['name'].split()
        first = name[0]
        middle = ""
        last = ""
        
        if len(name) == 2:
            last = name[1]
        elif len(name) == 3:
            middle = name[1]
            last = name[2]
        
        house = row['house']
        birth = row['birth']
        
        db.execute("INSERT INTO students (first, middle, last, house, birth) VALUES(?, ?, ?, ?, ?)", first, middle, last, house, birth)
        