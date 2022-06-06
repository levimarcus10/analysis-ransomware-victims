from datetime import datetime
from sqlite3 import Error
import sys
import time
import utils

# [RansomEXX]
# 2 pages, no entering leaks

def crawl_ransomexx(driver,con,familiesSite):
    
    [groupName, onionVersion, siteLink] = utils.enter_site(driver, "RansomEXX")
    
    # FAMILY
    cur = con.cursor()

    print("\ngroupName: " + groupName)
    print("onionVersion: " + onionVersion)

    # Enter Site
    print("\nTrying to enter Site...")
    driver.get(siteLink)
    print("Entered Site\n")

    groupTitle = groupName          # nothing
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


    # Calculate NumPages Dinamically (<ul> of <li> = list of page numbers)
    pages = driver.find_elements_by_xpath('/html/body/div/div[21]/div/div/div/ul/li')           
    numPages = len(pages)

    print("\nnumPages: " + str(numPages));

    #id = lenTable      # Primary Key of Attack Table 

    cur = con.cursor()
    cur.execute("SELECT * FROM attack")
    id = len(cur.fetchall())
    print("TABLE ROWS: " + str(id))

    pageNumber = 0
    while pageNumber <= numPages:      

        pageNumber+=1
        currentPage = siteLink+"?page="+str(pageNumber)
        driver.get(currentPage)        # Go to next page 

        # Save HTML each page 
        pageSource = driver.page_source
        fileToWrite = open("source_ransomexx/ransomexx_p"+str(pageNumber)+".html", "w", encoding="utf-8")
        fileToWrite.write(pageSource)
        fileToWrite.close()


        print("\n--------------------------------\n")
        print("PAGE " + str(pageNumber))

        # All leaks from same page
        leaks = driver.find_elements_by_xpath("//div[@class='container py-4']/div[@class='row justify-content-md-center']")
        print("num leaks : " + str(len(leaks)))

        
        for i in range(len(leaks)):
            print("\n[LEAK "+str(i)+"]\n")
    
            l = leaks[i]

            try:
                siteTitle = l.find_element_by_tag_name("h5").text
                print("siteTitle: " + siteTitle)
            except Exception as e: 
                siteTitle = -1
                print(e)

            try:    
                link = l.find_element_by_tag_name("a").get_attribute("href")
                print("link: " + link)
            except Exception as e: 
                link = -1
                print(e)

            try:
                pS = l.find_elements_by_tag_name("p")
                information = pS[1].text
                print("information: " + information)
                print("...endinformation\n")
            except Exception as e:
                information = -1
                print(e)


            # same element: "published: 2022-02-15, visits: 26783, leak size: 2.4GB"

            try:
                pS = l.find_elements_by_tag_name("p")
                all = pS[2].text
                allParts = all.split(",")
            except Exception as e:
                print(e)

            try:
                datePart = allParts[0]
                dateSplit = datePart.split(":")
                predate = dateSplit[1].strip()
                print("predate: " + predate)              # Fix Date format

                predateParts = predate.split("-")
                date = predateParts[2] + "/" + predateParts[1] + "/" + predateParts[0]
                print("date: " + date)             
            except Exception as e:
                date = -1
                print(e)

            try:
                viewsPart = allParts[1]
                viewsSplit = viewsPart.split(":")
                views = viewsSplit[1].strip()                
                print("views: " + views)
            except Exception as e:
                views = -1
                print(e)

            try: 
                dataSizePart = allParts[2]
                dataSizeSplit = dataSizePart.split(":")
                dataSize = dataSizeSplit[1].strip()
                print("dataSize: " + dataSize)
            except Exception as e:
                dataSize = -1
                print(e)

          
            now = datetime.now()
            lastCrawledLeak = now.strftime("%m/%d/%Y, %H:%M:%S")
            print("lastCrawledLeak: " + lastCrawledLeak)

            location = -1
            ransomMoney = -1  
            publishedPercentage = -1      
            id += 1

            try:
                # ATTACKS
                attack = [id,siteTitle,link,location,information,date,views,ransomMoney,publishedPercentage,dataSize,lastCrawledLeak,groupName]

                print("Inserting Values into ATTACK...")
                cur.execute("INSERT INTO attack VALUES(?,?,?,?,?,?,?,?,?,?,?,?);",attack)
                con.commit()
            except Exception as e:
                print(e)

            # Get back lost reference (always same page!)
            #leaks = driver.find_elements_by_xpath("//div[@class='container py-4']/div[@class='row justify-content-md-center']")
 
        # end for
    # end while


    print('Returning to Families Site Page...')
    driver.get(familiesSite)
    time.sleep(10)



