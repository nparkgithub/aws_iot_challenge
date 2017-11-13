#!/usr/bin/env python3
"""mqtt_publisher.py: publish xdk sensor data using mqtt"""

__author__      = "Nam Soo Park"
__copyright__   = "Copyright 2017, AWS_IOT Challenge"

import os
import random
import time
import re
import paho.mqtt.client as mqtt
import json
"""
while True:
        temp = random.uniform(1,100)
        hum = int(random.uniform(1,100))
	os.system("sudo mosquitto_pub -h 192.168.1.155 -p 1883 -t Home/Outdoor/Temperature -m " + str(temp)) 
	os.system("sudo mosquitto_pub -h 192.168.1.155 -p 1883 -t Home/Outdoor/Humidity -m " + str(hum)) 
	time.sleep(2)
"""
test_data = [
	"BOSCH_XDK#Humidity#25",
	"BOSCH_XDK#Temp#34520",
	"BOSCH_XDK#Pressure#100475",
	"BOSCH_XDK#Accel#934, -178, -317",
	"BOSCH_XDK#Gyro#1586, -3173, 2197",
	"BOSCH_XDK#Light#5760",
	"BOSCH_XDK#Mag#-25, 27, -39" ]

sensor_pattern_dic = {
	"Humidity" : "#(\d+)",
	"Temp": "#(\d+)",
	"Pressure": "#(\d+)",
	"Accel": "#([-]?\d+),\s([-]?\d+),\s+([-]?\d+)",
	"Gyro": "#([-]?\d+),\s([-]?\d+),\s+([-]?\d+)",
	"Light": "#(\d+)",
	"Mag": "#([-]?\d+),\s([-]?\d+),\s+([-]?\d+)"
}
sensor_data_dic = {
	"Humidity" : 0,
	"Temp": 0,
	"Pressure": 0,
	"Accel": {"x":0, "y":0, "z":0},
	"Gyro":  {"x":0, "y":0, "z":0},
	"Light": 0,
	"Mag":{"x":0, "y":0, "z":0}
}
# This is the Publisher
def compose_sensor_data_send_to_mqtt_using_python(topic, sensor_data_dic):
	broker_addr="192.168.1.155"
	port=1883
	MQTT_MSG=json.dumps(sensor_data_dic)
	client = mqtt.Client()
	client.connect(broker_addr,port,60)
	client.publish(topic, MQTT_MSG)
	client.disconnect()

def compose_sensor_data_send_to_mqtt_using_shell(sensor_data_dic):
	command_cmd = "sudo mosquitto_pub -h 192.168.1.155 -p 1883 -t "
	topic = "Home/Outdoor/Humidity " + "-m " + str(sensor_data_dic["Humidity"]) 
	cmd = command_cmd + topic
	os.system(cmd)
	topic = "Home/Outdoor/Temperature " + "-m " + str(sensor_data_dic["Temp"]) 
	cmd = command_cmd + topic
	os.system(cmd)
	topic = "Home/Outdoor/Pressure " + "-m " + str(sensor_data_dic["Pressure"]) 
	cmd = command_cmd + topic
	os.system(cmd)
	topic = "Home/Outdoor/Light " + "-m " + str(sensor_data_dic["Light"]) 
	cmd = command_cmd + topic
	os.system(cmd)
	topic = "Home/Outdoor/Accel_x " + "-m " + str(sensor_data_dic["Accel"]["x"]) 
	cmd = command_cmd + topic
	os.system(cmd)
	topic = "Home/Outdoor/Accel_y " + "-m " + str(sensor_data_dic["Accel"]["y"]) 
	cmd = command_cmd + topic
	os.system(cmd)
	topic = "Home/Outdoor/Accel_z " + "-m " + str(sensor_data_dic["Accel"]["z"]) 
	cmd = command_cmd + topic
	os.system(cmd)
	topic = "Home/Outdoor/Gyro_x " + "-m " + str(sensor_data_dic["Gyro"]["x"]) 
	cmd = command_cmd + topic
	os.system(cmd)
	topic = "Home/Outdoor/Gyro_y " + "-m " + str(sensor_data_dic["Gyro"]["y"]) 
	cmd = command_cmd + topic
	os.system(cmd)
	topic = "Home/Outdoor/Gyro_z " + "-m " + str(sensor_data_dic["Gyro"]["z"]) 
	cmd = command_cmd + topic
	os.system(cmd)
	topic = "Home/Outdoor/Magnetic_x " + "-m "+ str(sensor_data_dic["Mag"]["x"]) 
	cmd = command_cmd + topic
	os.system(cmd)
	topic = "Home/Outdoor/Magnetic_y " + "-m " + str(sensor_data_dic["Mag"]["y"]) 
	cmd = command_cmd + topic
	os.system(cmd)
	topic = "Home/Outdoor/Magnetic_z " + "-m " + str(sensor_data_dic["Mag"]["z"]) 
	cmd = command_cmd + topic
	os.system(cmd)


def find_item(key):
	try:
		return sensor_pattern_dic[key]
	except Exception as e:
		print("Can not find key {}".format(key))
		return None

def parse_data(input_data):
	#for data in input_data:
	data = input_data
	if data:
		try:
			result = re.search("#(\w+)#",data)
			key = result.group(1)
			print key
			pattern = find_item(key)
			print pattern
			result = re.search(pattern,data)
			dict_flag = isinstance(sensor_data_dic[key],dict)
			if dict_flag == True:
				sensor_data_dic[key]["x"] = result.group(1)
				sensor_data_dic[key]["y"] = result.group(2)
				sensor_data_dic[key]["z"] = result.group(3)
			else:
				sensor_data_dic[key] = result.group(1)
			print sensor_data_dic
		except Exception as e:
			print("Error in finding {} as {}".format(data, e))
def send_sensor_data(read_data):
	parse_data(read_data)
	compose_sensor_data_send_to_mqtt_using_python("AWS_IOT/XDK", sensor_data_dic)
