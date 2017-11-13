#!/usr/bin/env python3
"""awsIotAdapter.py: Adapting internal mqtt data to AWS IOT"""

__author__      = "Nam Soo Park"
__copyright__   = "Copyright 2017, AWS_IOT Challenge"

'''
/*
 * Copyright 2010-2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License").
 * You may not use this file except in compliance with the License.
 * A copy of the License is located at
 *
 *  http://aws.amazon.com/apache2.0
 *
 * or in the "license" file accompanying this file. This file is distributed
 * on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
 * express or implied. See the License for the specific language governing
 * permissions and limitations under the License.
 */
 '''

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import logging
import time
import argparse
import datetime
import json
import random
import os


# Read in command-line parameters
parser = argparse.ArgumentParser()
parser.add_argument("-e", "--endpoint", action="store", required=True, dest="host", help="Your AWS IoT custom endpoint")
parser.add_argument("-r", "--rootCA", action="store", required=True, dest="rootCAPath", help="Root CA file path")
parser.add_argument("-c", "--cert", action="store", dest="certificatePath", help="Certificate file path")
parser.add_argument("-k", "--key", action="store", dest="privateKeyPath", help="Private key file path")
parser.add_argument("-w", "--websocket", action="store_true", dest="useWebsocket", default=False,
                    help="Use MQTT over WebSocket")
parser.add_argument("-id", "--clientId", action="store", dest="clientId", default="basicPubSub",
                    help="Targeted client id")
parser.add_argument("-t", "--topic", action="store", dest="topic", default="sdk/test/Python", help="Targeted topic")

args = parser.parse_args()
host = args.host
rootCAPath = args.rootCAPath
certificatePath = args.certificatePath
privateKeyPath = args.privateKeyPath
useWebsocket = args.useWebsocket
clientId = args.clientId
topic = args.topic

if args.useWebsocket and args.certificatePath and args.privateKeyPath:
    parser.error("X.509 cert authentication and WebSocket are mutual exclusive. Please pick one.")
    exit(2)

if not args.useWebsocket and (not args.certificatePath or not args.privateKeyPath):
    parser.error("Missing credentials for authentication.")
    exit(2)

# Configure logging
logger = logging.getLogger("AWSIoTPythonSDK.core")
logger.setLevel(logging.INFO)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

# Custom MQTT message callback
def customRoverCallback(client, userdata, message):
    logger.info("Rover Contoller is activated: ")
    os.system("sudo python ../motor/RoverControlSensor.py &")
    logger.info(message.payload)
    logger.info("from topic: ")
    logger.info(message.topic)
    logger.info("--------------\n\n")
# Custom MQTT message callback
def customServorCallback(client, userdata, message):
    logger.info("Servo Contoller is activated: ")
    os.system("sudo python ../servo/simulate_servo_u_d_l_r.py &")
    logger.info(message.payload)
    logger.info("from topic: ")
    logger.info(message.topic)
    logger.info("--------------\n\n")
# Custom MQTT message callback
def customXDKCallback(client, userdata, message):
    logger.info("XDK Contoller is activated: ")
    os.system("sudo python ../xdk/read_xdk.py &")
    logger.info(message.payload)
    logger.info("from topic: ")
    logger.info(message.topic)
    logger.info("--------------\n\n")

# Init AWSIoTMQTTClient
myAWSIoTMQTTClient = None
if useWebsocket:
    myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId, useWebsocket=True)
    myAWSIoTMQTTClient.configureEndpoint(host, 443)
    myAWSIoTMQTTClient.configureCredentials(rootCAPath)
else:
    myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId)
    myAWSIoTMQTTClient.configureEndpoint(host, 8883)
    myAWSIoTMQTTClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

# AWSIoTMQTTClient connection configuration
myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

# Connect and subscribe to AWS IoT
myAWSIoTMQTTClient.connect()
#myAWSIoTMQTTClient.subscribe(topic, 1, customCallback)
myAWSIoTMQTTClient.subscribe("/AWS_IoT/Turn/Rover", 1, customRoverCallback)
myAWSIoTMQTTClient.subscribe("/AWS_IoT/Turn/XDK", 1, customXDKCallback)
myAWSIoTMQTTClient.subscribe("/AWS_IoT/Turn/Servo", 1, customServorCallback)

time.sleep(2)

# Publish to the same topic in a loop forever
loopCount = 0

SeonsorTopic = "AWS_IOT/XDK"
RoverSpeedTopic = "AWS_IOT/SPEED"
ServorRotationUpDownTopic = "AWS_IOT/UP_DOWN"
ServorRotationRightLeftTopic = "AWS_IOT/RIGHT_LEFT"
 
def publish_speed_data(json_msg):
  dict = json.loads(json_msg)
  value = dict["speed"]
  rover_speed_data = {}
  rover_speed_data["deviceParameter"] = "speed"
  rover_speed_data["deviceValue"] = value
  rover_speed_data["deviceId"] = "SpeedChecker"
  rover_speed_data['dateTime'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  return (RoverSpeedTopic, rover_speed_data)
   
def publish_servor_rot_up_down_pos_data(json_msg):
  dict = json.loads(json_msg)
  value = dict["up_down"]
  servor_rot_pos_data = {}
  servor_rot_pos_data["deviceParameter"] = "up_down"
  servor_rot_pos_data["deviceValue"] = value
  servor_rot_pos_data["deviceId"] = "SevorMotor"
  servor_rot_pos_data['dateTime'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  return (ServorRotationUpDownTopic, servor_rot_pos_data)

def publish_servor_rot_right_left_pos_data(json_msg):
  dict = json.loads(json_msg)
  value = dict["right_left"]
  servor_rot_pos_data = {}
  servor_rot_pos_data["deviceParameter"] = "right_left"
  servor_rot_pos_data["deviceValue"] = value
  servor_rot_pos_data["deviceId"] = "SevorMotor"
  servor_rot_pos_data['dateTime'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  return (ServorRotationRightLeftTopic, servor_rot_pos_data)


def publish_sensor_data(json_msg):  
  dict = json.loads(json_msg)

  sensors_data ={'dateTime':None, 'Temperature':0.0, 'Humidity':0.0, 'Light' : 0.0,
                'Gyroscope': {"x":0.0, "y":0.0, "z":0.0},
                'Accelerometer': {"x":0.0, "y":0.0, "z":0.0},
                'Magnetometer': {"x":0.0, "y":0.0, "z":0.0}
                }
  sensors_data['dateTime'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  sensors_data['deviceParameter'] = "sensors"
  sensors_data['deviceId'] = "XDK"
  sensors_data['deviceValue'] = 0xff
  sensors_data['Temperature'] = dict["Temp"]
  sensors_data["Humidity"] = dict["Humidity"]
  sensors_data["Light"] =  dict["Light"]

  sensors_data["Accelerometer"]["x"] = dict["Accel"]["x"]
  sensors_data["Accelerometer"]["y"] = dict["Accel"]["y"]
  sensors_data["Accelerometer"]["z"] = dict["Accel"]["z"]

  sensors_data["Gyroscope"]["x"] = dict["Gyro"]["x"]
  sensors_data["Gyroscope"]["y"] = dict["Gyro"]["y"]
  sensors_data["Gyroscope"]["z"] = dict["Gyro"]["z"]

  sensors_data["Magnetometer"]["x"] = dict["Mag"]["x"]
  sensors_data["Magnetometer"]["y"] = dict["Mag"]["y"]
  sensors_data["Magnetometer"]["z"] = dict["Mag"]["z"]
  return (SeonsorTopic, sensors_data)

import paho.mqtt.client as mqtt
import json

# This is the Subscriber
MQTT_TOPIC = "#"
MY_HOST_IP = "192.168.1.155"

internal_mqtt_client = None

def internal_mqtt_on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(MQTT_TOPIC)


def internal_mqtt_on_message(client, userdata, msg):
    print("user data ={} topics = {} msg={}".format(userdata, msg.topic, msg.payload.decode()))
    try:
      payload = json.loads(msg.payload)  # you can use json.loads to convert string to json
      print(payload)  # then you can check the value
    except KeyError as e:
        print("Error in Json parsing Error ={}".format(e))
        return 
    if msg.topic == SeonsorTopic:
      topic, message = publish_sensor_data(msg.payload)
      message = json.dumps(message)
      myAWSIoTMQTTClient.publish(topic, message, 1)
    elif msg.topic == RoverSpeedTopic:
      topic, message = publish_speed_data(msg.payload)
      message = json.dumps(message)
      myAWSIoTMQTTClient.publish(topic, message, 1)
    elif msg.topic == ServorRotationUpDownTopic:  
      topic, message = publish_servor_rot_up_down_pos_data(msg.payload)
      message = json.dumps(message)
      myAWSIoTMQTTClient.publish(topic, message, 1)
    elif msg.topic == ServorRotationRightLeftTopic: 
      topic, message = publish_servor_rot_right_left_pos_data(msg.payload)
      message = json.dumps(message)
      myAWSIoTMQTTClient.publish(topic, message, 1)

def set_up_internal_mqtt():
  global internal_mqtt_client
  print("Starting setting up internal mqtt")
  internal_mqtt_client = mqtt.Client()
  internal_mqtt_client.connect(MY_HOST_IP, 1883, 60)

  internal_mqtt_client.on_connect = internal_mqtt_on_connect
  internal_mqtt_client.on_message = internal_mqtt_on_message
  return internal_mqtt_client

def main():
  client = set_up_internal_mqtt()
  client.loop_start()

  while True:
    pass
      #myAWSIoTMQTTClient.publish(topic, "New Message " + str(loopCount), 1)


if __name__ == '__main__':
  main()