#!/usr/bin/env python3
"""Sensors.py: Enable Sonar sensors to measure distance"""

__author__      = "Nam Soo Park"
__copyright__   = "Copyright 2017, AWS_IOT Challenge"

from sys import platform
import time
import math 
import threading
import RoverMotorSensor as RMS
import paho.mqtt.client as mqtt
import json

compile_os = "linux"

if platform == "linux" or platform == "linux2":
    print 'linux'
elif platform == "darwin":
    print 'darwin'
    compile_os = "darwin"
elif platform == "win32":
    print 'win'
    compile_os = "win"

if compile_os == "win" or compile_os == "darwin":
    from RaspberryPi import GPIO as GPIO
else:
    import RPi.GPIO as GPIO

# This is the Publisher
class Mqtt_Publisher(object):
    def __init__(self, broker_addr="192.168.1.155", port=1883):
        self.broker_addr = broker_addr
        self.port = port
        self.client = None

    def publish(self, topic, msg):        
        MQTT_MSG=json.dumps(msg)
        client = mqtt.Client()
        client.connect(self.broker_addr,self.port,60)
        client.publish(topic, MQTT_MSG)
        client.disconnect()

class DetectObject(object):
    def __init__(self): 
        self.TRIG = 21
        self.ECHO = 20
        self.previous_distance = 0
        self.mqtt = Mqtt_Publisher()

    def wait_BCM_initalized(self):
        if False == RMS.bcm_initialized_from_other:
            print("BCM has not initialized yet")
            time.sleep(1)
            return
            #GPIO.setwarnings(False)
            #GPIO.setmode(GPIO.BCM)
            #GPIO.cleanup()
        print "Distance Measurement In Progress"
        GPIO.setup(self.TRIG,GPIO.OUT)
        GPIO.setup(self.ECHO,GPIO.IN)
        

    def measure_location_speed(self):
        self.wait_BCM_initalized()
        try:
            GPIO.output(self.TRIG, False)
            #print "Waiting For Sensor To Settle"
            time.sleep(0.5)
            GPIO.output(self.TRIG, True)
            time.sleep(0.00001)
            GPIO.output(self.TRIG, False)
            
            while GPIO.input(self.ECHO)==0:
                pulse_start = time.time()
            while GPIO.input(self.ECHO)==1:
                pulse_end = time.time()

            pulse_duration = pulse_end - pulse_start
            # v = d /t if v is light speed and t is 2t, then 
            distance = pulse_duration * 17150
            distance = round(distance, 2)
            print "Distance:", distance, "cm"
            speed =  math.fabs(self.previous_distance - distance) / (pulse_duration * 1000)
            self.previous_distance = distance 
            print("Speed = {} cm/second(s)".format(speed))
            msg = {}
            msg["speed"] = speed
            self.mqtt.publish("AWS_IOT/SPEED",msg)
            if distance < 35 and RMS.get_motor_state() == RMS.FORWARD_RUNNING:
                print("Executing stopping motor with object {} cm".format(distance))
                RMS.move_stop()
                RMS.update_motor_state(RMS.COLLISON_DETECT)
        except Exception as e:
            print("Exception happens {}".format(e))
             
        
