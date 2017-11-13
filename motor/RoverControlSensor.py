#!/usr/bin/env python3
"""RoverControlSensor.py: Main program for controlling Rover"""

__author__      = "Nam Soo Park"
__copyright__   = "Copyright 2017, AWS_IOT Challenge"

import RoverMotorSensor as RM
import threading
import sys
import time
import threading
import signal
import os
from Sensors import DetectObject

class ThreadJob(threading.Thread):
    def __init__(self,function):
        threading.Thread.__init__(self)
        self.function = function

        # The shutdown_flag is a threading.Event object that
        # indicates whether the thread should be terminated.
        self.shutdown_flag = threading.Event()

        # ... Other thread setup code here ...

    def run(self):
        print('Thread #%s started' % self.ident)

        while not self.shutdown_flag.is_set():
            # ... Job code here ...
            self.function()

        # ... Clean shutdown code here ...
        print('Thread #%s stopped' % self.ident)


class ServiceExit(Exception):
    """
    Custom exception which is used to trigger the clean exit
    of all running threads and the main program.
    """
    pass


def service_shutdown(signum, frame):
    print('Caught signal %d' % signum)
    raise ServiceExit

simulate_movement_started = False

def simulate_movement():
    # Rover init
    global simulate_movement_started
    if simulate_movement_started == False:
        RM.port_init()
        RM.motor_gpio_init()
        RM.print_port_info()
        RM.update_motor_state(RM.STOPPED)
        simulate_movement_started = True
    
    senariors = ["f", "f","f", "b", "b","b"] * 3

    speed = 1

    for cmd in senariors:
        try:
            
            if cmd == "r":
                RM.turn_right()
            elif cmd == "l":
                RM.turn_left()
            elif cmd == "f":
                if RM.get_motor_state() == RM.COLLISON_DETECT:
                    print("Can not execute due to Collision detect")
                else:         
                        #speed = 8
                    RM.update_motor_state(RM.FORWARD_RUNNING)
                    RM.move_forward(speed)                
            elif cmd == "c":
                if RM.get_motor_state() == RM.COLLISON_DETECT:
                    print("Can not execute due to Collision detect")
                else:      
                    RM.update_motor_state(RM.FORWARD_RUNNING)   
                    #speed = 8
                    RM.move_forward(20)
            elif cmd == "b":
                RM.update_motor_state(RM.BACKWARD_RUNNING)
                    #speed = 8
                RM.move_backward(speed)                
            elif cmd == "s":
                RM.move_stop()
            elif cmd == "q":
                RM.move_stop()
                #CM.stop()
                print "BYE"
                exit(1)
            else:
                print("Invalid input ={}".format(cmd))
        except Exception as e:
            print("Error whiling processing input ={}".format(e))
        
    input = raw_input("try again(any key) or quit(Ctrl-C)")

def main():
    dt_obj = DetectObject()
    # Register the signal handlers
    signal.signal(signal.SIGTERM, service_shutdown)
    signal.signal(signal.SIGINT, service_shutdown)

    print('Starting main program')

    # Start the job threads
    try:
        j1 = ThreadJob(dt_obj.measure_location_speed)
        j1.start()

        j2 = ThreadJob(simulate_movement)
        j2.start()

        # Keep the main thread running, otherwise signals are ignored.
        while True:
            time.sleep(0.5)

    except ServiceExit:
        # Terminate the running threads.
        # Set the shutdown flag on each thread to trigger a clean shutdown of each thread.
        j1.shutdown_flag.set()
        j2.shutdown_flag.set()
        #os.system("sudo kill -9 " + str(os.getpid())
     

    print('Exiting main program')


if __name__ == '__main__':
    main()


