from calendar import month
from datetime import datetime
from sqlite3 import Error
import sys
import time
import utils

# [Hive]
# All leaks 1 page, no page change

def crawl_hive(driver,con,familiesSite):  
    
    [groupName, onionVersion, siteLink] = utils.enter_site(driver, "Hive")
    
    # FAMILY
    cur = con.cursor()

    print("\ngroupName: " + groupName)
    print("onionVersion: " + onionVersion)

    # Enter Site
    print("\nTrying to enter Site...")
    driver.get(siteLink)
    time.sleep(12)          # Fixes Enable JS, page wasn't loading !
    print("Entered Site\n")

    groupTitle = driver.find_element_by_xpath("//div[@class='logo']/p").text
    print("groupTitle: " + groupTitle)

    information = -1
    print("information: " + str(information))

    now = datetime.now()
    lastCrawledGroup = now.strftime("%m/%d/%Y, %H:%M:%S")
    print("lastCrawledGroup: " + lastCrawledGroup)	

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



    #id = lenTable

    cur = con.cursor()
    cur.execute("SELECT * FROM attack")
    id = len(cur.fetchall())
    print("TABLE ROWS: " + str(id))

    # Save HTML page 
    
    pageSource = driver.page_source
    fileToWrite = open("source_hive/hive_main.html", "w", encoding="utf-8")
    fileToWrite.write(pageSource)
    fileToWrite.close()

    # All leaks from page 
    leaks = driver.find_elements_by_xpath("//div[@class='container']/div/section")

    # Sometimes no leaks load, usually works on 2nd try
    tries = 1
    while len(leaks) == 0:
        print("TRY NUMBER: " + str(tries))

        driver.get(siteLink)
        time.sleep(10)       
        leaks = driver.find_elements_by_xpath("//div[@class='container']/div/section")
 
        tries+=1
        if tries == 5: break
  


    for i in range(len(leaks)):
        print("\n[LEAK "+str(i)+"]\n")

        l = driver.find_element_by_xpath("//div[@class='container']/div/section["+str(i+1)+"]")
        
        # .text no funciona 

        try:
            siteTitle = l.find_element_by_xpath("div/div/div/h2").get_attribute('innerHTML')
            print("siteTitle: " + siteTitle)
        except Exception as e: 
            siteTitle = -1
            print(e)

        try:    
            link = l.find_element_by_xpath("div/div/div/ul/li/a").get_attribute("href")
            print("link: " + link)
        except Exception as e: 
            link = -1
            print(e)

        location = -1

        try:
            information = l.find_element_by_xpath("div/div/div/p").get_attribute('innerHTML')
            print("information: " + information)
            print("...endinformation\n")
        except Exception as e:
            information = -1
            print(e)

        try:
            date = l.find_element_by_xpath("div/div/div[2]/div[2]/p/span").get_attribute('innerHTML').split()     # 24 January 2022 
            day = date[0]
            month = date[1]
            year = date[2]
            
            time_object = datetime.strptime(month, "%B") 
            monthNum = time_object.month
            print("PRE-date: " + day + str(monthNum) + year)   
            date = day+"/"+str(monthNum)+"/"+year
            print("date: " + date)   
        except Exception as e:
            date = -1
            print(e)

        views = -1

        ransomMoney = -1        

        publishedPercentage = -1

        dataSize = -1

        now = datetime.now()
        lastCrawledLeak = now.strftime("%m/%d/%Y, %H:%M:%S")
        print("lastCrawledLeak: " + lastCrawledLeak)

        id += 1
        
        attack = [id,siteTitle,link,location,information,date,views,ransomMoney,publishedPercentage,dataSize,lastCrawledLeak,groupName]
        try:
            print("Inserting Values into ATTACK...")
            cur.execute("INSERT INTO attack VALUES(?,?,?,?,?,?,?,?,?,?,?,?);",attack)
            con.commit()
        except Exception as e:
            print(e)


    print('Returning to Families Site Page...')
    driver.get(familiesSite)
    time.sleep(10)



