from cmath import log
import json
from operator import index
from traceback import print_tb
from unicodedata import category
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import requests
import shutil


# TYPES OF ORGANIZATIONS: link      [execute in URL-cat project] -> [virustotal.com]
def getCategories():

    df = pd.read_csv('attack.csv')

    print("Len before dropping duplicates = " + str(len(df)))       # 19668

    # Drop duplicates from dataframe
    df.drop_duplicates('link', inplace=True, ignore_index=True)         # if two rows have same link, drop one (-1 eliminated)

    print("Len after dropping duplicates = " + str(len(df)))        # 1953

    # Fix link format and update in dataframe
    for i in range(len(df)):
        
        link = df.at[i,'link']
        #print(link)

        if '.onion' in link:                 
            if '/page/' in link:      
                parts = link.split('/page/')
                link = parts[1]
            else: 
                parts = link.split('.onion/')
                link = parts[1]

        if link.startswith("http"):                 # Only works without http(s):// - www is fine
            firstBar = link.find('/')
            cut = firstBar + 2
            link = link[cut : :]                    # from after second '/' to end

        if link[-1] == '/':                         # Not working if ends with '/' 
            link = link.replace('/','')

        #print(link)
        df.at[i,'link'] = link         


    # Create DF with Category from each fixed link -> fill txt as you go, virustotal stops daily after 500
    
    shutil.copy('categoriesALLsofar.txt','categoriesALLsofarORIGINAL.txt')

    f = open('categoriesALLsofar.txt','a')
    lines = countFileLines("categoriesALLsofar.txt")            # To know where to continue at

    for i in range(lines, len(df)):
        
        print("i = " + str(i))

        myLink = df.at[i,'link']

        cat = getName(myLink)                       # Call Function
        #cat = getNameTest(myLink)                  # Enter manually category for testing

        if cat == -2:                               # Return -2 when quota exceeded
            break         
        
        f.write(str(cat))
        f.write("\n")                               # Next time it omits empty space and write exactly after  

        print(str(myLink) + " - " + str(cat))


# For given link, returns the category from virus total [4/min, 500/day = execution/day 125 mins = 2h 5mins]
def getName(link):

    url = "https://www.virustotal.com/api/v3/domains/"+link         # Only works without http(s), www is ok

    headers = {
        "Accept": "application/json",
        "x-apikey": "1053e4226a4e3bd2de8a072c2ad9c2a3a3f5a4afe177204821dfdffda457b3de"         # levmarc97@gmail
        #"x-apikey": "5a3d9b116fe76dabf23aaefa986cd0c76c624c2b7ec5c446082bcdadf248b8f4"          # levmarc97@hotmail
    }

    response = requests.get(url, headers=headers)
    
    jsonData = json.loads(response.text)                           # Convert from text to json

    # Cases: Category found, Category found empty, NotFoundError, QuotaExceededError #

    category = -1       # default

    firstKey = list(jsonData.keys())[0]

    # NotFoundError (-1) or QuotaExceededError (-2)
    if firstKey == 'error':
        
        print(jsonData)
        errorCode = jsonData['error']['code']

        if errorCode == 'NotFoundError':
            print("Category Not Found ")
            return -1

        elif errorCode == "QuotaExceededError":
            print("Quota exceeded ")
            return -2

        else:
            return -1

    # Category found      
    else:
        jsonCats = jsonData['data']['attributes']['categories']     # {'key': 'value', 'key': 'value', ...} with categories

        # Category found empty (-1)
        try: 
            category = list(jsonCats.values())[0]                   # first value
        except Exception as e: 
            print("Category empty: ")
            print(jsonCats)
            return -1

    return category


def countFileLines(fileName):

    count = 0

    f = open(fileName,'r')
    for line in f:
        if line != "\n":
            count += 1
    f.close()

    return count


# For testing only
def getNameTest(link):

    print(link)
    cat = input("Enter category of link: ")
    return cat


# Fix Categories (join unknown and '-1', all business and economy, goverment, etc.)
def fixCategories(dfCat):

    for i in range(len(dfCat)):
        
        cat = dfCat.at[i,'category']
        dfCat.at[i,'category'] = cat.lower()              # all to lower case
        cat = dfCat.at[i,'category']

        if cat == 'unknown':
            dfCat.at[i,'category'] = '-1'
        elif 'blogs' in cat:
            dfCat.at[i,'category'] = 'blog'
        elif 'business' in cat or 'economy' in cat:
            dfCat.at[i,'category'] = 'business and economy'
        elif 'government' in cat:
            dfCat.at[i,'category'] = 'government'
        elif 'health' in cat:
            dfCat.at[i,'category'] = 'health'
        elif 'travel' in cat:
            dfCat.at[i,'category'] = 'travel'
        elif 'shopping' in cat:
            dfCat.at[i,'category'] = 'shopping'
        elif 'education' in cat or 'educational' in cat:
            dfCat.at[i,'category'] = 'education'
        elif 'finance' in cat or 'financial' in cat:
            dfCat.at[i,'category'] = 'finance'
        elif 'information' in cat:
            dfCat.at[i,'category'] = 'information technology'
        elif 'media' in cat:
            dfCat.at[i,'category'] = 'news and media'
        elif 'shopping' in cat:
            dfCat.at[i,'category'] = 'shopping'

    return dfCat



# Get Graph from saved txt with categories and '-1' (basic Graph)
def getCategoriesGraph():

    # Once txt has all categories...

    # To compare with other data, update link position with category from txt in original DF
    # For now just get category column 
    
    # Use saved txt and save as csv
    #dfCat = pd.read_fwf('categoriesALLsofar.txt')
    #dfCat.to_csv("categoriesALL.csv", index=False)             # avoid index column


    # Use saved csv (CHOOSE !)
    #dfCat = pd.read_csv('categoriesAll_git.csv')
    dfCat = pd.read_csv('categoriesAll_virustotal.csv')
            
    # Fix categories function (virustotal)
    dfCat = fixCategories(dfCat)

    # Count each Category
    dfCat = dfCat.groupby(dfCat.columns.to_list(),as_index=False).size()
    #print(dfCat)

    # Drop row category = -1                        (NO !)
    #dfCat = dfCat.drop([dfCat.index[0]])
    #print(dfCat)

    nonCat = dfCat.at[0,'size']
    total = dfCat['size'].sum()

    print("Number of categorized organizations: " + str(total - nonCat))        
    print("Number of non categorized organizations (-1): " + str(nonCat))
    print("Total number of unique organizations (unique link): " + str(total))

    # Change -1 for 'unknown'
    dfCat.at[0,'category'] = 'unknown'
    #print(dfCat)

    # Sort from biggest
    dfCat = dfCat.sort_values('size')       # ascending=False
    print(dfCat)

    # Plot Bar Chart (unknown in red)
    color = len(dfCat)*['royalblue']
    color[-2] = 'firebrick'

    ax = dfCat.plot(kind='barh', x='category', y='size', color=color, legend=False, logx=True)     # add logx=True for log scale
    ax.set_xlabel("number of leaks")
    plt.tight_layout()
    plt.show()
    



# Get Graph from saved txt with categories and '-1' and compare with other data (Families)
def getCategoriesGraphFamilies():

    # To compare with other data, add new column with categories in original DF

    # Use saved csv
    #dfCat = pd.read_csv('categoriesAll_git.csv')
    dfCat = pd.read_csv('categoriesAll_virustotal.csv')
            
    df = pd.read_csv('attack.csv')
    df.drop_duplicates('link', inplace=True, ignore_index=True)       

    # Fix categories function (virustotal)
    dfCat = fixCategories(dfCat)

    # Add column to DF and change -1 for unknown
    for i in range(len(dfCat)): 
        if dfCat.at[i,'category'] == '-1':
            dfCat.at[i,'category'] = 'unknown'

    categoryList = dfCat['category'].tolist()

    df['category'] = categoryList

    # By Percentages of each Family (all same length)
    dfCross = pd.crosstab(df['category'],df['groupName'], normalize='index')       # normalize='index' all over 100%    
    print(dfCross)

    # Alphabetically descending
    dfCross = dfCross.sort_values('category', ascending=False)       

    # Plot Bar Chart
    ax = dfCross.plot.barh(stacked=True)                  # stacked so columns of same country overlap
    ax.legend(bbox_to_anchor=(1.0, 1.0))                     # Move legend out of data
    ax.set_xlabel("percentage of leaks")
    plt.tight_layout()
    plt.show()



getCategories()

getCategoriesGraph()

getCategoriesGraphFamilies()

print("END\n")


