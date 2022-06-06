from matplotlib import legend
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime



# Remove from l1, dates before first l2 date, and then get difference
def getMissingDates(l1,l2):

    l3 = []
    l1Fixed = []

    firstDate = datetime.strptime(l2[0], '%Y-%m-%d')

    # Drop dates before first time of that title
    for i in range(len(l1)):
        date = datetime.strptime(l1[i], '%Y-%m-%d')
        if date == firstDate or date > firstDate:
            l1Fixed.append(l1[i])

    # Calculate dates missing
    for i in range(len(l1Fixed)):
        if l1Fixed[i] not in l2:
            l3.append(l1Fixed[i])

    return l3
 


# HAVE ANY ATTACKS DISAPPEARED OVER RECRAWLS
def getDisappeared():

    df = pd.read_csv('attack.csv')

    print("Original len: " + str(len(df)))         # 19668

    # There are 22 dates total, at beginning random days. 

    # Join 14/03 and 15/03 (it was midnight)      
    date15 = datetime(2022, 3, 15)
    date15 = date15.strftime('%Y-%m-%d')                          # remove h:m:s

    for i in range(len(df)):
        dateString = df.at[i,'lastCrawledLeak']
        date = datetime.strptime(dateString, '%m/%d/%Y, %H:%M:%S')
        dateNoTime = date.strftime('%Y-%m-%d')                          # remove h:m:s

        # Turn 15/03 into 14/03
        if dateNoTime == date15:
            df.at[i,'lastCrawledLeak'] = "03/14/2022, 23:59:59"



    # Dates (no h:m:s) for each family crawl
    crawlingDates = {'CONTI': [], 'Hive': [], 'LockBit 2.0': [], 'Lorenz': [], 'Midas': [], 
    'Pysa': [], 'Quantum': [], 'Ragnar_Locker': [], 'RansomEXX': [], 'Snatch': []}   

    lastFamily = 'random'
    for i in range(len(df)):
        family = df.at[i,'groupName']

        dateString = df.at[i,'lastCrawledLeak']
        date = datetime.strptime(dateString, '%m/%d/%Y, %H:%M:%S')
        dateNoTime = date.strftime('%Y-%m-%d')                          # remove h:m:s

        if family != lastFamily:
            crawlingDates[family].append(dateNoTime)
        lastFamily = family

    print(crawlingDates)

    # Drop titles with no value: -1, NaN
    df = df[df.title != 1]
    df = df[df.title != '1']
    df = df[df.title != -1]
    df = df[df.title != '-1']
    df = df[df.title != -1.0]
    df = df[df.title != '-1.0']
    df = df.dropna()

    print("Len after dropping invalid titles: " + str(len(df)))         # 19463

    # DF sorted by titles
    df = df.sort_values(by=['title'])
    df = df.reset_index(drop=True)                           

    # If each title has each recrawl date for that family its first time crawl
    
    lastTitle = ""
    lastFamily = ""
    titleDates = []                     # list of all dates from same title

    disappearedTitles = []
    disappearedFamilies = []
    disappearedDates = []


    for i in range(len(df)):
        title = df.at[i,'title']
        family = df.at[i,'groupName']
        dateString = df.at[i,'lastCrawledLeak']
        
        dateAll = datetime.strptime(dateString, '%m/%d/%Y, %H:%M:%S')
        date = dateAll.strftime('%Y-%m-%d')                          # remove h:m:s
        
        if i != 0 and title != lastTitle:

            print("NEW LEAK\n")
            print(len(crawlingDates[lastFamily]))
            print(crawlingDates[lastFamily])
            print(len(titleDates))
            print(titleDates)

            remainingDates = getMissingDates(crawlingDates[lastFamily], titleDates)          # first list must be larger

            print("\nlen remainingDates: " + str(len(remainingDates)))
            print(remainingDates)
            print()
            for j in range(len(remainingDates)):
                disappearedTitles.append(lastTitle)                     # same title, same family, EACH OF THE MISSING DATES
                disappearedFamilies.append(lastFamily)
                disappearedDates.append(remainingDates[j])

            titleDates = []                     # restart list for next leak
            

        titleDates.append(date)                 # add existing date of same leak

        print("i = " + str(i) + " : "+ title + " --> " + family)

        lastTitle = title
        lastFamily = family

        
    #print(df[['title','groupName']].head(200))

    print("\n\n")
    print(len(disappearedTitles))                   # 3537
    print(len(disappearedFamilies))
    print(len(disappearedDates))

    #print(disappearedTitles)
    #print(disappearedFamilies)
    #print(disappearedDates)

    # Create DF with 3 lists of disappeared title, family, date
    dfSave = pd.DataFrame(list(zip(disappearedTitles, disappearedFamilies, disappearedDates)), columns =['title', 'family', 'date'])
    dfSave.to_csv("attackDisappeared.csv", index=False)  



# Get Graph from csv with disappeared dates from each title/family
def getDisappearedGraph():

    df = pd.read_csv('attackDisappeared.csv')
    
    df = df[['date','title']]

    df = df.groupby(['date']).count()
    print(df)

    ax = df.plot(legend=False)
    ax.set_xlabel("date")
    ax.set_ylabel("number of disappeared leaks")

    plt.tight_layout()
    plt.show()
    

# Get Families Graph from csv with disappeared dates from each title/family
def getDisappearedGraphFamilies():

    df = pd.read_csv('attackDisappeared.csv')
    
    df = df[['date','family']]

    df = pd.crosstab(df['date'],df['family'])

    print(df)
    ax = df.plot()

    ax.set_xlabel("date")
    ax.set_ylabel("number of disappeared leaks per family")

    plt.tight_layout()
    plt.show()
    


# Special Case: Lockbit. Count number of leaks with date AFTER crawl date (date will be published if you don't pay...)
def getDatesAfterCrawl():

    df = pd.read_csv('attack.csv')

    df = df[df.date != -1]
    df = df[df.date != '-1']
    df = df[df.date != -1.0]
    df = df[df.date != '-1.0']

    dates = []
    crawls = []
    families = []

    for i in range(len(df)):
 
        try:
            crawlString = df.at[i,'lastCrawledLeak']
            crawAll = datetime.strptime(crawlString, '%m/%d/%Y, %H:%M:%S')
            crawl = crawAll.strftime('%Y-%m-%d')                          # remove h:m:s    

            dateString = df.at[i,'date']
            dateAll = datetime.strptime(dateString, '%d/%m/%Y')
            date = dateAll.strftime('%Y-%m-%d')   

            family = df.at[i,'groupName']

            if date > crawl:
                dates.append(date)
                crawls.append(crawl)
                families.append(family)

        except Exception as e:
            print(e)
        

    # Create DF with 3 lists of disappeared title, family, date
    dfSave = pd.DataFrame(list(zip(dates, crawls, families)), columns =['date', 'crawl', 'family'])
    dfSave.to_csv("attackDatesAfterCrawl.csv", index=False)  



# Get Graph from csv with dates afetr crawl from Lockbit
def getDatesAfterCrawlGraph():

    df = pd.read_csv('attackDatesAfterCrawl.csv')
    
    print("len of dates after crawl: " + str(len(df)))      # 320

    df = pd.crosstab(df['crawl'],df['family'])              # all are Lockbit

    print(df)

    ax = df.plot()

    ax.set_xlabel("crawl")
    ax.set_ylabel("number of leaks to be published")

    plt.tight_layout()
    plt.show()
    



getDisappeared()

getDisappearedGraph()

getDisappearedGraphFamilies()

getDatesAfterCrawl()

getDatesAfterCrawlGraph()