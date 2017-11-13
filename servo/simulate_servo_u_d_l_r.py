#!/usr/bin/env python3
"""simulate_servo_u_d_l_r.py: Controlling Servo motors to make it up down/left right"""

__author__      = "Nam Soo Park"
__copyright__   = "Copyright 2017, AWS_IOT Challenge"

import RPi.GPIO as GPIO
import time
import random
import threading 
import paho.mqtt.client as mqtt
import json


GPIO_UP_DOWN_NO = 6 # up and down motor
GPIO_RIGH_LEFT_NO = 13 # left and right

GPIO.setmode(GPIO.BCM)


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

class ServoMotor(object):
    """ Representation of Servor Motor Controller """
    def __init__(self, gpio=6):
        self.gpio = gpio
        self.curr_pos = 0.0
        GPIO.setup(self.gpio, GPIO.OUT)
        self.p = GPIO.PWM(self.gpio, 50)   #sets pin 21 to PWM and sends 50 signals per second
        self.p.start(7.5)         #starts by sending a pulse at 7.5% to center the servo

        self.move_to_center()
        time.sleep(1)
        self.move_to_bottom()

    def move_up(self, step):
        self.curr_pos -= step;
        print 'new position %d' % self.curr_pos
        if self.curr_pos < 4.5:
            print 'out of range'
            self.curr_pos *= 2
            #return False
        self.p.ChangeDutyCycle(self.curr_pos)
        return True

    def move_down(self, step):
        self.curr_pos = self.curr_pos + step;
        print 'new position %d' % self.curr_pos
        if self.curr_pos > 10.5:
            print 'out of range'
            self.curr_pos /= 2
            #return False
        self.p.ChangeDutyCycle(self.curr_pos)
        return True

    def start(self):
        self.p.start(self.curr_pos)

    def stop(self):
        self.p.stop(self.curr_pos)

    def cleanup(self):
        GPIO.cleanup()

    def move_to_center(self):
        print 'move to center'
        self.p.ChangeDutyCycle(7.5)
        self.curr_pos = 7.5

    def move_to_bottom(self):
        print 'move to bottom'
        self.p.ChangeDutyCycle(10.5)
        self.curr_pos = 10.5

    def move_to_top(self):
        print 'move to top'
        self.p.ChangeDutyCycle(4.5)
        self.curr_pos = 4.5

    def move_to_right_most(self):
        self.move_to_bottom()

    def move_to_left_most(self):
        self.move_to_down()

    def move_left(self, step):
        self.move_down(step)

    def move_right(self,step):
        self.move_up(step)
    

def simulate_up_down_motor(move_step = 1.5, interval =1):
    motor = ServoMotor(GPIO_UP_DOWN_NO) 
    mqtt = Mqtt_Publisher()
    msg = {}

    try:
        option = ["up","down"]
        while True:
            time.sleep(interval)
            cmd = random.choice(option)
            if cmd == "up":
                if motor.move_up(move_step) == False:
                    motor.start()
            elif cmd == "down":
                if motor.move_down(move_step) == False:
	               motor.start()
            msg["up_down"] = 1 if cmd  == "up" else 0
            mqtt.publish("AWS_IOT/UP_DOWN", msg)  
    except KeyboardInterrupt:
        motor.stop()
        motor.cleanup()


def simulate_right_lef_motor(move_step = 1.5, interval = 1):
    motor = ServoMotor(GPIO_RIGH_LEFT_NO) 
    mqtt = Mqtt_Publisher()
    msg = {}
    try:
       option = ["right","left"]
       while True:
            time.sleep(interval)
            cmd = random.choice(option)
            if cmd == "right":
                if motor.move_right(move_step) == False:
                    motor.start()
            elif cmd == "left":
                if motor.move_left(move_step) == False:
                   motor.start()
            msg["right_left"] = 1 if cmd  == "right" else 0
            mqtt.publish("AWS_IOT/RIGHT_LEFT", msg)  
    except KeyboardInterrupt:
        motor.stop()
        motor.cleanup()

def main():
    #simulate_right_lef_motor()
    #simulate_up_down_motor()
    t1 = threading.Thread(target=simulate_right_lef_motor)
    t2 = threading.Thread(target=simulate_up_down_motor)
    t1.start()
    t2.start()
if __name__ == "__main__":
    main()

