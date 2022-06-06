from turtle import pu
import pandas as pd
import matplotlib.pyplot as plt


# PUBLISHING FREQUENCY (publishedPercentage)
def getPublished():

    df = pd.read_csv('attack.csv')
    print("Len before dropping not valids = " + str(len(df)))       # 19668

    # Drop not valid titles and published
    df = df[df.title != '-1']
    df = df[df.publishedPercentage != '-1']
    df = df[df.publishedPercentage != '...']
    df = df.dropna()                                                # Drops rows where at least one elements is missing
    print("Len after dropping not valids = " + str(len(df)))        # 10334 

    # Count unique titles 
    uniqueTitles = df['title'].nunique()
    print("Number of unique titles = " + str(uniqueTitles))         # 851 (just to see value)

    # Sort by title (put together same leak recrawls)
    df = df.sort_values(by=['title'])
    df = df.reset_index(drop=True)                                  # update index with new order (access with .at)


    # Add column with change relative to first leak with same title = {less (-1), same (0), more (1)}
    # Create list, fill, add as column to DF
    trendList = []

    # Add list that count recrawls for each leak
    reCrawlList = []
    rc = 0
    
    # For each title, is there any that changes Published values? (first time add 'same' to list)
    lastTitle = df.at[0,'title']
    lastPublished = int(df.at[0,'publishedPercentage'])

    for i in range(len(df)):
        title = df.at[i,'title']
        published = int(df.at[i, 'publishedPercentage'])

        if title == lastTitle:                              # same leak
            if published < lastPublished:
                trendList.append(-1)
                #print("Less: " + str(published))
            elif published == lastPublished:
                trendList.append(0)
            else:
                trendList.append(1)
                #print("More: " + str(published))

            rc += 1
            reCrawlList.append(rc)

        else:                                               # new leak (write 'same')
            trendList.append(0)
            rc = 1
            reCrawlList.append(rc)

        lastTitle = title                                   # update with new last
        lastPublished = published

    print("Number of less (-1): " + str(trendList.count(-1)))
    print("Number of same (0): " + str(trendList.count(0)))
    print("Number of more (1): " + str(trendList.count(1)))
    
    # Add lists as columns to DF
    df['trend'] = trendList
    df['recrawl'] = reCrawlList

    # A few titles have 2 leaks on same page, unifies as 1 and counts 28 recrawls [max recrawls 14]
    df = df[df['recrawl'] < 15]

    # Fix crawl number of Lorenz (+1) and Quantum (+3). So at beginning only Conti
    for i in range(len(df)):
        try:
            family = df.at[i,'groupName']
            if family == 'Lorenz':
                rc = df.at[i,'recrawl']
                rc+=1
                df.at[i,'recrawl'] = rc
            elif family == 'Quantum':
                rc = df.at[i,'recrawl']
                rc+=3
                df.at[i,'recrawl'] = rc
        except Exception as e:
            print(e)
    
    # Save DF
    #df.to_csv("attackPublished.csv",index=False)                    # Avoid extra index column, already have ID




# Print Graph from saved csv with trend and recrawl columns
def getPublishedGraph():
     
    dfAll = pd.read_csv('attackPublished.csv')

    df = dfAll[["groupName", "trend", "recrawl"]]    
    print(df)

    # Group by recrawl and get average of all trend from that recrawl
    df = df.groupby(['recrawl']).mean('trend')
    print(df)

    df.plot()
    
    #plt.ylim([-1, 1])            # y axis with all possible values
    plt.tight_layout()
    plt.show()
    


# Print Families Graph from saved csv with trend and recrawl columns
def getPublishedGraphFamilies():
     
    dfAll = pd.read_csv('attackPublished.csv')

    df = dfAll[["groupName", "trend", "recrawl"]]    

    # Group by recrawl and get average of trend for each family on each recrawl

    df = pd.crosstab(df['recrawl'],df['groupName'], values = df['trend'], aggfunc = "mean")
    
    print(df)

    ax = df.plot()    
    plt.ylim([-1, 1])           
    plt.tight_layout()
    plt.show()
    

# Get nº incease, decrease, equal, average, desv tip
def getPublishedTable():

    dfAll = pd.read_csv('attackPublished.csv')

    print()
    print("Len of DF: " + str(len(dfAll)))

    df = dfAll[["groupName", "trend"]]    

    # Inc, Dec, Equal for each family
    dfCountFamilies = pd.crosstab(df['groupName'],df['trend'])    
    print(dfCountFamilies)

    # Inc, Dec, Equal in total
    dfCountTotal = df.groupby('trend').count()
    print(dfCountTotal)

    # Total mean and standard deviation
    dfMeanTotal = df[['trend']].mean()
    print(dfMeanTotal)

    dfStTotal = df[['trend']].std()
    print(dfStTotal)

    # Mean and std for each family
    dfMeanFamilies = df.groupby('groupName').mean()
    print(dfMeanFamilies)

    # Mean for each family
    dfStFamilies = df.groupby('groupName').std()
    print(dfStFamilies)


getPublished()

#getPublishedGraph()                   # not used
#getPublishedGraphFamilies()           # not used

getPublishedTable()