import datetime
from math import isnan
import random
import sqlite3
from sqlite3 import Error
db_file='history.db'
import time
import numpy as np

def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()

def random_date(start, end):

    b=end-start

    days=b.days

    r_d =random.randrange(days)
    random_date = start + datetime.timedelta(days=r_d)
    return random_date

def random_time():
    h=random.randint(0, 23)
    m = random.randint(1, 12)
    s = random.randint(0, 59)
    yup=datetime.time(h,m,s)

    return yup

# insert a random record into database
def insert_random(db_file):

    s = datetime.date(2021, 10, 1)
    e = datetime.date(2021, 11, 10)
    #random date
    r_date=random_date(s, e)
    #day
    the_day=r_date.weekday()+1
    #random time
    r_time=random_time().strftime("%H:%M:%S")

    #randomnumber
    number=random.randint(0, 20)

    #random room number
    roomNumber = random.randint(0, 5)

    conn = sqlite3.connect(db_file)
    cur=conn.cursor()
    sql='insert into history_data(room_number,number,the_time,the_date,the_day) values(?,?,?,?,?)'
    data=(roomNumber,number,r_time,r_date,the_day)
    cur.execute(sql,data)
    conn.commit()
    conn.close()

# insert a record with random number and random roomNumber but with current time
def insert_now():
    r_date=datetime.date.today()
    #day
    the_day=r_date.weekday()+1
    #r_date=r_date.strftime("%Y-%m-%d")

    r_time = time.strftime('%H:%M:%S', time.localtime())
    r_date = time.strftime('%Y-%m-%d', time.localtime())
    #randomnumber
    number=random.randint(0, 20)

    #random room number
    roomNumber = 0

    conn = sqlite3.connect(db_file)
    cur=conn.cursor()
    sql='insert into history_data(room_number,number,the_time,the_date,the_day) values(?,?,?,?,?)'
    data=(roomNumber,number,r_time,r_date,the_day)
    cur.execute(sql,data)
    conn.commit()
    conn.close()

#check the newest record
def check_new():
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    dataList=[]
    for i in range(5):
        #print(i)
        roomNumber = i
        newestData = cur.execute("select * from history_data where room_number=? order by id desc limit 1",(roomNumber,))
        for data in newestData:
            dataList.append({"roomNumber":i, "number": data[2],"time": data[4]})
    conn.close()
    print( dataList)

def check_history():
    roomNumber=2
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()

    for i in range(1,8):
        dataList = []
        newestData = cur.execute("select * from history_data where room_number=? and the_day= ? order by id desc limit 20",
                                 (roomNumber,i))
        for data in newestData:
                dataList.append({"roomNumber": roomNumber, "number": data[2], "day": data[5], "time":data[4]})
        print(dataList)
    conn.close()

def checktime(roomNumber):
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    time_series=generate_time()
    dataList=[]
    for i in range(1,6): # for day
        dayData=[]
        #27 time points, 26 time intervals
        for k in range(26):
            temp=[]
            start=time_series[k]
            end=time_series[k+1]
            newestData = cur.execute("select * from history_data where room_number=? and the_day= ? "
                                     "and STRFTIME('%H:%M', the_time) >= ?"
                                     "and STRFTIME('%H:%M', the_time) < ?"
                                     "order by id desc limit 20",
                                     (roomNumber, i,start,end))
            for data in newestData:
                temp.append(data[2])
            if len(temp)!=0:
                med=np.median(temp)
            else : med=0
            dayData.append(med)
        #print(len(dayData))
        #print(dayData)
        dataList.append({"name":the_day(i),"historyData":dayData})
    conn.close()
    return  dataList

# To generate time series in form of "%H:%M"
def generate_time():
    time_series=[]
    time_series.append(str(datetime.time(5,30).strftime('%H:%M')))
    for i in range(13):
        h=6+i
        a_time=str(datetime.time(h,00).strftime('%H:%M'))
        b_time = str(datetime.time(h, 30).strftime('%H:%M'))
        time_series.append(a_time)
        time_series.append(b_time)
    return time_series

# insert some data for every time interval for a room. This is for getting enough
# data for each time interval to test showing the historical data
def insert_time(roomNumber):
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    for i in range(13):
        h=5+i
        a_time=str(datetime.time(h,15,4).strftime('%H:%M:%S'))
        b_time = str(datetime.time(h, 43,23).strftime('%H:%M:%S'))

        s = datetime.date(2021, 10, 1)
        e = datetime.date(2021, 11, 10)
        r_date = random_date(s, e)
        # day
        the_day = r_date.weekday() + 1
        # randomnumber
        number = random.randint(0, 20)

        sql = 'insert into history_data(room_number,number,the_time,the_date,the_day) values(?,?,?,?,?)'
        data = (roomNumber, number, a_time, r_date, the_day)
        cur.execute(sql, data)
        conn.commit()

        sql = 'insert into history_data(room_number,number,the_time,the_date,the_day) values(?,?,?,?,?)'
        data = (roomNumber, number, b_time, r_date, the_day)
        cur.execute(sql, data)
        conn.commit()

    conn.close()

def the_day(d):
    if d==1: return "Monday"
    elif d==2: return "Tuesdady"
    elif d==3: return "Wednesday"
    elif d==4: return "Thursday"
    elif d==5: return "Friday"

check_new()