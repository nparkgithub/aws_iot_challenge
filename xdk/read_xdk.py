#!/usr/bin/env python3
"""read_xdk.py: Read sensor data from Bosh XDK"""

__author__      = "Nam Soo Park"
__copyright__   = "Copyright 2017, AWS_IOT Challenge"

import serial
from mqtt_publisher import *

class Serializer: 
    def __init__(self, port, baudrate=9600, timeout=.1): 
        self.port = serial.Serial(port = port, baudrate=baudrate, 
        timeout=timeout, writeTimeout=timeout)

    def open(self): 
        self.port.open()

    def close(self): 
        self.port.close() 

    def send(self, msg):
        self.port.write(msg)

    def recv(self):
        return self.port.readline()

PORT = '/dev/ttyACM0' 


# test main class made for testing
def main():
    test_port = Serializer(port = PORT)

    while True:
        #print(test_port.recv())
	line = test_port.recv()
	line = line.strip()
#	print line 
	if line.startswith("BOSCH_XDK") == True:
		send_sensor_data(line)
		print line
if __name__ == "__main__":
    main()
