from re import sub
import sqlite3
from time import sleep
from turtle import end_fill
from typing import final
from unicodedata import category
import db_controller
from datetime import datetime
from sqlite3 import Error
import sys
import time
import utils
import pandas as pd
import csv


# COUNT TOTAL OF CAT/SUBCAT IN FILE
def countCats():
    categoryDict = {}
    subcategoryDict = {}

    categoryList = []
    f = open('linksDBCategories.txt','r')
    line = f.readline()
    while line:                                         # Create list with cat types
        categoryList.append(line.replace('\n',''))
        line = f.readline()


    for cat in categoryList:            # Initialize empty dictionaries from list (key, value)
        categoryDict[cat] = 0
        subcategoryDict[cat] = 0

    totalCats = 0
    totalSubs = 0

    f2 = open('linksDBWithCat.txt','r')         # Start the count for each Cat/Subcat Dicts
    line = f2.readline()
    while line:
        lineParts = line.split()
        cat = lineParts[1]
        subcat = lineParts[2]

        if cat in categoryDict:
            categoryDict[cat] += 1
            totalCats += 1

        if subcat in subcategoryDict:
            subcategoryDict[subcat] += 1
            totalSubs += 1

        line = f2.readline()


    print("Total = " + str(totalCats))
    print("Categories: " + str(categoryDict))
    print()
    print("Total = " + str(totalSubs))
    print("Subcategories: " + str(subcategoryDict))



# FIND CATEGORY AND SUBCATEGORY POSSIBLE TYPES
def catTypes(): 
    categories = {""}               # No repeats
    subcategories = {""}

    f = open('linksDBWithCat.txt','r')
    line = f.readline()
    while line:
        #print(line)
        parts = line.split()
        categories.add(parts[1])
        subcategories.add(parts[2])

        line = f.readline()

    print("\nPOSSIBLE CATEGORIES: ")
    print(sorted(categories))
    print("\nPOSSIBLE SUBCATEGORIES: ")
    print(sorted(subcategories))



# WRITE ALL LINKS FROM DB TO TXT... AND FIX THEM [virustotal.com]
def links2txtVirus():
    
    con = db_controller.sql_connection()        
    db_controller.sql_create(con)
    cur = con.cursor()

    cur.execute("SELECT link FROM attack")
    linkList = cur.fetchall()                   # List of Tuples with 1 element

    f = open('linksDB.txt', 'w')
    try:
        for l in linkList:
            
            link = l[0]
            link = link.strip()
            #f.write(link + " \t --> \t ")       # write original link to compare

            if '.onion' in link:                 # PRE: get domain and after process it like the rest
                if '/page/' in link:      
                    parts = link.split('/page/')
                    link = parts[1]
                else: 
                    parts = link.split('.onion/')
                    link = parts[1]

            if link.startswith("http"):                  # Only works without http(s):// - www is fine
                firstBar = link.find('/')
                cut = firstBar + 2
                link = link[cut : :]                     # from cut to end
                
            f.write(link)
            f.write("\n")
    finally:
        f.close()


links2txtVirus()


# WRITE ALL LINKS FROM DB TO TXT... AND FIX THEM [URL categorization GitHub]

# Links can start http(s)://www... OR www... OR only_domain OR -1
# OR special case .onion --> http://continewsnv5otx5kaoje7krkto2qbu3gtqef22mnr7eaxw3y6ncz3ad.onion[/page]/[www.]rtcnt.com
def links2txtGit():
    
    con = db_controller.sql_connection()        
    db_controller.sql_create(con)
    cur = con.cursor()

    cur.execute("SELECT link FROM attack")
    linkList = cur.fetchall()                   # List of Tuples with 1 element

    f = open('linksDB.txt', 'w')
    try:
        for l in linkList:
            
            link = l[0]
            link = link.strip()
            #f.write(link + " \t --> \t ")       # write original link to compare

            if '.onion' in link:                 # PRE: get domain and after process it like the rest
                if '/page/' in link:      
                    parts = link.split('/page/')
                    link = parts[1]
                else: 
                    parts = link.split('.onion/')
                    link = parts[1]

            if link.startswith("http") or link == '-1':      
                f.write(link)
            elif link.startswith("www"):
                f.write("http://"+link)
            else:
                f.write("http://www."+link)
            f.write("\n")
    finally:
        f.close()



# MOVE DATA FROM DB1 TO DB2
def move_data():

    con = db_controller.sql_connection()        # NEW DB
    db_controller.sql_create(con)
    cur = con.cursor()

    cur.execute("ATTACH DATABASE 'ransomwareLeaksDB.db' AS old")


    cur.execute("SELECT * FROM old.family")
    row = cur.fetchone()

    family = ['CONTI',row[1],row[2],row[3],row[4]]
    print(family)

    try:
        print("Inserting Values into FAMILY...")
        cur.execute("INSERT INTO family VALUES(?,?,?,?,?);",family)
        con.commit()
    except Exception as e:
        print(e)


    cur.execute("SELECT * FROM old.attack")
    all = cur.fetchall()

    i = 0
    for row in all:            # 0...428
        
        try:
            i+=1
            attack = [i, row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],'CONTI']
            print("Inserting Values into ATTACK...")
            cur.execute("INSERT INTO attack VALUES(?,?,?,?,?,?,?,?,?,?,?,?);",attack)       # elimina el anterior execute, todo ya en all
            con.commit()
            print("Commit.")

        except Exception as e:
            print(e)
