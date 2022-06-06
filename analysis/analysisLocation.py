from inspect import stack
from opcode import stack_effect
from unicodedata import category
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time



# COUNTRIES OF ORGANIZATIONS: location and TLD of links
def getLocations():

    df = pd.read_csv('attack.csv')
 
    # Drop duplicates from dataframe   
    df.drop_duplicates('title', inplace=True, ignore_index=True)      # if drop by location, all location='-1' will be dropped, could have TLD


    # Update DF with Country by finding name in location OR by finding TLD in link ('country-codes-tlds.csv') OR by US States

    dfCountryAndTLD = pd.read_csv('country-codes-tlds.csv')      # column = 'country', 'tld'
    dfStates = pd.read_csv('states.csv')
    countLocations = 0
    countTLDs = 0
    countStates = 0
    countNotFound = 0               # Location -1 or Not Found

    for i in range(len(df)):
        
        # Find Country name directly in location
        location = df.at[i,'location']
        print("----------------------")
        print(str(location))     
            
        foundName = False
        foundTLD = False
        foundState = False

        for j in range(len(dfCountryAndTLD)):
            country = str(dfCountryAndTLD.at[j,'country'])
            if location is not np.NaN and country != 'nan' and country in location:   # location=NaN or country='nan' gives an error       
                df.at[i,'location'] = country
                countLocations += 1
                print("1.-----> " + str(country) + "\n\n")
                foundName = True
                break
        

        # If Country not found in list, try with TLD in link
        if not foundName:
            
            link = df.at[i,'link']
            print(str(link))   

            # Get final part of link (.es)
            link = link.strip()
            linkParts = link.split(".")
            linkTLD = "." + linkParts[-1]
            if "/" in linkTLD: linkTLD = linkTLD.replace("/","")            # some end in '.es/'

            for k in range(len(dfCountryAndTLD)):
                possibleTLD = str(dfCountryAndTLD.at[k,'tld'])
                if possibleTLD == linkTLD:
                    country = dfCountryAndTLD.at[k,'country']               # Get corresponding Country of TLD
                    df.at[i,'location'] = country
                    countTLDs += 1
                    print("2.-----> " + str(country) + "\n\n")
                    foundTLD = True
                    break


        # If Country not found in list & TLD not found, try with US States in location (states.csv)
        if not foundName and not foundTLD:
            
            for j in range(len(dfStates)):
                stateName = str(dfStates.at[j,'State'])
                stateCode = str(dfStates.at[j,'Abbreviation'])
                if location is not np.NaN and location != 'nan':            # Same error a country list
                    if stateName in location or stateCode in location:
                        df.at[i,'location'] = 'USA'                             # Only USA States 
                        countStates += 1
                        print("3.----->  USA !!! \n\n")
                        foundState = True
                        break

        
        # Location not found in any way, write -1
        if not foundName and not foundTLD and not foundState:
            countNotFound += 1
      

    print("Finished Calculating Countries...")

    print("Number of countries obtained by name: " + str(countLocations))                       # 409
    print("Number of countries obtained by TLD: " + str(countTLDs))                             # 453
    print("Number of countries obtained by US Sates: " + str(countStates))                      # 159

    print("Total number of unique organizations with location not found or -1: " + str(countNotFound))     # 65       

    print("Total number of unique organizations: " + str(len(df)))                              # 1999

    # SAVE DF
    #df.to_csv("attackCountries.csv",index=False)        # Avoid extra index column, already have ID



# Get Graph from saved CSV with location = {Country, -1}
def getLocationsGraph():
    
    dfAttack = pd.read_csv('attackCountries.csv')

    # Maintain original order with '-1', to compare with family type or other data   

    locationList = dfAttack['location'].tolist()
    df = pd.DataFrame(locationList, columns=["location"])        # create new DF with country list

    # Fix Countries (USA, Catalonia, Galicia, Hong Kong, Unknown)
    for i in range(len(df)):
        location = df.at[i,'location']
        if location == 'USA':
            df.at[i,'location'] = 'United States'
        elif location == 'Catalonia' or location == 'Galicia':
            df.at[i,'location'] = 'Spain'
        elif location == 'Hong Kong':
            df.at[i,'location'] = 'China'
        elif location == '-1':
            df.at[i,'location'] = 'Unknown'
 

    # Count times of each location and sort
    df = df.groupby(df.columns.to_list(),as_index=False).size()
    df = df.sort_values('size', ascending=False)                                         # ascending=False
    print(df)

    # Plot Bar Chart (unknown in red)
    color = len(df)*['royalblue']
    color[0] = 'firebrick'

    ax = df.plot(kind='bar', x='location', y='size', color=color, legend=False, logy=True)     # add log[x|y]=True for log scale
    ax.set_ylabel("number of leaks")
 
    plt.tight_layout()
    plt.show()
    


# Get Graph from saved CSV with location = {Country, -1} and Combine Locations with Family
def getLocationsGraphFamilies():
    
    df = pd.read_csv('attackCountries.csv')

    # Fix Countries (USA, Catalonia, Galicia, Hong Kong)
    for i in range(len(df)):
        location = df.at[i,'location']
        if location == 'USA':
            df.at[i,'location'] = 'United States'
        elif location == 'Catalonia' or location == 'Galicia':
            df.at[i,'location'] = 'Spain'
        elif location == 'Hong Kong':
            df.at[i,'location'] = 'China'
        elif location == '-1':
            df.at[i,'location'] = 'Unknown'
  

    # By Percentages of each Family (all same length)
    dfCross = pd.crosstab(df['location'],df['groupName'], normalize='index')       # normalize='index' all over 100%    

    # Plot Bar Chart
    ax = dfCross.plot.bar(stacked=True)                  # stacked so columns of same country overlap
    ax.legend(bbox_to_anchor=(1.0, 1.0))                  # move legend out of data
    ax.set_ylabel("percentage of leaks")
    
    plt.tight_layout()
    plt.show()



getLocations()

getLocationsGraph()

getLocationsGraphFamilies()

print("END")