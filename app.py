import base64
import datetime
import json
import os
import time
from numpy import median, mean
from flask import Flask, render_template, request
from flask_mqtt import Mqtt
import sys
import sqlite3

db_file="history.db"

app = Flask(__name__)
app.config['MQTT_BROKER_URL'] = "localhost"

# Must set this otherwise the the photos will be stored into broswer's cache, and the result is the photos for rooms
# not get updated.
#app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_REFRESH_TIME'] = 1.0  # refresh time in seconds
app.config['MQTT_KEEPALIVE'] = 60
app.config['MQTT_USERNAME'] = 'local'
app.config['MQTT_PASSWORD'] = 'shuihouzishuihouzi'
app.config['MQTT_TLS_ENABLED'] = False
app.config['MQTT_CLEAN_SESSION'] = True
mqtt = Mqtt(app)

mqtt.subscribe('data')
mqtt.subscribe('photo')

current_data = []  # a global variable to store current number of people in rooms.
current_photo = ""
# these two flags are for checking if we have receive message from publisher/broker. Only when we received message,
# we send the newly received message to the front end.
# this is to avoid such a situation: when there is a delay between the broker and the publisher or server, the backend
# maybe will send old data to front end.
data_received = 0
photo_received = 0


@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    print("client for server connected", flush=True, file=sys.stderr)


@mqtt.on_topic("photo")
def test1(client, userdata, message):
    global current_photo
    current_photo = message.payload
    global photo_received
    photo_received = 1


@mqtt.on_topic("data")
def test2(client, userdata, message):
    msg_r = str(message.payload.decode("utf-8"))
    global current_data
    # write listened data into database
    current_data = json.loads(msg_r)
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    for r in current_data:
        roomNumber = r["roomNumber"]
        number = r["number"]
        r_date = datetime.date.today()
        the_day = r_date.weekday() + 1
        r_time = time.strftime('%H:%M:%S', time.localtime())
        r_date = time.strftime('%Y-%m-%d', time.localtime())
        sql = 'insert into history_data(room_number,number,the_time,the_date,the_day) values(?,?,?,?,?)'
        data = (roomNumber, number, r_time, r_date, the_day)
        cur.execute(sql, data)
        conn.commit()
    conn.close()
    # when data is received, change the flag to 1.
    global data_received
    data_received = 1


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/history/<roomNumberParam>")
def photo(roomNumberParam):
    return render_template("history.html")


# This is just for testing showing the right picture

'''
@app.route("/photo/<roomNumberParam>")
def testPhoto(roomNumberParam):

    global photo_received
    photo_received = 0
    mqtt.publish("photo_check", str(roomNumberParam))
    # set the flag to 0 first, then publish the check msg and wait for the data msg sending back.
    # After the data msg is received, send it to the front end.
    while (1):
        if (photo_received == 1): break

    # write the picture so that front end can use directly
    name=str(roomNumberParam)+".png"
    path=os.path.join("static", "img", name)
    f = open(path, "wb")
    f.write(current_photo)
    print("Image Received")
    f.close()
    path_html="/static/img/"+str(roomNumberParam)+".png"

    # here current_photo is a bytes-like object, just use you read image with "rb"
    return render_template("imgTest.html", path=path_html)
'''
@app.route("/photo/<roomNumberParam>")
def testPhoto(roomNumberParam):

    # here current_photo is a bytes-like object, just use you read image with "rb"
    return render_template("imgTest.html")

@app.route("/getData", methods=['GET'])
def getData():

    #  just read newest data from database
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    dataList=[]
    for i in range(5):
        #print(i)
        roomNumber = i
        newestData = cur.execute("select number from history_data where room_number=? order by id desc limit 1",(roomNumber,))
        for data in newestData:
            dataList.append({'roomNumber':i, 'number': data[0]})
    res= json.dumps(dataList)
    conn.close()
    '''
    global data_received
    data_received = 0
    mqtt.publish("check", "check")
    while (1):
        if (data_received == 1): break
        # print(data_received)
    res = json.dumps(current_data)
    '''
    return res

@app.route("/getPhoto", methods=['GET'])
def getPhoton():
    roomNumber=request.args.get("roomNumber")
    global photo_received
    photo_received = 0
    mqtt.publish("photo_check", str(roomNumber))
    # set the flag to 0 first, then publish the check msg and wait for the data msg sending back.
    # After the data msg is received, send it to the front end.
    while (1):
        if (photo_received == 1): break

    # write the picture so that front end can use directly
    name=str(roomNumber)+".png"
    path=os.path.join("static", "img", name)
    f = open(path, "wb")
    f.write(current_photo)
    print("Image Received")
    f.close()
    path_html="/static/img/"+str(roomNumber)+".png"

    # here current_photo is a bytes-like object, just use you read image with "rb"
    return path_html

@app.route("/getHistoryData",methods=['GET'])
def history():
    roomNumber=request.args.get("roomNumber")
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    time_series = generate_time()
    dataList = []
    for i in range(1, 6):  # for day
        dayData = []
        # 27 time points, 26 time intervals
        for k in range(26):
            temp = []
            start = time_series[k]
            end = time_series[k + 1]
            newestData = cur.execute("select * from history_data where room_number=? and the_day= ? "
                                     "and STRFTIME('%H:%M', the_time) >= ?"
                                     "and STRFTIME('%H:%M', the_time) < ?"
                                     "order by id desc limit 20",
                                     (roomNumber, i, start, end))
            for data in newestData:
                temp.append(data[2])
            if len(temp) != 0:
                med = median(temp)
            else:
                med = 0
            dayData.append(med)
        # print(len(dayData))
        # print(dayData)
        dataList.append({"name": the_day(i), "historyData": dayData})
    conn.close()
    return json.dumps(dataList)

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

def the_day(d):
    if d==1: return "Monday"
    elif d==2: return "Tuesdady"
    elif d==3: return "Wednesday"
    elif d==4: return "Thursday"
    elif d==5: return "Friday"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=False)
