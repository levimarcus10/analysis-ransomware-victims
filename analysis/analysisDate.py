from cProfile import label
from matplotlib import legend
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time
import datetime
import scipy.stats as s


# WHEN HAVE THE ATTACKS OCCURED (date)
def getDates():

    df = pd.read_csv('attack.csv')

    print("Original len without dropping duplicates = " + str(len(df)))       # 19668

    # Drop duplicates from dataframe   
    df.drop_duplicates('title', inplace=True, ignore_index=True)      # don't drop by date, there could be attacks on same date

    print("After dropping duplicates = " + str(len(df)))        # 1999

    # Drop dates with no value
    df = df[df.date != '-1']
    df = df[df.date != '00/00/2000']
    
    print("After dropping '-1' = " + str(len(df)))      


    # Convert strings to dates
    df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y', errors='coerce')             # ignore errors, some dates are correct

    # Sort from earliest to laters (works fine)
    dfSorted = df.sort_values(by=['date'])

    '''
    with open("allSortedDates.txt", 'w') as f:
        for entry in dfSorted['date']:
            f.write(str(entry))
            f.write("\n")
    '''

    # Eliminate NaT from conversion, date but bad format (only 20)
    dfSorted = dfSorted.dropna()
    print(dfSorted['date'])

    print("After dropping 'NaT' = " + str(len(dfSorted)))      # 1868

    # Save attack sorted by dates
    #dfSorted.to_csv("attackDates.csv",index=False)        # Avoid extra index column, already have ID



# Get Graph from saved CSV sorted only with valid dates [Basic Graph]
def getDatesGraph():
    
    df = pd.read_csv('attackDates.csv')
    #print(df['date'])

    # Create column containing month (if not each day apears in graph)
    df['month'] = pd.to_datetime(df['date']).dt.to_period('M')


    # Add 2020-02, 2020-03 with 0 (2020-01 has 6)
    
    # Create 'false' 2020-02 and 03 from fist two rows of 2020-01
    df.at[0,'month'] = '2020-02'
    df.at[1,'month'] = '2020-03'

    # Count time of each month
    dfCount = df.groupby(df['month'].to_list(),as_index=False).size()

    # Re-set correct numbers
    dfCount.at[0,'size'] = 6
    dfCount.at[1,'size'] = 0
    dfCount.at[2,'size'] = 0

    # Add unknown row in red
    dfUnknown = {'index': 'unknown', 'size': 131}                   # 131 = 1999 - 1868
    dfCount = dfCount.append(dfUnknown, ignore_index=True)
    print(dfCount)

    color = len(dfCount)*['royalblue']
    color[-1] = 'firebrick'

    # Plot Bar Graph
    ax = dfCount.plot(kind='bar', x='index', y='size', legend=False, color=color)
    ax.set_xlabel("month")
    ax.set_ylabel("number of leaks")

    plt.tight_layout()
    plt.show()
    


# Get Graph from saved CSV sorted only with valid dates [PDF and CDF Graph]
def getDatesGraphPDFandCDF():
    
    df = pd.read_csv('attackDates.csv')
    #print(df['date'])

    # Create column containing month (if not each day apears in graph)
    df['month'] = pd.to_datetime(df['date']).dt.to_period('M')


    # Add 2020-02, 2020-03 with 0 (2020-01 has 6)    

    # Create 'false' 2020-02 and 03 from fist two rows of 2020-01
    df.at[0,'month'] = '2020-02'
    df.at[1,'month'] = '2020-03'

    # Count time of each month
    dfCount = df.groupby(df['month'].to_list(),as_index=False).size()

    # Re-set correct numbers
    dfCount.at[0,'size'] = 6
    dfCount.at[1,'size'] = 0
    dfCount.at[2,'size'] = 0

    print(dfCount)

    # Don't add unknown (df already has only correct dates)

    # Plot PDF + CDF Graphs

    # getting data of the histogram
    count, bins_count = np.histogram(dfCount['size'], bins=10)
    
    # finding the PDF of the histogram using count values
    pdf = count / sum(count)
    
    # using numpy np.cumsum to calculate the CDF
    # We can also find using the PDF values by looping and adding
    cdf = np.cumsum(pdf)
    
    # plotting PDF and CDF
    plt.plot(bins_count[1:], pdf, color="red", label="PDF")
    plt.plot(bins_count[1:], cdf, label="CDF")
    plt.legend()

    plt.ylabel("month probability")
    plt.xlabel("number of registerd leaks")

    #plt.tight_layout()
    plt.show()



# Get Graph from saved CSV sorted only with valid dates [Graph with Families]
def getDatesGraphFamilies():
    
    df = pd.read_csv('attackDates.csv')

    # Create column containing month (if not each day apears in graph)
    df['month'] = pd.to_datetime(df['date']).dt.to_period('M')

    # Count times of each month and for each month each family
    dfCount = df.groupby(['month','groupName']).size()
    print(dfCount)

    dfCross = pd.crosstab(df['month'],df['groupName'], normalize='index')                   # Matrix [Month, Family]
    print(dfCross)

    # Plot Bar Chart
    ax = dfCross.plot.bar(stacked=True)                  # stacked so columns of same country overlap
    ax.legend(bbox_to_anchor=(1.0, 1.0))                     # Move legend out of data
    ax.set_xlabel("month")
    ax.set_ylabel("percentage of leaks")
    plt.tight_layout()
    plt.show()



getDates()

getDatesGraph()

getDatesGraphPDFandCDF()

getDatesGraphFamilies()

print("END")