from ast import expr_context
from datetime import datetime
import site
from sqlite3 import Error
from statistics import pvariance
import sys
import time
import utils

# [LockBit 2.0]
# All leaks in 1 page, enter each leak for more info and back (info is better)
# First leaks not published yet, rest yes

def crawl_lockbit(driver,con,familiesSite):
    
    [groupName, onionVersion, siteLink] = utils.enter_site(driver, "LockBit 2.0")
    
    # FAMILY
    cur = con.cursor()

    print("\ngroupName: " + groupName)
    print("onionVersion: " + onionVersion)

    # Enter Site
    print("\nTrying to enter Site...")
    driver.get(siteLink)
    time.sleep(10)   
    print("Entered Site.\n")

    groupTitle = groupName          # it's an image
    print("groupTitle: " + groupTitle)

    # New Page
    print("Entering Conditions...")
    driver.get(siteLink+"/conditions")
    time.sleep(5)   

    information = ""
    for i in range(4):
        information = information + " " + driver.find_element_by_xpath("//div[@class='mb-3']["+str(i+1)+"]").text     # only 4 first div
    print("information: " + information)

    # Return to main page
    print("Returning to main page...\n")
    driver.get(siteLink)
    time.sleep(10)   

    now = datetime.now()
    lastCrawledGroup = now.strftime("%m/%d/%Y, %H:%M:%S")
    print("lastCrawledGroup: " + lastCrawledGroup)	

    
    # Insertar DB
    
    family = [groupName,onionVersion,groupTitle,information,lastCrawledGroup]

    # If table already has groupName, update lastCrawledGroup
    try:
        print("Inserting Values into FAMILY...")
        cur.execute("INSERT INTO family VALUES(?,?,?,?,?);",family)
        con.commit()
    except Exception as e:
        print(e)                # UNIQUE constraint failed
        print("Updating FAMILY...")
        cur.execute("UPDATE family SET lastCrawledGroup=? WHERE groupName=?", (lastCrawledGroup,groupName))
        con.commit()


    #id = lenTable      # Primary Key of Attack (Read last id from table --> crawler_onion)

    cur = con.cursor()
    cur.execute("SELECT * FROM attack")
    id = len(cur.fetchall())
    print("TABLE ROWS: " + str(id))

    # Save HTML of main page 
    
    pageSource = driver.page_source
    fileToWrite = open("source_lockbit/lockbit_main.html", "w", encoding="utf-8")
    fileToWrite.write(pageSource)
    fileToWrite.close()
    

    # All leaks from same page [post-block good OR post-block bad]
    leaks = driver.find_elements_by_xpath("//div[@class='post-big-list  ']/div")         # remember spaces in class name

    print("MAX: " + str(len(leaks)))        # 355 = 0..354

    for i in range(len(leaks)):
        print("\n[LEAK "+str(i)+"]\n")

        try:
            l = driver.find_element_by_xpath("//div[@class='post-big-list  ']/div["+str(i+1)+"]")   # some can't find div[i]

            # All the code in try, if fails sleep(10) and next div[i]

            try: 
                l.find_element_by_xpath("div[@class='post-block-body']/a").click()
                print("Entering leak...")
            except Exception as e:
                print(e)

            # Leak Page !

            try:    
                link = driver.find_element_by_xpath("//div[@class='post-big-title']").text
                print("link: " + link)
            except Exception as e: 
                link = -1
                print(e)

            try:
                siteTitleAux = link.split(".")       # link with no .com
                siteTitle = siteTitleAux[0]
                print("siteTitle: " + siteTitle)
            except Exception as e: 
                siteTitle = -1
                print(e)

            try:
                date = driver.find_element_by_xpath("//p[@class='post-banner-p']").text.split()       # 07 Feb, 2022 09:32:00

                day = date[0]
                month = date[1].split(",")      # Feb,
                month = month[0]
                year = date[2]
                print("PRE-date: " + day + month + year)   

                time_object = datetime.strptime(month, "%b") 
                monthNum = time_object.month
                date = day+"/"+str(monthNum)+"/"+year
                print("date: " + date)
            except Exception as e:
                date = -1
                print(e)

            try:
                information = driver.find_element_by_xpath("//div[@class='desc']").text
                print("information: " + information)
                print("...endinformation\n")
            except Exception as e:
                information = -1
                print(e)   

            
            try:
                # Save HTML each leak 
                leakSource = driver.page_source
                
                siteTitleFile = siteTitle.replace(" ","_").lower()
                
                fileToWrite = open("source_lockbit/lockbit_"+siteTitleFile+".html", "w")
                fileToWrite.write(leakSource)
                fileToWrite.close()
            except Exception as e:
                information = -1
                print(e)   
            

            now = datetime.now()
            lastCrawledLeak = now.strftime("%m/%d/%Y, %H:%M:%S")
            print("lastCrawledLeak: " + lastCrawledLeak)

            location = -1
            views = -1
            ransomMoney = -1
            publishedPercentage = -1
            dataSize = -1
            id += 1

            # Insert DB
            try:
                attack = [id,siteTitle,link,location,information,date,views,ransomMoney,publishedPercentage,dataSize,lastCrawledLeak,groupName]

                print("Inserting Values into ATTACK...")
                cur.execute("INSERT INTO attack VALUES(?,?,?,?,?,?,?,?,?,?,?,?);",attack)
                con.commit()
            except Exception as e:
                print(e)
        
            driver.get(siteLink)     # Return to main page
            time.sleep(3)           # Can't find next div !
            
            leaks = driver.find_elements_by_xpath("//div[@class='post-big-list  ']/div")      # Get back lost reference
        
        except Exception as e:          # if can't find div[i] with leak, I think it hasn't loaded
            print(e)
            time.sleep(10)
    
    
    print('Returning to Families Site Page...')
    driver.get(familiesSite)
    time.sleep(10)




