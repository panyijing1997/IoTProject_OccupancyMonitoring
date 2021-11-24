import json
import os
import random
import paho.mqtt.client as mqtt
import numpy as np
import argparse
import sys
import time
import cv2
from object_detector import ObjectDetector
from object_detector import ObjectDetectorOptions

camera_id=0

width=1280
height=960
num_threads=4
enable_edgetpu=False
model='model4.tflite'
cap = cv2.VideoCapture("4.mp4")
cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

cap_real = cv2.VideoCapture(camera_id)
cap_real.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cap_real.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

def on_message_local(client, userdata, message):
    if message.topic == "data":
        r_msg=str(message.payload.decode("utf-8"))
        print("local receicved",r_msg)
    elif message.topic == "photo_check":

        name= str(message.payload.decode("utf-8")) +".png"

        if str(message.payload.decode("utf-8")) == "0":
            print("yay")
            # take a photo from the real camera
            success, image = cap_real.read()
            if not success:
                sys.exit(
                    'ERROR: Unable to read from webcam. Please verify your webcam settings.'
                )
            image = cv2.flip(image, 1)
            cv2.imwrite(name, image)
        elif str(message.payload.decode("utf-8")) == "1":
            print("yay")
            # take a photo from the real camera
            success, image = cap.read()
            if not success:
                sys.exit(
                    'ERROR: Unable to read from webcam. Please verify your webcam settings.'
                )
            image = cv2.flip(image, 1)
            cv2.imwrite(name, image)
        else:
        # generate random pic for testing
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
    client.subscribe("photo_check")


c = mqtt.Client()
c.on_connect = on_connect_local
c.on_message= on_message_local
c.username_pw_set("local","shuihouzishuihouzi")
c.connect("localhost", 1883, 200)
c.loop_start()

c_cloud = mqtt.Client()
c_cloud.on_connect = on_connect_local
c_cloud.on_message= on_message_local
c_cloud.username_pw_set("local","shuihouzishuihouzi")
c_cloud.connect("yijingmqtt.westeurope.azurecontainer.io", 1883, 200)
c_cloud.loop_start()

''' #test another video at the same time
cap2=cv2.VideoCapture("1.mp4")
cap2.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cap2.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
'''
options = ObjectDetectorOptions(
    num_threads=num_threads,
    score_threshold=0.3,
    max_results=50,
    label_allow_list=["person"],
    enable_edgetpu=enable_edgetpu)
detector = ObjectDetector(model_path=model, options=options)

options2 = ObjectDetectorOptions(
    num_threads=num_threads,
    score_threshold=0.1,
    max_results=50,
    label_allow_list=["person"],
    enable_edgetpu=enable_edgetpu)
detector2 = ObjectDetector(model_path=model, options=options2)

nList=[]
nList2=[]# for storing 10 data and find the maxima
while True:
    success, image = cap_real.read()
    if not success:
        sys.exit(
            'ERROR: Unable to read from webcam. Please verify your webcam settings.'
        )
    image = cv2.flip(image, 1)
    # Run object detection estimation using the model.
    detections1 = detector.detect(image)

    #test another video at the same time
    success2, image2 = cap.read()
    if not success2:
        sys.exit(
            'ERROR: Unable to read from webcam. Please verify your webcam settings.'
        )
    image2 = cv2.flip(image2, 1)
    # Run object detection estimation using the model.
    detections2 = detector2.detect(image2)

    #for every 10 times of detection, we only publish the max number.
    nList.append(len(detections1))
    nList2.append(len(detections2))
    if len(nList)==3:
        #print(nList)
        a=np.max(nList)
        b=np.max(nList2)
        nList.clear()
        nList2.clear()
        print("max",a)
        print("max", b)
        d = []  # dictionary, format {roomNumber}
        d.append({'roomNumber': 0, 'number': int(a)})
        d.append({'roomNumber': 1, 'number': int(b)})
        # room0 has real number, others are simulated
        for i in range(2,5):
            d.append({'roomNumber': i, 'number': random.randint(0, 10)})
        print(d)
        c.publish("data",json.dumps(d))
        c_cloud.publish("data", json.dumps(d))
    time.sleep(1)
