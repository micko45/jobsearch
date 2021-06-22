import sqlite3
from datetime import datetime, timedelta, date

db = './files/db.sql'
con = sqlite3.connect(db)
cur = con.cursor()

#select updated from jobs where JobID = 8620334 order by date(updated) ASC limit 1;

def todays_date():
  return date.today()

def yesterdays_date():
  today = todays_date()
  return today - timedelta(days = 1)

def get_last_date(jobid, today = str(todays_date()), yesterday = yesterdays_date()):
 
  sql = "SELECT updated FROM jobs WHERE JobID = {} ORDER BY DATE(updated) ASC LIMIT 1".format(int(jobid))
  cur.execute(sql)
  sql_data = cur.fetchall()
  for d in sql_data:
     data =  "".join(d)

     if data == today:
       return "Today"

     elif data == yesterday:
       return "Yesterday"

     else: return data

def get_oldest_date(jobid):
  today = str(todays_date())
  yesterday = str(yesterdays_date())
 
  sql = "SELECT updated FROM _jobs WHERE jobid = {} ORDER BY DATE(updated) ASC LIMIT 1".format(int(jobid))
  cur.execute(sql)
  data = cur.fetchall()
  for d in data:
     data =  "".join(d)

     if data == today:
       return "Today"

     elif data == yesterday:
       return "Yesterday"

     else: return data

def df_2_db(df):

  df.to_sql(name='_jobs_tmp', con=con, if_exists='append')

  sql = 'insert or ignore into _jobs("index", title, url, location, comp, updated, site, jobid) select "index", title, url, location, comp, max(updated), site, JobID as latest from _jobs_tmp  group by JobID;'
  print(sql)
  cur.execute(sql)
  con.commit()
 

if __name__ == "__main__":
#  df_2_db()
#  print(get_last_date(8620558))
  print(yesterdays_date())
  for i in [ 8620558, 1954113, 1956471, 8627436, 1954237, 8625984 ]:
    d2 = get_oldest_date(i)
    print(d2)
   # today = str(todays_date())
   # yesterday = str(yesterdays_date())
    #today = datetime.now().strftime("%Y-%m-%d")
   # if today == d2:
   #   #print(today, " and ", d2 , "match", i )
   #   print("today is ", d2)
   # elif d2 == yesterday:
   #   print("yesterday was ", d2)
   # else: print(today, d2, i)
#  print("yesterday " , today - timedelta(days = 1))
