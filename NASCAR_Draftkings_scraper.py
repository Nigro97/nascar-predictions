#Scraping NASCAR Draftkings data from frcs.pro
import urllib.request as urllib
from bs4 import BeautifulSoup
import pandas as pd
import time
import random

def get_race_list(soup):
    """input html soup, return list of race names by isolating correct tag"""
    race_string = soup.find("div", class_="dropdown periodSelectionDropDown").get_text()
    races = race_string.splitlines()[6:]
    race_list = []
    for race in races:
        race_list.append(race[0:race.find(" (")])
    return race_list

def get_soup(url):
    """Input website URL, open site, and read html which is returned"""
    html = urllib.urlopen(url)
    soup = BeautifulSoup(html)
    html.close()
    return soup

def get_headers(soup):
    """Input html soup, find all abbr tags, put text from them in a list which will become a dataframe header"""
    headers = soup.find_all("abbr")
    df_header = []
    for header in headers:
        df_header.append(header.get_text())
    return df_header

def get_stats(soup, header):
    """Input html soup, get text from all tbody tags, return data separated by new lines in list of lists by line"""
    tbody = soup.find("tbody")
    #tbody tags contain the tabular data that can be split into lines
    lines = tbody.get_text().splitlines()

    row = []
    data = []
    for line in lines:
        if line != "":
            #lots of empty text that needs to be removed
            row.append(line.strip())
            if len(row) == len(header):
                #create next list when reaching the end of one line
                data.append(row)
                row = []
    return data

def create_df(data, header):
    """Input list of lists and header list to create a dataframe which is returned"""
    df = pd.DataFrame(data, columns = header)
    df.set_index("Driver")
    return df

def stats_urls(soup):
    ul_tag = soup.find("ul", class_ = "list-unstyled sibling-links")
    a_tags = ul_tag.find_all("a")
    urls = []
    for tag in a_tags:
        href = tag.get("href")
        if href.startswith("http"):
            urls.append(href)
    return urls

#obtaining perfect lineup data for race from linestarapp website
lineup_url = "https://www.linestarapp.com/Perfect/Sport/NAS/Site/DraftKings/PID/307"
lineup_soup = get_soup(lineup_url)
race_names = get_race_list(lineup_soup)

#obtaining race statistics from frcs website
stats_url = "https://frcs.pro/dfs/draftkings/race-fantasy-points/2020/daytona-international-speedway/daytona-500/"
stats_soup = get_soup(stats_url)
df_header = get_headers(stats_soup)
stats_data = get_stats(stats_soup, df_header)
df = create_df(stats_data, df_header)

#obtain urls for individual race statistics
race_urls = stats_urls(stats_soup)
for url in race_urls[5:]:
    race_soup = get_soup(url)
    race_data = get_stats(race_soup, df_header)
    race_df = create_df(race_data, df_header)
    df = df.append(race_df)
    time.sleep(random.randint(2,6))
print(df)
