from calendar import month
from datetime import datetime
from distutils.log import info
from sqlite3 import Error
import sys
import time
import utils

# [Pysa]
# All leaks 1 page, no page change

def crawl_pysa(driver,con,lenTable):  
    
    [groupName, onionVersion, siteLink] = utils.enter_site(driver, "Pysa")
    
    # FAMILY
    cur = con.cursor()

    print("\ngroupName: " + groupName)
    print("onionVersion: " + onionVersion)

    # Enter Site
    print("\nTrying to enter Site...")
    driver.get(siteLink)
    time.sleep(5)          
    print("Entered Site\n")

    groupTitle = groupName          # title in page is artistic
    print("groupTitle: " + groupTitle)

    information = driver.find_element_by_xpath("//html/body/header/div/p").text.strip()
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


    id = lenTable

    # Save HTML page 
    
    pageSource = driver.page_source
    fileToWrite = open("source_pysa/pysa_main.html", "w", encoding="utf-8")
    fileToWrite.write(pageSource)
    fileToWrite.close()

    # All leaks from page 
    leaks = driver.find_elements_by_xpath("//div[@class='span9']/section")
    print("LEN LEAKS: ")
    print(len(leaks))

    
    for i in range(len(leaks)):
        print("\n[LEAK "+str(i)+"]\n")

        l = leaks[i]

        try:
            siteTitle = l.find_element_by_xpath("div/span/a").get_attribute('innerHTML')
            print("siteTitle: " + siteTitle)
        except Exception as e: 
            siteTitle = -1
            print(e)

        try:
            PREdate = l.find_element_by_xpath("div/span[2]").get_attribute('innerHTML').split("/")    # MM/DD/YY (add also 20YY)
            print("PREdate: " + str(PREdate))
            month = PREdate[0]            
            day = PREdate[1]
            year = PREdate[2]      
            if len(year) == 2:          # some already have the 20YY, most don't
                year = "20"+year

            date = day+"/"+month+"/"+year
            print("date: " + str(date))
        except Exception as e:
            date = -1
            print(e)

        try:    
            link = l.find_element_by_xpath("div/span[3]/a").get_attribute("href")
            print("link: " + str(link))
        except Exception as e: 
            link = -1
            print(e)

        try:    
            information = l.find_element_by_xpath("div[2]").text
            if information == "":                   # all have element, some are blank
                information = -1
            print("information: " + str(information))
            print("...information")
        except Exception as e: 
            information = -1
            print(e)

        location = -1

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
    
    # end for



