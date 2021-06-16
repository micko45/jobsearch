import sqlite3
db = './files/db.sql'
con = sqlite3.connect(db)
cur = con.cursor()
#select updated from jobs where JobID = 8620334 order by date(updated) ASC limit 1;


def get_last_date(jobid):
 
  sql = "SELECT updated FROM jobs WHERE JobID = {} ORDER BY DATE(updated) ASC LIMIT 1".format(int(jobid))
  cur.execute(sql)
  data = cur.fetchall()
  for d in data:
     return "".join(d)


#get_last_date()
