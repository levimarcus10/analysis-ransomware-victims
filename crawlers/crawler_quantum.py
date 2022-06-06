from ast import expr_context
from datetime import datetime
import site
from sqlite3 import Error
from statistics import pvariance
import sys
import time
import utils

# [Quantum]
# All leaks in 1 page, enter each leak for more info and back

def crawl_quantum(driver,con,familiesSite):
    
    [groupName, onionVersion, siteLink] = utils.enter_site(driver, "Quantum")
    
    # FAMILY
    cur = con.cursor()

    print("\ngroupName: " + groupName)
    print("onionVersion: " + onionVersion)

    # Enter Site
    print("\nTrying to enter Site...")
    driver.get(siteLink)
    print("Entered Site.\n")

    groupTitleList = driver.find_element_by_xpath("//html/body/div[1]/div[2]/div/a").text.split()
    groupTitle = groupTitleList[1] + " " + groupTitleList[2]
    print("groupTitle: " + groupTitle)

    # "About" Page
    driver.get(siteLink+"about")
    time.sleep(2)

    information = driver.find_element_by_xpath("//div[@class='blog-post-content']").text
    print("information: " + information)
    print("...end information")

    # Return to Main Page
    driver.get(siteLink)
    time.sleep(2)

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


    #id = lenTable      # Primary Key of Attack  

    cur = con.cursor()
    cur.execute("SELECT * FROM attack")
    id = len(cur.fetchall())
    print("TABLE ROWS: " + str(id))


    # Save HTML of main page 
    pageSource = driver.page_source
    fileToWrite = open("source_quantum/quantum_main.html", "w", encoding="utf-8")
    fileToWrite.write(pageSource)
    fileToWrite.close()


    # Leaks are divided into columns on same page

    columns = driver.find_elements_by_xpath("//div[@class='col-sm-4']")
    print(len(columns))

    for j in range(len(columns)):
        print("\n[COLUMN "+str(j)+"]\n")

        # All leaks from same column
        leaks = driver.find_elements_by_xpath("//div[@class='col-sm-4']["+str(j+1)+"]/section[@class='blog-post']")
        print(len(leaks))

        for i in range(len(leaks)):
            print("\n[LEAK "+str(i)+"]\n")

            l = driver.find_element_by_xpath("//div[@class='col-sm-4']["+str(j+1)+"]/section[@class='blog-post']["+str(i+1)+"]")

            try:
                siteTitle = l.find_element_by_tag_name("h2").text         
                print("siteTitle: " + siteTitle)
            except Exception as e: 
                siteTitle = -1
                print(e)


            # Enter each leak (new page) NOW USE DRIVER, NOT LEAK 'l'

            try:   
                As = l.find_elements_by_tag_name("a")       # two links, only 2nd works
                As[1].click()
                print("\nEntering leak...\n")

                # Save HTML each leak 
                leakSource = driver.page_source

                siteTitleFile = siteTitle.replace(" ","_").lower()
                
                fileToWrite = open("source_quantum/quantum_"+siteTitleFile+".html", "w")
                fileToWrite.write(leakSource)
                fileToWrite.close()
            except Exception as e:
                print(e)

            try:
                dataSizeAll =  driver.find_element_by_xpath("/html/body/div[2]/div/div/section[1]/div/div/div[1]/span[1]").text
                if 'file' in dataSizeAll:
                    dataSizeParts = dataSizeAll.split()
                    dataSize = dataSizeParts[0]
                else:
                    dataSize = dataSizeAll
                print("dataSize: " + dataSize)                          # 490[]GB [(232323 files)]
            except Exception as e:
                dataSize = -1
                print(e)

            try:
                viewsAll =  driver.find_element_by_xpath("/html/body/div[2]/div/div/section[1]/div/div/div[1]/span[2]").text.split()
                viewsPoint = viewsAll[0].split(".")                                      # Convert: 203.7K figure

                LeftPoint = viewsPoint[0]
                RightPoint = viewsPoint[1].replace("K","")

                views = LeftPoint + RightPoint + "00"
                print("views: " + views)
            except Exception as e:
                views = -1
                print(e)

            try:
                predate =  driver.find_element_by_xpath("/html/body/div[2]/div/div/section[1]/div/div/div[1]/p").text.split("-")
                        
                year = predate[0]           # Convert: 2021-10-18 
                month = predate[1]
                day = predate[2]

                date = day + "/" + month + "/" + year
                print("date: " + date)          
            except Exception as e:
                date = -1
                print(e)   

            try:
                link =  driver.find_element_by_xpath("/html/body/div[2]/div/div/section[1]/div/div/div[2]/div[1]/div[1]/dl/dd[2]/a").get_attribute('href')
                print("link: " + link)              # format?
            except Exception as e:
                link = -1
                print(e)   

            try:
                publishedPercentageAll =  driver.find_element_by_xpath("/html/body/div[2]/div/div/section[1]/div/div/div[2]/div[1]/div[1]/dl/dd[5]").text.split()
                publishedPercentageWithSymbol = publishedPercentageAll[0]
                publishedPercentage = publishedPercentageWithSymbol.replace('%','')
                print("publishedPercentage: " + publishedPercentage)           # Convert: 100% (...)     
            except Exception as e:
                publishedPercentage = -1
                print(e)   

            try:
                information =  driver.find_element_by_xpath("/html/body/div[2]/div/div/section[1]/div/div/div[2]/div[2]/div").text
                print("information: " + information)
                print("...end information")                              
            except Exception as e:
                information = -1
                print(e) 
    
            
            now = datetime.now()
            lastCrawledLeak = now.strftime("%m/%d/%Y, %H:%M:%S")
            print("lastCrawledLeak: " + lastCrawledLeak)

            location = -1
            ransomMoney = -1

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
            columns = driver.find_elements_by_xpath("//div[@class='col-sm-4']")         # Get back lost references
            leaks = driver.find_elements_by_xpath("//div[@class='col-sm-4']["+str(j+1)+"]/section[@class='blog-post']")  

        # end inner for
    # end outer for


    print('Returning to Families Site Page...')
    driver.get(familiesSite)
    time.sleep(10)


