from calendar import month
from datetime import datetime
from sqlite3 import Error
import sys
import time
import utils

# [Snatch]
# several pages, each page leaks, enter and back

def crawl_snatch(driver,con,familiesSite):
    
    [groupName, onionVersion, siteLink] = utils.enter_site(driver, "Snatch")
    
    # FAMILY
    cur = con.cursor()

    print("\ngroupName: " + groupName)
    print("onionVersion: " + onionVersion)

    # Enter Site
    print("\nTrying to enter Site...")
    driver.get(siteLink)
    print("Entered Site\n")

    groupTitle = groupName      # it's the same
    print("groupTitle: " + groupTitle.replace("\n"," "))

    information = driver.find_element_by_xpath("//div[@id='info_block']").text
    print("information: " + information)
    print("end information")

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
    

    # Calculate NumPages Dinamically ('count page numbers at bottom)
    pages = driver.find_elements_by_xpath("/html/body/div/main/div/div/div[4]/div/div/a")
    numPages = len(pages)
    print("\nnumPages: " + str(numPages));

    #id = lenTable      # Primary Key of Attack Table (Read last id from table --> crawler_onion)
    
    cur = con.cursor()
    cur.execute("SELECT * FROM attack")
    id = len(cur.fetchall())
    print("TABLE ROWS: " + str(id))

    pageNumber = 0
    while pageNumber < numPages:      

        pageNumber+=1
        currentPage = siteLink+"index.php?page="+str(pageNumber)
        driver.get(currentPage)        # Go to next page 
        time.sleep(5)

        # Save HTML each page 
        pageSource = driver.page_source
        fileToWrite = open("source_snatch/snatch_p"+str(pageNumber)+".html", "w", encoding="utf-8")
        fileToWrite.write(pageSource)
        fileToWrite.close()

        print("\n--------------------------------\n")
        print("PAGE " + str(pageNumber))

        # All leaks from same page
        leaks = driver.find_elements_by_xpath("//div[@class='ann-block']")

        for i in range(len(leaks)):
            print("\n[LEAK "+str(i)+"]\n")
    
            # All code in try, if div[i] fails, sleep and try next one

            try: 
                l = driver.find_element_by_xpath("//div[@class='ann-block']["+str(i+1)+"]")

                try:
                    siteTitle = l.find_element_by_xpath("div[2]/div").text
                    print("siteTitle: " + siteTitle)
                except Exception as e: 
                    siteTitle = -1
                    print(e)


                # Possible dataSize formats:
                # 160 GB
                # 500 GB | Text...
                # 100 GB | Data Added: 2.9 GB
                # Data Added: 350 GB

                try:
                    dataSize =  l.find_element_by_xpath("div[2]/span").text 
                    dsParts = dataSize.split()
                    if dataSize[0].isnumeric():
                        dataSize = dsParts[0] + " " + dsParts[1]
                    else:
                        dataSize = dsParts[2] + " " + dsParts[3]
                    print("dataSize: " + dataSize)
                except Exception as e:
                    dataSize = -1
                    print(e)


                # 2 or 3 divs (1st one not important when 3) -> date and views
                try:
                    divs = l.find_elements_by_xpath("div/div")
                    divNums = len(divs) - 3                             # Should be 3, appears 6
                    print("div nums: " + str(divNums))

                    dateDiv = divNums - 1
                    viewsDiv = divNums
                except Exception as e:
                    date = -1
                    print(e)

                try:
                    predate = l.find_element_by_xpath("div/div["+str(dateDiv)+"]").text        # Fix Format = 'Feb 23, 2022 10:36 PM'
                    print("predate: " + predate)

                    predateParts = predate.split()
                    
                    preMonth = predateParts[0]
                    time_object = datetime.strptime(preMonth, "%b")        # %B = January, %b = Jan
                    month = time_object.month

                    preDay = predateParts[1]
                    day = preDay.replace(",","")

                    year = predateParts[2]

                    date = day + "/" + str(month) + "/" + year
                    print("date: " + date)
                except Exception as e:
                    date = -1
                    print(e)

                try:
                    views =  l.find_element_by_xpath("div/div["+str(viewsDiv)+"]/p").text
                    print("views: " + views)
                except Exception as e:
                    views = -1
                    print(e)


                # Enter and Save Leak
                
                try:
                    l.find_element_by_tag_name("button").click()
                    time.sleep(4)

                    leakPage = driver.find_element_by_xpath("/html/body/div[4]/main/div/div/div[2]/div[2]").get_attribute('innerHTML')
                    
                    popUpTitle = siteTitle.replace('”','').replace('“','').replace(" ","_").lower()
                    
                    fileToWrite = open("source_snatch/snatch_p"+str(pageNumber)+"_"+popUpTitle+".html", "w", encoding="utf-8")
                    fileToWrite.write(leakPage)
                    fileToWrite.close()
                except Exception as e:
                    print(e)


                # Now use Driver

                # Some links don't have www (https://domain.com) - works fine with url categorization
                
                try:    
                    link = driver.find_element_by_xpath("/html/body/div[4]/main/div/div/div[2]/div[2]/div[2]/div[2]/div/span[1]").text
                    if '://' not in link:       # when no link, it takes other info as it
                        link = -1
                    print("link: " + str(link))
                except Exception as e: 
                    link = -1
                    print(e)

                try:
                    information = driver.find_element_by_xpath("/html/body/div[4]/main/div/div/div[2]/div[2]/div[2]/div[3]/p").text
                    print("information: " + information)
                    print("...endinformation\n")
                except Exception as e:
                    information = -1
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
                
                driver.get(currentPage)     # Return to main page
                leaks = driver.find_elements_by_xpath("//div[@class='ann-block']")       # Get back lost reference


            except Exception as e:          # if can't find div[i] with leak, it might not be loaded
                print(e)
                time.sleep(10)

        # end for
    # end while
      

    print('Returning to Families Site Page...')
    driver.get(familiesSite)
    time.sleep(10)





