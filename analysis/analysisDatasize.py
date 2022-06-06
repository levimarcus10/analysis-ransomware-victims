import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# MOST DATA STOLEN (dataSize)
def getDatasize():

    df = pd.read_csv('attack.csv')
    print("Original len without dropping = " + str(len(df)))       # 19668

    # Drop rows with invalid dataSize
    df = df.sort_values(by=['dataSize'])

    df = df[df.dataSize != -1.0]
    df = df[df.dataSize != '-1.0']
    df = df[df.dataSize != -1]
    df = df[df.dataSize != '-1']
    df = df[df.dataSize != '0.00 B']
    df = df[df.dataSize != '0.00B']
    df = df[df.dataSize != '0.00b']

    print("Original len after dropping invalids = " + str(len(df)))       # 10307

    # Entries with same title, keep only highest size
    df = df.drop_duplicates('title', keep='last')

    print("After dropping duplicates (keep highest) = " + str(len(df)))        # 791

    df = df.reset_index(drop=True)          # to do df.at[]

    # Add column with fixed and unified dataSize format -> all in bytes
    # 1 KB, 1 MB, 1 GB, 1 TB, 1KB, 1MB, 1GB, 1TB
    
    dataList = []
    kbList = ['KB', 'Kb', 'kB', 'kb']
    mbList = ['MB', 'Mb', 'mB', 'mb']
    gbList = ['GB', 'Gb', 'gB', 'gb']
    tbList = ['TB', 'Tb', 'tB', 'tb']
    allList = ['k','K','m','M','g','G','t','T']             # some are only '1G'

    factor = 'b'
    num = 0

    for i in range(len(df)):
        ds = df.at[i,'dataSize']

        # Add 'B' to '1G'
        if ds[-1] in allList: ds = ds + 'B'

        #print(ds + " = ")

        if ' ' in ds:                                      # Number' 'Bytes
            parts = ds.split()
            num = float(parts[0])
            factor = parts[1]
        else:                                              # NumberBytes
            factor = ds[-2] + ds[-1]   
            num = ds.translate({ord(ds[-2]): None})
            num = float(num.translate({ord(ds[-1]): None}))

        #print(str(num) + " + " + factor)

        if factor in kbList:
            dataList.append(num/1024)
        elif factor in mbList:
            dataList.append(num)                  # (num*1024*1024)  
        elif factor in gbList:
            dataList.append(num*1024)            
        elif factor in tbList:
            dataList.append(num*1024*1024)
        else:
            dataList.append(num)

        
    # Add lists as columns to DF
    df['dataFixed'] = dataList

    # Save DF
    df.to_csv("attackDatasize.csv",index=False)                    # Avoid extra index column, already have ID


# Add to DF column with range of dataSize value (all in bytes)
def addRangeColumn(df):
    
    ranges = []
    for i in range(len(df)):
        ds = df.at[i,'dataFixed']

        if ds <= pow(10,-2):
            ranges.append('[0.001-0.01]')            # ('[10^3-10^4]')
        elif ds <= pow(10,-1):
            ranges.append('[0.01-0.1]')
        elif ds <= pow(10,0):
            ranges.append('[0.1-1]')
        elif ds <= pow(10,1):
            ranges.append('[1-10]')
        elif ds <= pow(10,2):
            ranges.append('[10-100]')
        elif ds <= pow(10,3):
            ranges.append('[100-1,000]')
        elif ds <= pow(10,4):
            ranges.append('[1,000-10,000]')
        elif ds <= pow(10,5):
            ranges.append('[10,000-100,000]')
        elif ds <= pow(10,6):
            ranges.append('[100,000-1,000,000]')        
        elif ds > pow(10,6):
            ranges.append('[1,000,000-10,000,000]')

    # Append list as row
    df['dataRange'] = ranges
    return df


# Get Graph from csv with dataSize fixed all in MEGAbytes column
def getDatasizeGraph():

    df = pd.read_csv('attackDatasize.csv')

    # Sort
    df = df.sort_values(by=['dataFixed'])
    df = df.reset_index(drop=True)        

    dataList = df['dataFixed'].tolist()
    df = pd.DataFrame(dataList, columns=["dataFixed"])                 # create new DF with dataSize list

    # Group by range [10^3 ... 10^12]
    df = addRangeColumn(df)

    rangeList = df['dataRange'].tolist()
    df = pd.DataFrame(rangeList, columns=["dataRange"])                 # create new DF with range views list

    # Count time of each range
    df = df.groupby(df.columns.to_list(),as_index=False).size()

    print(df)

    # Reorder rows
    df = df.reindex([0,1,2,5,7,9,4,6,8,3]) 
    df = df.reset_index(drop=True)        

    print(df)
    
    # Add unknown row in red
    dfUnknown = {'dataRange': 'unknown', 'size': 1208}                   # 1208 = 1999 - 791
    df = df.append(dfUnknown, ignore_index=True)

    color = len(df)*['royalblue']
    color[-1] = 'firebrick'

    # Plot Bar Graph
    ax = df.plot(kind='bar', x='dataRange', y='size', legend=False, color=color, logy=True)
    ax.set_xlabel("range of megabytes")
    ax.set_ylabel("number of leaks")

    for bar in ax.patches:
        
        ax.annotate(format(bar.get_height(), ''),
                    (bar.get_x() + bar.get_width() / 2,
                        bar.get_height()), ha='center', va='center',
                    size=10, xytext=(0, 8),
                    textcoords='offset points')

    plt.tight_layout()
    plt.show()



# Get Graph from csv with dataSize "fixed all in bytes" column [Graph by range with Families]
def getDatasizeGraphFamilies():
    
    df = pd.read_csv('attackDatasize.csv')

    # Group by range and combine with family
    df = addRangeColumn(df)   

    df = pd.crosstab(df['dataRange'],df['groupName'], normalize='index')            # Matrix [Range, Family]
    print(df)

    # Reorder rows
    
    df0 = df.iloc[0] 
    df1 = df.iloc[1]
    df2 = df.iloc[2]
    df3 = df.iloc[3] 
    df4 = df.iloc[4]
    df5 = df.iloc[5]
    df6 = df.iloc[6] 
    df7 = df.iloc[7]
    df8 = df.iloc[8]
    df9 = df.iloc[9]

    #  df = df.reindex([0,1,2,5,7,9,4,6,8,3]) Can't be used in crosstab
    df = df.append(df0)   
    df = df.append(df1)   
    df = df.append(df2)   
    df = df.append(df5)   
    df = df.append(df7)   
    df = df.append(df9)   
    df = df.append(df4)   
    df = df.append(df6)   
    df = df.append(df8)   
    df = df.append(df3)   

    df = df[10:]
    print(df)

    # Plot Bar Chart
    ax = df.plot.bar(stacked=True)                        # stacked so columns of same country overlap
    ax.legend(bbox_to_anchor=(1.0, 1.0))                  # move legend out of data
    ax.set_xlabel("range of megabytes")
    ax.set_ylabel("percentage of leaks")
    
    plt.tight_layout()
    plt.show()



# Calculate total and average number of datasize per family ['dataFixed']
def countDatasizeFamilies():
    
    df = pd.read_csv('attackDatasize.csv')

    # Total
    dfTotal = df.groupby('groupName').sum()
    print(dfTotal['dataFixed'])

    # Average
    dfAvg = df.groupby('groupName').mean()
    print(dfAvg['dataFixed'])




# Get Boxplot from saved CSV 
def getDatasizeFamiliesBoxplot():
    
    df = pd.read_csv('attackDatasize.csv')
    print(df)

    # Boxplot
    ax = df.boxplot(column='dataFixed', by='groupName')
    ax.set_xlabel("family")
    ax.set_ylabel("amount of data")
    ax.set_yscale('log')

    plt.tight_layout()
    plt.show()



getDatasize()

getDatasizeGraph()

getDatasizeGraphFamilies()

countDatasizeFamilies()

getDatasizeFamiliesBoxplot()