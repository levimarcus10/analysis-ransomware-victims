from calendar import month
from datetime import datetime
from sqlite3 import Error
import sys
import time
import utils

# [Lorenz]
# All leaks 1 page, no page change

def crawl_lorenz(driver,con,familiesSite):  
    
    [groupName, onionVersion, siteLink] = utils.enter_site(driver, "Lorenz")
    
    # FAMILY
    cur = con.cursor()

    print("\ngroupName: " + groupName)
    print("onionVersion: " + onionVersion)

    # Enter Site
    print("\nTrying to enter Site...")
    driver.get(siteLink)
    time.sleep(5)          
    print("Entered Site\n")

    groupTitle = driver.find_element_by_xpath("//h3/p").text
    print("groupTitle: " + groupTitle)

    information = driver.find_element_by_xpath("//h4/small").text
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


    # id = lenTable

    cur = con.cursor()
    cur.execute("SELECT * FROM attack")
    id = len(cur.fetchall())
    print("TABLE ROWS: " + str(id))

    # Save HTML page 
 
    pageSource = driver.page_source
    fileToWrite = open("source_lorenz/lorenz_main.html", "w", encoding="utf-8")
    fileToWrite.write(pageSource)
    fileToWrite.close()
    
    
    # All leaks from page [all divs except id=comp99]
    leaks = driver.find_elements_by_xpath("//div[@class='col-sm-9']/div[not(contains(@id, 'comp99'))]")
    print(len(leaks))

    # Leak 2 = Kenall can't find PublishedPercentage !!!

    for i in range(len(leaks)):
        print("\n[LEAK "+str(i)+"]\n")

        l = leaks[i]        # works when no page change

        try:
            siteTitle = l.find_element_by_xpath("div[@class='panel-heading']/h3").text
            print("siteTitle: " + siteTitle)
        except Exception as e: 
            siteTitle = -1
            print(e)


        # Some leaks have inside <panel-heading> 3 or 4 <h5>, usually 2 
        # Last one is link, one before is date

        NumH5 = len(l.find_elements_by_xpath("div[@class='panel-heading']/h5")) 

        try:    
            link = l.find_element_by_xpath("div[@class='panel-heading']/h5["+str(NumH5)+"]/a").get_attribute("href")
            print("link: " + link)
        except Exception as e: 
            link = -1
            print(e)

        try:
            date = l.find_element_by_xpath("div[@class='panel-heading']/h5["+str(NumH5-1)+"]").text.split()    # Posted Dec 17, 2021. -> [D/M/Y]
            
            day = date[2].replace(",","")   # 17,
            month = date[1]
            year = date[3].replace(".","")  # 2021.
            
            time_object = datetime.strptime(month, "%b")        # %B = January, %b = Jan
            monthNum = time_object.month
            print("PRE-date: " + day + str(monthNum) + year)   
            
            date = day+"/"+str(monthNum)+"/"+year
            print("date: " + date)   
        except Exception as e:
            date = -1
            print(e)


        # Some have <a> in the middle, others don't
        try:        
            publishedPercentage = l.find_element_by_xpath("div[@class='panel-body']/a/div/div").text.split()    # Uploaded 95% files -> 95
            publishedPercentage = publishedPercentage[1]
            publishedPercentage = publishedPercentage.replace("%","")
            print("publishedPercentage: " + str(publishedPercentage))     
        except:
            try:
                publishedPercentage = l.find_element_by_xpath("div[@class='panel-body']/div/div").text.split()   
                publishedPercentage = publishedPercentage[1]
                publishedPercentage = publishedPercentage.replace("%","")
                print("2.publishedPercentage: " + str(publishedPercentage))  
            except Exception as e:
                publishedPercentage = -1
                print(e)      
        

        views = -1

        location = -1
        
        information = -1

        ransomMoney = -1        

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

    print('Returning to Families Site Page...')
    driver.get(familiesSite)
    time.sleep(10)




