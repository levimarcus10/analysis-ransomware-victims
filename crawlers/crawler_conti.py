from datetime import datetime
from sqlite3 import Error
import sys
import time
import utils

# [CONTI]
# several pages, each page 9 leaks with popup

def crawl_conti(driver,con,familiesSite):
    
    [groupName, onionVersion, siteLink] = utils.enter_site(driver, "CONTI")
    
    # FAMILY
    cur = con.cursor()

    print("\ngroupName: " + groupName)
    print("onionVersion: " + onionVersion)

    # Enter Site
    print("\nTrying to enter Site...")
    driver.get(siteLink)
    print("Entered Site\n")

    groupTitle = driver.find_element_by_xpath("//div[@class='logo']/a/div").text
    print("groupTitle: " + groupTitle.replace("\n"," "))

    information = driver.find_element_by_xpath("//div[@class='text']").text
    print("information: " + information)

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


    # Calculate NumPages Dinamically ('go to last page' button)
    numPages = driver.find_elements_by_tag_name("li")[-1].find_element_by_tag_name("a").get_attribute("href")
    numPages = numPages[-2] + numPages[-1]      # last 2 numbers from string
    numPages = int(numPages)

    print("\nnumPages: " + str(numPages));


    #id = lenTable      # Primary Key of Attack Table (Read last id from table --> crawler_onion)
    
    cur = con.cursor()
    cur.execute("SELECT * FROM attack")
    id = len(cur.fetchall())
    print("TABLE ROWS: " + str(id))

    pageNumber = 0
    while pageNumber <= numPages:      

        pageNumber+=1
        currentPage = siteLink+"page/"+str(pageNumber)
        driver.get(currentPage)        # Go to next page 

        # Save HTML each page 
        pageSource = driver.page_source
        fileToWrite = open("source_conti/conti_p"+str(pageNumber)+".html", "w", encoding="utf-8")
        fileToWrite.write(pageSource)
        fileToWrite.close()


        print("\n--------------------------------\n")
        print("PAGE " + str(pageNumber))

        # All leaks from same page
        leaks = driver.find_elements_by_xpath("//div[@class='card']")

        for i in range(len(leaks)):
            print("\n[LEAK "+str(i)+"]\n")
    
            l = driver.find_element_by_xpath("//div[@class='card']["+str(i+1)+"]")

            try:
                siteTitle = l.find_element_by_xpath("div[@class='title']").text
                print("siteTitle: " + siteTitle)
            except Exception as e: 
                siteTitle = -1
                print(e)

            try:    
                link = l.find_element_by_xpath("div[@class='body']/div/span/a").get_attribute("href")
                print("link: " + link)
            except Exception as e: 
                link = -1
                print(e)

            try:
                location = l.find_element_by_xpath("div[@class='body']/div[@class='wrap']/span").text
                print("location: " + location)
            except Exception as e: 
                location = -1
                print(e)

            try:
                information = l.find_element_by_xpath("div[@class='body']/div[@class='wrap'][2]/span").text
                print("information: " + information)
                print("...endinformation\n")
            except Exception as e:
                information = -1
                print(e)

            try:
                date = l.find_element_by_xpath("div[@class='footer']/div").text
                print("date: " + date)
            except Exception as e:
                date = -1
                print(e)

            try:
                views =  l.find_element_by_xpath("div[@class='footer']/div[@class='view']/span[2]").text
                print("views: " + views)
            except Exception as e:
                views = -1
                print(e)

            try:
                publishedPercentage = l.find_element_by_xpath("div[@class='meter']/span").text.split()
                publishedPercentage = publishedPercentage[1].replace("%","")
                print("publishedPercentage: " + str(publishedPercentage))     # text = "PUBLISHED 10%"
            except:
                publishedPercentage = 0         # if nothing, then 0% published
                print("publishedPercentage: " + str(publishedPercentage))

            try: 
                # 'Read More' Button
                l.find_element_by_xpath("div[@class='footer']/div[3]").click()
                time.sleep(2)   # OK
            
                # Popup is accessible '0 [ 0.00 B ]' 
                dataSize = driver.find_element_by_xpath("//div[@class='footer']/div[3]").text
                dataSize = dataSize.split("[")
                dataSize = dataSize[1].replace("]","").strip()      # strip removes spaces at start and end
                print("dataSize: " + dataSize)
            except Exception as e:
                dataSize = -1
                print(e)

            try:
                # Save HTML each popup 
                popUp = driver.find_element_by_xpath("//div[@class='news']").get_attribute('innerHTML')
                
                popUpTitle = siteTitle.replace('”','').replace('“','').replace(" ","_").lower()
                print("POPUP TITLE: " + popUpTitle)
                
                fileToWrite = open("source_conti/conti_p"+str(pageNumber)+"_"+popUpTitle+".html", "w", encoding="utf-8")
                fileToWrite.write(popUp)
                fileToWrite.close()
      
                driver.get(currentPage)     # Close Popup  
            except Exception as e:
                print(e)

            now = datetime.now()
            lastCrawledLeak = now.strftime("%m/%d/%Y, %H:%M:%S")
            print("lastCrawledLeak: " + lastCrawledLeak)

            ransomMoney = -1        
            id += 1

            try:
                # ATTACKS
                attack = [id,siteTitle,link,location,information,date,views,ransomMoney,publishedPercentage,dataSize,lastCrawledLeak,groupName]

                print("Inserting Values into ATTACK...")
                cur.execute("INSERT INTO attack VALUES(?,?,?,?,?,?,?,?,?,?,?,?);",attack)
                con.commit()
            except Exception as e:
                print(e)

                # Get back lost reference
            leaks = driver.find_elements_by_xpath("//div[@class='card']")

        # end for
    # end while
    
    print('Returning to Families Site Page...')
    driver.get(familiesSite)
    time.sleep(10)
