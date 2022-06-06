from ast import expr_context
from datetime import datetime
import site
from sqlite3 import Error
from statistics import pvariance
import sys
import time
import utils

# [Midas]
# All leaks in 1 page, enter each leak for more info and back

def crawl_midas(driver,con,familiesSite):
    
    [groupName, onionVersion, siteLink] = utils.enter_site(driver, "Midas")
    
    # FAMILY
    cur = con.cursor()

    print("\ngroupName: " + groupName)
    print("onionVersion: " + onionVersion)

    # Enter Site
    print("\nTrying to enter Site...")
    driver.get(siteLink)
    print("Entered Site.\n")

    groupTitle = groupName          # No Title inside page
    print("groupTitle: " + groupTitle)

    time.sleep(3)
    information = driver.find_element_by_xpath("//html/body/div[1]/div/div[2]/div[1]/p").text
    print("information: " + information)

    now = datetime.now()
    lastCrawledGroup = now.strftime("%m/%d/%Y, %H:%M:%S")
    print("lastCrawledGroup: " + lastCrawledGroup)	

    
    # Insert DB
    
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


    #id = lenTable      # Primary Key of Attack (Read last id from table)
    
    cur = con.cursor()
    cur.execute("SELECT * FROM attack")
    id = len(cur.fetchall())
    print("TABLE ROWS: " + str(id))


    # Go to leaks, other page
    driver.get(siteLink+"/blog.php")
    time.sleep(5)
    
    
    # Save HTML of main page 
    pageSource = driver.page_source
    fileToWrite = open("source_midas/midas_main.html", "w", encoding="utf-8")
    fileToWrite.write(pageSource)
    fileToWrite.close()
    

    # All leaks from same page
    leaks = driver.find_elements_by_xpath("//div[@class='row mb-5']/div")
    print(len(leaks))

    for i in range(len(leaks)):
        print("\n[LEAK "+str(i)+"]\n")

        l = driver.find_element_by_xpath("//div[@class='row mb-5']/div["+str(i+1)+"]")

        # Enter 'Read more..' directly
        try:
            l.find_element_by_xpath("div/a").click()
            time.sleep(2)
        except Exception as e:
            print(e)


        # Some leaks don't have all info, look by 'th': <tr> <th>Company:</th> <td>Keuerleber</td> </tr>
        trS = driver.find_elements_by_xpath("//html/body/div[4]/div/div/div/div[2]/div/div[1]/table/tbody/tr")
        print("number of trS:")
        print(len(trS))


        try:
            for tr in trS:
                if "Company" in tr.find_element_by_tag_name('th').text:
                    siteTitle = tr.find_element_by_tag_name('td').text.strip()      # remove spaces
            print("siteTitle: " + siteTitle)
        except Exception as e: 
            siteTitle = -1
            print(e)

        try:
            for tr in trS:
                if "Address" in tr.find_element_by_tag_name('th').text:
                    location = tr.find_element_by_tag_name('td').text.strip()     
            print("location: " + location)
        except Exception as e: 
            location = -1
            print(e)

        try:
            for tr in trS:
                if "Website" in tr.find_element_by_tag_name('th').text:
                    link = tr.find_element_by_tag_name('td').text.strip()      
            print("link: " + link)
        except Exception as e: 
            link = -1
            print(e)

        try:
            information =  driver.find_element_by_xpath("//html/body/div[4]/div/div/div/div[2]/div/div[2]").text.strip()
            print("information: " + information)
            print("...end information: ")
        except Exception as e:
            information = -1
            print(e)

        try:
            views =  driver.find_element_by_xpath("//html/body/div[4]/div/div/div/div[2]/div/div[3]/span").text.split()
            views = views[1].strip()                    # views = 'Views: 10807'
            print("views: " + views)
        except Exception as e:
            views = -1
            print(e)


        now = datetime.now()
        lastCrawledLeak = now.strftime("%m/%d/%Y, %H:%M:%S")
        print("lastCrawledLeak: " + lastCrawledLeak)


        # Save HTML each leak 
        try: 
            leakSource = driver.page_source
            
            siteTitleFile = siteTitle.replace(" ","_").lower()
            
            fileToWrite = open("source_midas/midas_"+siteTitleFile+".html", "w")
            fileToWrite.write(leakSource)
            fileToWrite.close()
        except Exception as e:
            print(e)


        date = -1
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
        

        driver.get(siteLink+"/blog.php")     # Return to main page
        leaks = driver.find_elements_by_xpath("//div[@class='row mb-5']/div")   # Get back lost reference
    
    # end for

    print('Returning to Families Site Page...')
    driver.get(familiesSite)
    time.sleep(10)






