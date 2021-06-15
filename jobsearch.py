import requests
from bs4 import BeautifulSoup as bs
import re, datetime
import pandas as pd
import pickle  

pk_file = "./pikle.pk"

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
data = soup.find_all('div', {'class':"job-details-header serp-item default"})

#Set up irishjobs.ie
url2 = "https://www.irishjobs.ie/ShowResults.aspx?Keywords=linux&autosuggestEndpoint=%2Fautosuggest&Location=0&Category=&Recruiter=Company&Recruiter=Agency&btnSubmit=Search"
r2 = requests.get(url2, headers = headers)
soup2 = bs(r2.content, 'html.parser')
data2 = soup2.find_all('div', {'class':'module job-result'})

year = datetime.datetime.now().strftime("%Y")

def make_clickable(val):
    # target _blank to open new window
    return '<a target="_blank" href="{}">{}</a>'.format(val, val)

def day_date(x = "1 Day ago"):
    s = x.lower().replace('day ', 'days ')
    parsed_s = [s.split()[:2]]
    time_dict = dict((fmt,float(amount)) for amount,fmt in parsed_s)
    dt = datetime.timedelta(**time_dict)
    past_time = datetime.datetime.now() - dt
    parsed_date = past_time.strftime("%d/%m/%Y")
    return parsed_date
#day_date()

def tidy_date(_input = "2 Jun 2021"):
    d = datetime.datetime.strptime(_input, '%d %b %Y')
    return d.strftime("%d/%m/%Y")
#tidy_date()

def today():
    return datetime.datetime.now().strftime("%d/%m/%Y")
#today()

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

def test2():
    for x in data2:
        #print(x.find('li', {'class':'updated-time'}).text.replace('Updated ', ''))
        print(x.find('h3', {'itemprop':'name'}).a.text)
#test2()

def test1():
    for i in data:
        #print("Updated", i.find('dd', {'class':'fa-clock-o'}).text)
        #print(i.find('dd', re.compile("fa-clock")))
        txt = i.find('a').get('href').replace('/', '')
        print(convert_comp(txt))

#test1()

def jobsie(a):
    for i in data:
        job_title = i.find('h2').text
        comp = i.find('a').get('href').replace('/', '')
        url = i.find_all('a')[1].get('href')
        location = i.find('dd', {'class':'fa-map-marker'}).text
        updated = i.find('dd', {'class':'fa-clock-o'}).text
        site = "jobs.ie"
        jobID = url.replace('&', '=').split('=')[1]
        a.append([job_title, url, location, comp, updated, site, jobID])

def irishjobs(a):
    for x in data2:
        title = x.find_all('a')[1].text
        url = "https://www.irishjobs.ie"  + x.find_all('a')[1].get('href')
        location = x.find('li', {'class':'location'}).find('a').text
        comp = x.find('h3', {'itemprop':'name'}).a.text
        updated = x.find('li', {'class':'updated-time'}).text.replace('Updated ', '')
        site = "irishjobs.ie"
        a.append([title, url, location, comp, updated, site])

def mk_df(a):
    df = pd.DataFrame(a, columns = ['title', 'url', 'location', 'comp', 'updated', 'site', 'JobID'])
    
    for index, row in df.iterrows():
        if "Today" in df.loc[index, 'updated']:
            df.loc[index, 'updated'] = today()

        elif "Day" in df.loc[index, 'updated']:
                df.loc[index, 'updated'] = day_date(df.loc[index, 'updated'])

        elif "/" not in df.loc[index, 'updated']:
            df.loc[index, 'updated'] = tidy_date(df.loc[index, 'updated'] + " " + year)

        #Clean up company stuff. 
        df.loc[index, 'comp'] = convert_comp( df.loc[index, 'comp'])
    
    df['updated'] =pd.to_datetime(df.updated, dayfirst=True).dt.date  
    df = df.sort_values(by = 'updated', ascending=False)
    df['url'] = '<a href=' + df['url'] + '><div>' + 'url' + '</div></a>'
    #df = df.style.format({'url': make_clickable})
    
    return df

a = []
irishjobs(a)
jobsie(a)
df = mk_df(a)
pickle.dump(df.to_html(escape = False), open(pk_file, 'wb'))

print(df.head())
