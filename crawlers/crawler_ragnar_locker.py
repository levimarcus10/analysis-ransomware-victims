from ast import expr_context
from datetime import datetime
import site
from sqlite3 import Error
from statistics import pvariance
import sys
import time
import utils

# [Ragnar_Locker]
# All leaks in 1 page, enter each leak for more info and back

def crawl_ragnar_locker(driver,con,familiesSite):
    
    [groupName, onionVersion, siteLink] = utils.enter_site(driver, "Ragnar_Locker")
    
    # FAMILY
    cur = con.cursor()

    print("\ngroupName: " + groupName)
    print("onionVersion: " + onionVersion)

    # Enter Site
    print("\nTrying to enter Site...")
    driver.get(siteLink)
    print("Entered Site.\n")

    groupTitle = driver.find_element_by_xpath("//div[@id='_tl_view']/h1").text.strip()
    print("groupTitle: " + groupTitle)

    information = driver.find_element_by_xpath("//div[@id='_tl_view']/div[@class='header']/p").text
    print("information: " + information)

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
    time.sleep(5)


    # Save HTML of main page 
    pageSource = driver.page_source
    fileToWrite = open("source_ragnar/ragnar_main.html", "w", encoding="utf-8")
    fileToWrite.write(pageSource)
    fileToWrite.close()

    # All leaks from same page
    leaks = driver.find_elements_by_xpath("//div[@class='content']/div[@class='card']")

    for i in range(len(leaks)):
        print("\n[LEAK "+str(i)+"]\n")

        l = driver.find_element_by_xpath("//div[@class='card']["+str(i+1)+"]")

        # Main Page [Pages with 2<p> title and then views-published] [some add 3rd<p> between both]

        if len(l.find_elements_by_xpath("p")) == 3:
            pViewsPublished = 3
        else:
            pViewsPublished = 2

        try:
            siteTitle = l.find_element_by_xpath("p/a").text         # always first <p>
            print("siteTitle: " + siteTitle)
        except Exception as e: 
            siteTitle = -1
            print(e)

        try:
            views =  l.find_element_by_xpath("p["+str(pViewsPublished)+"]/small/span").text
            print("views: " + views)
        except Exception as e:
            views = -1
            print(e)

        try:
            prepreDate = l.find_element_by_xpath("p["+str(pViewsPublished)+"]/small[2]").text.split()
            print("PREdate " + prepreDate[1])
            predate = prepreDate[1].split("/")                        # date = 'Published: 06/14/2020 16:32:12'  [CAMBIAR DIA/MES!]
            date = str(predate[1])+"/"+str(predate[0])+"/"+str(predate[2])
            print("date " + date)
        except Exception as e:
            date = -1
            print(e)


        # Enter each leak (new page) NOW USE DRIVER, NOT LEAK 'l'

        try: 
            l.find_element_by_xpath("p/a").click()
            print("\nEntering leak...\n")

            # Save HTML each leak 
            leakSource = driver.page_source
            
            siteTitleFile = siteTitle.replace(" ","_").lower()
            
            fileToWrite = open("source_ragnar/ragnar_"+siteTitleFile+".html", "w")
            fileToWrite.write(leakSource)
            fileToWrite.close()
        except Exception as e:
            print(e)

        # 1) Tiene todo. Information = todos <p> hasta encontrar location
        # 2) No Information Si demás. Buscas demás y ya
        # 3) No Location ni link Si information. Information = todos <p>

        information = -1        # para añadir en DB si no encuentro nada
        location = -1
        link = -1

        try:
            allP = driver.find_elements_by_xpath("//div[@id='_tl_view']/p")
            #print("NUMBER Ps :" + str(len(allP)))
            if len(allP) > 10:
                nPs = 10
            else:
                nPs = len(allP)            # si muchos <p> limito a 10, si pocos cojo todos
            information = ''
            for j in range(nPs):     

                if 'Headquarters' in allP[j].text or 'Address' in allP[j].text:
                    location = allP[j].text
                    print("location: " + location)

                    for k in range(j-1):          # si hay location, info = principio ... location 
                        information += allP[k].text
                    print("information (yes location): " + information)

                if 'Website' in allP[j].text:
                    link = allP[j].text.replace('Website','')      # 'Website:www.abc.com' 
                    link = link.replace(':','')
                    print("link: " + link)
            
            if information == '':               # no hay location, info = todos <p>
                if len(allP) > 5:
                    nInfs = 5
                else:
                    nInfs = len(allP)                 # si muchos <p> limito info a 5, si pocos cojo todos
                
                for m in range(nInfs):
                    information += allP[m].text
                print("information (no location): " + information)
                
        except Exception as e:
            print(e)

        
        now = datetime.now()
        lastCrawledLeak = now.strftime("%m/%d/%Y, %H:%M:%S")
        print("lastCrawledLeak: " + lastCrawledLeak)

        ransomMoney = -1
        publishedPercentage = -1
        dataSize = -1
        id += 1

        # Insertar DB

        try:
            attack = [id,siteTitle,link,location,information,date,views,ransomMoney,publishedPercentage,dataSize,lastCrawledLeak,groupName]

            print("Inserting Values into ATTACK...")
            cur.execute("INSERT INTO attack VALUES(?,?,?,?,?,?,?,?,?,?,?,?);",attack)
            con.commit()
        except Exception as e:
            print(e)


        driver.get(siteLink)     # Return to main page
        leaks = driver.find_elements_by_xpath("//div[@class='content']/div[@class='card']")     # Get back lost reference

    # end for

    print('Returning to Families Site Page...')
    driver.get(familiesSite)
    time.sleep(10)






