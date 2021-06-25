import requests
from bs4 import BeautifulSoup as bs
import re, datetime
import pandas as pd
import pickle  
import sqlite3
from db import get_last_date, df_2_db, get_oldest_date
import re

pk_file = "./files/pikle.pk" #Pickle file to mail later
pd.set_option('display.max_colwidth', -1) #Pandas tuncates on raspberry pi. 
db = './files/db.sql' #We always need a DB

#some job sites are iffy when it comes to headers so spoof chrome
headers = {
"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9", 
"Accept-Encoding": "gzip, deflate", 
"Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8", 
"Dnt": "1", 
"Upgrade-Insecure-Requests": "1", 
"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36", 
}

#Set up jobs.ie
url = 'https://www.jobs.ie/linux-jobs'
r = requests.get(url, headers = headers)
soup = bs(r.content, 'html.parser')
data = soup.find_all('div', {'class':"job-details-header serp-item default"}) # Pull down only the job sections

#Set up irishjobs.ie
url2 = "https://www.irishjobs.ie/ShowResults.aspx?Keywords=linux&autosuggestEndpoint=%2Fautosuggest&Location=0&Category=&Recruiter=Company&Recruiter=Agency&btnSubmit=Search"
r2 = requests.get(url2, headers = headers)
soup2 = bs(r2.content, 'html.parser')
# data2 = soup2.find_all('div', {'class':'module job-result'}) #Weirdly wont work on python 3.5
data2 = soup2.find_all('div', {'class':  re.compile(r'module job-result')}) #Works on python 3.5 but seems slower

year = datetime.datetime.now().strftime("%Y")

def day_date(x = "1 Day ago"):
    #Ago is not a date so make it one
    s = x.lower().replace('day ', 'days ')
    parsed_s = [s.split()[:2]]
    time_dict = dict((fmt,float(amount)) for amount,fmt in parsed_s)
    dt = datetime.timedelta(**time_dict)
    past_time = datetime.datetime.now() - dt
    parsed_date = past_time.strftime("%d/%m/%Y")
    return parsed_date

def tidy_date(_input = "2 Jun 2021"):
    #Takes the days in months and makes it more standard
    d = datetime.datetime.strptime(_input, '%d %b %Y')
    return d.strftime("%d/%m/%Y")

def today():
    #have a guess
    return datetime.datetime.now().strftime("%d/%m/%Y")

def convert_comp(txt):
    #Converts company text and removes - and numbers
    if "-" in txt:
        d = txt.split("-")
        if d[-1].isdigit():
            d.pop()
            return "-".join(d)
        else:
            return txt
    else:
        return txt

def jobsie(a):
    #get a load of shit from jobs.ie
    for i in data:
        job_title = i.find('h2').text
        comp = i.find('a').get('href').replace('/', '')
        url = i.find_all('a')[1].get('href')
        location = i.find('dd', {'class':'fa-map-marker'}).text
        updated = i.find('dd', {'class':'fa-clock-o'}).text
        site = "jobs.ie"
        jobID = url.replace('&', '=').split('=')[1]
        lastDate = get_oldest_date(jobID)
        a.append([job_title, url, location, comp, updated, site, jobID, lastDate])

def irishjobs(a):
    #get a load of shit from irishjobs.ie
    for x in data2:
        title = x.find_all('a')[1].text
        url = "https://www.irishjobs.ie"  + x.find_all('a')[1].get('href')
        location = x.find('li', {'class':'location'}).find('a').text
        comp = x.find('h3', {'itemprop':'name'}).a.text
        updated = x.find('li', {'class':'updated-time'}).text.replace('Updated ', '')
        site = "irishjobs.ie"
        jobID = url.split('-')[-1].split('.')[0]
        lastDate = get_oldest_date(jobID)
        a.append([title, url, location, comp, updated, site, jobID, lastDate])

def mk_df(a):
    #make a dataframe from all the shit got from irishjobs.ie and jobs.ie
    #lastDate sucks and should be name changned as its first date job appeared
    df = pd.DataFrame(a, columns = ['title', 'url', 'location', 'comp', 'updated', 'site', 'JobID', 'lastDate'])
    
    for index, row in df.iterrows():
        #Dates are messy
        if "Today" in df.loc[index, 'updated']:
	    #Change it from "today" to the date
            df.loc[index, 'updated'] = today()

        elif "Day" in df.loc[index, 'updated']:
            #some of them say "update 1 Day ago" which is not good for my code
            df.loc[index, 'updated'] = day_date(df.loc[index, 'updated'])

        elif "/" not in df.loc[index, 'updated']:
	    #Some times the date just has a month like "1 of June"
            df.loc[index, 'updated'] = tidy_date(df.loc[index, 'updated'] + " " + year)

        #Clean up company stuff. 
        df.loc[index, 'comp'] = convert_comp( df.loc[index, 'comp'])
    
    df['updated'] =pd.to_datetime(df.updated, dayfirst=True).dt.date #make the date a date type
    df = df.sort_values(by = 'updated', ascending=False) #sort by date
    df['url'] = '<a href=' + df['url'] + '><div>' + 'url' + '</div></a>' # make the url a anchor
    df.fillna("None", inplace=True)
    
    return df

def main():
  a = []
  irishjobs(a)
  jobsie(a)
  df = mk_df(a)

  #dump to Database stuff, should be in its own function but i am tired. 
  #Also should add a job to clean up old db stuff to keep file small. 
  #cnx = sqlite3.connect(db)
  df_2_dump = df.drop('lastDate', axis=1)
  #df_2_dump = df.drop('lastDate', axis=1)
  df_2_db(df_2_dump)
  #df_2_dump.to_sql(name='jobs', con=cnx, if_exists='append')
  
  #Dump to pickle file so we can mail it later
  #df_2_dump = df_2_dump[df_2_dump["lastDate"].str.contains("Yesterday|Today|None")]
  pickle.dump(df[df["lastDate"].str.contains("Yesterday|Today|None")].to_html(escape = False), open(pk_file, 'wb'))

  print( df[df["lastDate"].str.contains("Yesterday|Today|None")] )
#  print(df.head())

main()

