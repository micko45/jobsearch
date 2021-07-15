import requests
from bs4 import BeautifulSoup as bs
import re, datetime
import pandas as pd
import pickle  
import sqlite3
import mail_df
from db import get_last_date, df_2_db, get_oldest_date
import re

a = []

def setUpVodafoneJobs(url):
  #some job sites are iffy when it comes to headers so spoof chrome
  headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate", 
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8", 
    "Dnt": "1", 
    "Upgrade-Insecure-Requests": "1", 
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36", 
   }

  #url = 'https://careers.vodafone.com/search/search/?q=&q2=&alertId=&title=&location=IE&date='
  r = requests.get(url, headers = headers)
  soup = bs(r.content, 'html.parser')
  data = soup.find_all('tr', {'class':'data-row clickable'})
  return data

def find_job_title(_input):
  output = _input.find('a', {'class':'jobTitle-link'}).get_text()
  return output

def find_job_url(_input):
  firstPartURL = 'https://careers.vodafone.com'
  output = _input.find('span', {'class':'jobTitle hidden-phone'})
  anchor = output.find('a').get('href')
  return firstPartURL + anchor

def find_job_location(_input):
  location = _input.find('span', {'class':'jobLocation'}).get_text()
  return location.strip()

def find_job_date(_input):
  jobDate = _input.find('span', {'class':'jobDate'}).get_text().strip()
  return jobDate

def find_job_id(url):
  return url.split('/')[-2]
  
def vodafoneJobs():
  urls = [
          'https://careers.vodafone.com/search/search/?q=&q2=&alertId=&title=&location=IE&date=', 
	  "https://careers.vodafone.com/search/search/?q=&location=IE&sortColumn=referencedate&sortDirection=desc&startrow=25" 
	  ]

  for url in urls:
    vodafoneJobsInfo(url)

def vodafoneJobsInfo(url):
  #get a load of shit from vodafone.com
  data = setUpVodafoneJobs(url)
  for job in data:
    company = "Vodafone"
    site = "vodafone.com"
    job_title = find_job_title(job)
    url = find_job_url(job)
    location = find_job_location(job)
    updated = find_job_date(job)
    lastDate = updated
    jobID = find_job_id(url)
    #jobID = url.replace('&', '=').split('=')[1]
    #a.append([job_title, url, location, comp, updated, site, jobID, lastDate])
    a.append([job_title, url, location, company, updated, site, jobID, lastDate])
  return a

def main():
 print( vodafoneJobs() )
 print(a)
  

main()
