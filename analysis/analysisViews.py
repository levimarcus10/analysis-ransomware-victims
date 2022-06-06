from inspect import stack
from opcode import stack_effect
from unicodedata import category
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time
import datetime



# NUMBER OF VIEWS (views)
def getViews():

    df = pd.read_csv('attack.csv')

    # Before I dropped duplicates and then I removed errors, here backwards

    print("Original len without dropping duplicates = " + str(len(df)))       # 19668

    # For same leak, number of views changes with re-crawls (drop later)
    dfSorted = df.sort_values(by=['views'])

    # Drop views with no value: -1, NaN
    dfSorted = dfSorted[dfSorted.views != -1.0]
    dfSorted = dfSorted.dropna()

    print(dfSorted['views'])
    print("After dropping error values (still duplicates) = " + str(len(dfSorted)))        # 11935

    '''
    with open("allSortedViews.txt", 'w') as f:
        for entry in dfSorted['views']:
            f.write(str(entry))
            f.write("\n")
    '''

    # Entries with same title, keep only highest view
    dfDropped = dfSorted.drop_duplicates('title', keep='last')
    print(dfDropped['views'])
    print("After dropping duplicates (keep highest) = " + str(len(dfDropped)))        # 994

    # Save attack with highest views
    dfDropped.to_csv("attackViews.csv",index=False)             # Avoid extra index column, already have ID



# Add to DF column with range of view value
def addRangeColumn(df):
    
    ranges = []
    for i in range(len(df)):
        views = df.at[i,'views']

        if views <= 100000:
            ranges.append('[0-100.000]')
        elif views <= 200000:
            ranges.append('[100.000-200.000]')
        elif views <= 300000:
            ranges.append('[200.000-300.000]')
        elif views <= 400000:
            ranges.append('[300.000-400.000]')
        elif views <= 500000:
            ranges.append('[400.000-500.000]')
        elif views <= 600000:
            ranges.append('[500.000-600.000]')
        elif views <= 700000:
            ranges.append('[600.000-700.000]')
        elif views <= 800000:
            ranges.append('[700.000-800.000]')
        elif views > 800000:
            ranges.append('[>800.000]')

    # Append list as row
    df['rangeViews'] = ranges
    return df



# Get Graph from saved CSV with sorted highest views [Graph by range]
def getViewsGraph():
    
    df = pd.read_csv('attackViews.csv')

    viewsList = df['views'].tolist()
    df = pd.DataFrame(viewsList, columns=["views"])                 # create new DF with views list

    # Group by range and count leaks [0 - 800.000] one has 10.035.608
    # 8 ranges of 100.000
    
    df = addRangeColumn(df)
    
    rangeList = df['rangeViews'].tolist()
    df = pd.DataFrame(rangeList, columns=["rangeViews"])                 # create new DF with range views list

    # Count time of each range
    dfCount = df.groupby(df.columns.to_list(),as_index=False).size()

    # Add unknown row in red
    dfUnknown = {'rangeViews': 'unknown', 'size': 1005}                   # 1005 = 1999 - 994
    dfCount = dfCount.append(dfUnknown, ignore_index=True)
    print(dfCount)

    color = len(dfCount)*['royalblue']
    color[-1] = 'firebrick'

    # Plot Bar Graph
    ax = dfCount.plot(kind='bar', x='rangeViews', y='size', legend=False, color=color, logy=True)
    ax.set_xlabel("range of views")
    ax.set_ylabel("number of leaks")
    
    for bar in ax.patches:
        
        ax.annotate(format(bar.get_height(), ''),
                    (bar.get_x() + bar.get_width() / 2,
                        bar.get_height()), ha='center', va='center',
                    size=10, xytext=(0, 8),
                    textcoords='offset points')

    plt.tight_layout()
    plt.show()
  


# Get Graph from saved CSV with sorted highest views [Graph by range with Families]
def getViewsGraphFamilies():
    
    df = pd.read_csv('attackViews.csv')

    # Group by range and combine with family
    
    df = addRangeColumn(df)

    dfCross = pd.crosstab(df['rangeViews'],df['groupName'], normalize='index')                   # Matrix [Range, Family]
    print(dfCross)

    # Plot Bar Chart
    ax = dfCross.plot.bar(stacked=True)                  # stacked so columns of same country overlap
    ax.legend(bbox_to_anchor=(1.0, 1.0))                  # move legend out of data
    ax.set_xlabel("range of views")
    ax.set_ylabel("percentage of leaks")
    
    plt.tight_layout()
    plt.show()



# Get Graph from saved CSV with number of average views per family --> boxplot
def getViewsFamiliesBoxplot():
    
    df = pd.read_csv('attackViews.csv')
    #print(df)

    # Boxplot
    ax = df.boxplot(column='views', by='groupName')
    ax.set_xlabel("family")
    ax.set_ylabel("views")
    ax.set_yscale('log')

    
    plt.tight_layout()
    plt.show()



# Get Graph from saved CSV --> Boxplot!
def getViewsGraphFamiliesAverage():
    
    df = pd.read_csv('attackViews.csv')

    df = df.groupby('groupName').mean()
    dfViews = df['views']
    
    # Plot Bar Graph
    dfViews.plot(kind='bar')

    plt.tight_layout()
    plt.show()


# Get Graph from saved CSV --> Table !
def getViewsGraphFamiliesTotal():
    
    df = pd.read_csv('attackViews.csv')

    df = df.groupby('groupName').sum()
    dfViews = df['views']
    print(dfViews)

    # Plot Bar Graph
    dfViews.plot(kind='bar')

    plt.tight_layout()
    plt.show()
    


# Calculate total and average number of views per family
def countViewsFamilies():
    
    df = pd.read_csv('attackViews.csv')

    # Total
    dfTotal = df.groupby('groupName').sum()
    print(dfTotal['views'])

    # Average
    dfAvg = df.groupby('groupName').mean()
    print(dfAvg['views'])


#getViews()

getViewsGraph()
getViewsGraphFamilies()

countViewsFamilies()   
getViewsFamiliesBoxplot()

#getViewsGraphFamiliesAverage()             # not used
#getViewsGraphFamiliesTotal()               # not used


print("END")