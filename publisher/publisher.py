import json
import os
import time
import random
import paho.mqtt.client as mqtt
import cv2
import numpy as np
#This script is for testing mosquitto image, and generate random number and random pic for each room.

def on_message_local(client, userdata, message):
    if message.topic == "data":
        r_msg=str(message.payload.decode("utf-8"))
        print("local receicved",r_msg)
    elif message.topic == "check":
        d = []
        for i in range(5):
            d.append({'roomNumber': i, 'number': random.randint(0, 20)})
        print(d)
        client.publish("data", json.dumps(d))
    elif message.topic == "photo_check":

        name= str(message.payload.decode("utf-8")) +".png"
        '''
        # TODO: accordinig to the room number pi camera take a photo here
        f = open(name, "rb")
        filecontent = f.read()
        byteArr = bytearray(filecontent)
        f.close()
        '''
        #generate random pic for testing
        rgb = np.random.randint(255, size=(900, 800, 3), dtype=np.uint8)
        cv2.imwrite(name, rgb)

        f = open(name, "rb")
        filecontent = f.read()
        byteArr = bytearray(filecontent)
        f.close()
        client.publish("photo", byteArr)

def on_connect_local(client, userdata, flags, rc):
    print(f"local connected with result code {rc}")
    client.subscribe("data")
    client.subscribe("check")
    client.subscribe("photo_check")



c = mqtt.Client()
c.on_connect = on_connect_local
c.on_message=on_message_local
c.username_pw_set("local","shuihouzishuihouzi")
c.connect("yijingmqtt.westeurope.azurecontainer.io", 1883, 200)
c.loop_start()


while True:
    print("==================================")
    d = []  # dictionary, format {roomNumber}
    for i in range(5):
        d.append({'roomNumber':i, 'number':random.randint(0,20)})
    print(d)
    c.publish("data",json.dumps(d))

    #Test Mqtt send image.


    #c.publish("test1", str(time.time()))

    time.sleep(2)