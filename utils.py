import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# Enter each leak site from main page
def enter_site(driver, siteName): 
    groups = driver.find_elements_by_tag_name("div")
    for g in groups:
        try:
            thisGroup = g.find_elements_by_tag_name("div")
            if siteName in thisGroup[0].text:
                groupName = thisGroup[0].text
                onionVersion = thisGroup[1].text
                siteLink = thisGroup[2].find_element_by_tag_name("a").get_attribute("href")
        except:
            nothing = 0
    return groupName, onionVersion, siteLink



# Count leaks of last crawl for each family
def countLeaksFamily():

    df = pd.read_csv('attack.csv')

    df = df.drop_duplicates('title', keep='last')
    
    df= df.groupby('groupName').size()
    
    print(df)
