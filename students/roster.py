# TODO
from cs50 import SQL
import csv
from sys import argv

if len(argv) != 2:
    print("Two arguments only")
    exit

house = argv[1]

db = SQL("sqlite:///students.db")

roster = db.execute("SELECT first, last, middle, birth FROM students WHERE house = ? ORDER BY last, first", house)

for i in range(len(roster)):
    if roster[i]['middle'] == "":
        firstlast = "{} {}, born {}"
        print(firstlast.format(roster[i]['first'], roster[i]['last'], roster[i]['birth']))
    else:
        firstlast = "{} {} {}, born {}"
        print(firstlast.format(roster[i]['first'], roster[i]['middle'], roster[i]['last'], roster[i]['birth']))

#print(roster)