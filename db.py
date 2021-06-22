import sqlite3
from datetime import datetime

db = './files/db.sql'
con = sqlite3.connect(db)
cur = con.cursor()

#select updated from jobs where JobID = 8620334 order by date(updated) ASC limit 1;

def get_last_date(jobid):
 
  sql = "SELECT updated FROM jobs WHERE JobID = {} ORDER BY DATE(updated) ASC LIMIT 1".format(int(jobid))
  cur.execute(sql)
  data = cur.fetchall()
  for d in data:
     return  "".join(d)

def get_oldest_date(jobid):
 
  sql = "SELECT updated FROM _jobs WHERE jobid = {} ORDER BY DATE(updated) ASC LIMIT 1".format(int(jobid))
  cur.execute(sql)
  data = cur.fetchall()
  for d in data:
     return  "".join(d)

def df_2_db(df):

  df.to_sql(name='_jobs_tmp', con=con, if_exists='append')

  sql = 'insert or ignore into _jobs("index", title, url, location, comp, updated, site, jobid) select "index", title, url, location, comp, max(updated), site, JobID as latest from _jobs_tmp  group by JobID;'
  print(sql)
  cur.execute(sql)
  con.commit()
 

if __name__ == "__main__":
  df_2_db()
#  print(get_last_date(8620558))
#  for i in [ 8620558, 1954113, 1956471 ]:
#    d2 = get_oldest_date(i)
#    today = datetime.now().strftime("%Y-%m-%d")
#    if today == d2:
#      print(today, " and ", d2 , "match", i )
#    else: print(today, d2, i)
