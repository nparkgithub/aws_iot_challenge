#!/usr/bin/env python3
"""RoverMotorSensor.py: controlling Rover using RPI GPIO"""

__author__      = "Nam Soo Park"
__copyright__   = "Copyright 2017, AWS_IOT Challenge"

# Universal code to run in Win and RPI
# Check which os is used to run this python code
from sys import platform
import time
import math 
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

# define GPIO for controlling
# front
M1A_ENABLE_GPIO = 3
M1A_INPUT1_GPIO = 5
M1A_INPUT2_GPIO = 9

M2A_ENABLE_GPIO = 4
M2A_INPUT1_GPIO = 11
M2A_INPUT2_GPIO = 10

# rear
M3A_ENABLE_GPIO = 14
M3A_INPUT1_GPIO = 23
M3A_INPUT2_GPIO = 24

M4A_ENABLE_GPIO = 22
M4A_INPUT1_GPIO = 27
M4A_INPUT2_GPIO = 17

#                Enable GPIO           Input 1 GPIO      Input 2 GPIO
fwl_port_info = [[M1A_ENABLE_GPIO, M1A_INPUT1_GPIO, M1A_INPUT2_GPIO],  # left motor
                 [M2A_ENABLE_GPIO, M2A_INPUT1_GPIO, M2A_INPUT2_GPIO]]  # right motor
#                Enable            Input 1           Input 2
rwl_port_info = [[M3A_ENABLE_GPIO, M3A_INPUT1_GPIO, M3A_INPUT2_GPIO],  # left motor
                 [M4A_ENABLE_GPIO, M4A_INPUT1_GPIO, M4A_INPUT2_GPIO]]  # right motor

# select turn
LEFT = 0
RIGHT = 1

# Pin Assignment index
ENABLE = 0
INPUT1 = 1
INPUT2 = 2

# select MOTOR
FWL_MOTOR = 1
FWR_MOTOR = 2
BWL_MOTOR = 3
BWR_MOTOR = 4

# select direction
FORWARD = 1
BACKWARD = 2

bcm_initialized_from_other = False

FORWARD_RUNNING = 1
COLLISON_DETECT = 2
BACKWARD_RUNNING = 3
STOPPED = 0
motor_status = STOPPED

def update_motor_state(status):
    global motor_status
    motor_status = status

def get_motor_state():
    global motor_status
    #print("Motor status {}".format(motor_status))
    return motor_status

def port_init():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.cleanup()
    global bcm_initialized_from_other
    bcm_initialized_from_other = True


def motor_gpio_init():
    # initialize GPIO
    # front - left
    GPIO.setup(M1A_ENABLE_GPIO, GPIO.OUT)
    GPIO.setup(M1A_INPUT1_GPIO, GPIO.OUT)
    GPIO.setup(M1A_INPUT2_GPIO, GPIO.OUT)

    # pwm = GPIO.PWM(M1A_ENABLE_GPIO, 500)
    # pwm.start(0)

    # front - right
    GPIO.setup(M2A_ENABLE_GPIO, GPIO.OUT)
    GPIO.setup(M2A_INPUT1_GPIO, GPIO.OUT)
    GPIO.setup(M2A_INPUT2_GPIO, GPIO.OUT)

    # rear - left
    GPIO.setup(M3A_ENABLE_GPIO, GPIO.OUT)
    GPIO.setup(M3A_INPUT1_GPIO, GPIO.OUT)
    GPIO.setup(M3A_INPUT2_GPIO, GPIO.OUT)

    # rear - right
    GPIO.setup(M4A_ENABLE_GPIO, GPIO.OUT)
    GPIO.setup(M4A_INPUT1_GPIO, GPIO.OUT)
    GPIO.setup(M4A_INPUT2_GPIO, GPIO.OUT)


# pwm = GPIO.PWM(M2A_ENABLE_GPIO, 500)
# pwm.start(0)

def print_port_info():
    print "Forward Left/Left : GPIO Enable, Input1 GPIO, Input2 GPIO"
    print fwl_port_info[LEFT][ENABLE], ":", fwl_port_info[LEFT][INPUT1], ":", fwl_port_info[LEFT][INPUT2]
    print fwl_port_info[RIGHT][ENABLE], ":", fwl_port_info[RIGHT][INPUT1], ":", fwl_port_info[RIGHT][INPUT2]
    print "Backward Left/Right : GPIO Enable, Input1 GPIO, Input2 GPIO"
    print rwl_port_info[LEFT][ENABLE], ":", rwl_port_info[LEFT][INPUT1], ":", rwl_port_info[LEFT][INPUT2]
    print rwl_port_info[RIGHT][ENABLE], ":", rwl_port_info[RIGHT][INPUT1], ":", rwl_port_info[RIGHT][INPUT2]


def motor_setup(motor, direction):
    if direction == FORWARD:
        input1 = True
        input2 = False
    elif direction == BACKWARD:
        input1 = False
        input2 = True
    else:
        print "Undefined Direction"
        exit(1)
    # Check if motor is forward or rear
    if motor == FWL_MOTOR:
        GPIO.output(fwl_port_info[LEFT][INPUT1], input1)
        GPIO.output(fwl_port_info[LEFT][INPUT2], input2)
    elif motor == FWR_MOTOR:
        GPIO.output(fwl_port_info[RIGHT][INPUT1], input1)
        GPIO.output(fwl_port_info[RIGHT][INPUT2], input2)
    elif motor == BWL_MOTOR:
        GPIO.output(rwl_port_info[LEFT][INPUT1], input1)
        GPIO.output(rwl_port_info[LEFT][INPUT2], input2)
    elif motor == BWR_MOTOR:
        GPIO.output(rwl_port_info[RIGHT][INPUT1], input1)
        GPIO.output(rwl_port_info[RIGHT][INPUT2], input2)
    else:
        print "Undefined Motors"
        exit(1)


def motor_enable(motor, enable):
    # Check if motor is forward or rear
    if True == enable or enable == False:
        print "Motor :", motor, "is to set to ", enable
    else:
        print "Undefined enable type"
        exit(1)
    if motor == FWR_MOTOR:
        GPIO.output(fwl_port_info[LEFT][ENABLE], enable)
    elif motor == FWL_MOTOR:
        GPIO.output(fwl_port_info[RIGHT][ENABLE], enable)
    elif motor == BWL_MOTOR:
        GPIO.output(rwl_port_info[LEFT][ENABLE], enable)
    elif motor == BWR_MOTOR:
        GPIO.output(rwl_port_info[RIGHT][ENABLE], enable)
    else:
        print "Undefined Motors"
        exit(1)

pwm1 = 0
pwm2 = 0
pwm3 = 0
pwm4 = 0

def motor_pwm_set(motor, freq, duty_cycle):
    # Check if motor is forward or rear
    print "motor pwm set", motor, " ", freq, " " ,duty_cycle
    if motor == FWL_MOTOR:
        global pwm1
        motor_enable(FWL_MOTOR, True)
        pwm1 = GPIO.PWM(fwl_port_info[LEFT][ENABLE], freq)
        pwm1.start(0)
        # pwm1.ChangeDutyCycle(duty_cycle)
    elif motor == FWR_MOTOR:
        global pwm2
        motor_enable(FWR_MOTOR, True)
        pwm2 = GPIO.PWM(fwl_port_info[RIGHT][ENABLE], freq)
        pwm2.start(0)
        # pwm2.ChangeDutyCycle(duty_cycle)
    elif motor == BWL_MOTOR:
        global pwm3
        motor_enable(BWL_MOTOR, True)
        pwm3 = GPIO.PWM(rwl_port_info[LEFT][ENABLE], freq)
        pwm3.start(0)
        # pwm3.ChangeDutyCycle(duty_cycle)
    elif motor == BWR_MOTOR:
        global pwm4
        motor_enable(BWR_MOTOR, True)
        pwm4 = GPIO.PWM(rwl_port_info[RIGHT][ENABLE], freq)
        pwm4.start(0)
        # pwm4.ChangeDutyCycle(duty_cycle)
    else:
        print "Undefined Motors"
        exit(1)


def motor_change_speed(motor, duty_cycle):
    # Check if motor is forward or rear
    print "motor change speed =", " " ,duty_cycle
    if motor == FWL_MOTOR:
        pwm1.ChangeDutyCycle(duty_cycle)
    elif motor == FWR_MOTOR:
        pwm2.ChangeDutyCycle(duty_cycle)
    elif motor == BWL_MOTOR:
        pwm3.ChangeDutyCycle(duty_cycle)
    elif motor == BWR_MOTOR:
        pwm4.ChangeDutyCycle(duty_cycle)
    else:
        print "Undefined Motors"
        exit(1)


def move_forward(walk_time):
    print "\nmove forward for ", walk_time, "second(s)"
    motor_setup(FWL_MOTOR, FORWARD)
    motor_setup(FWR_MOTOR, FORWARD)
    motor_setup(BWL_MOTOR, FORWARD)
    motor_setup(BWR_MOTOR, FORWARD)

    motor_enable(FWL_MOTOR, True)
    motor_enable(FWR_MOTOR, True)
    motor_enable(BWL_MOTOR, True)
    motor_enable(BWR_MOTOR, True)

    time.sleep(walk_time)
    move_stop()

def test_wheel(walk_time):
    print "\nmove forward for ", walk_time, "second(s)"
    motor_setup(FWL_MOTOR, FORWARD)
    motor_setup(FWR_MOTOR, FORWARD)
    motor_setup(BWL_MOTOR, FORWARD)
    motor_setup(BWR_MOTOR, FORWARD)
    print("Front Left triggering")
    motor_enable(FWL_MOTOR, True)
    time.sleep(walk_time)
    motor_enable(FWL_MOTOR, False)
    print("Front Right triggering") 
    motor_enable(FWR_MOTOR, True)
    time.sleep(walk_time)
    motor_enable(FWR_MOTOR, False)
    print("Rear Left triggering")
    motor_enable(BWL_MOTOR, True)
    time.sleep(walk_time)
    motor_enable(BWL_MOTOR, False)
    print("Rear Right triggering")
    motor_enable(BWR_MOTOR, True)
    time.sleep(walk_time)
    motor_enable(BWR_MOTOR, False)
    
    print("Turning Right")
    turn_right()
    print("Truing Left")
    turn_left()


def move_backward(walk_time):
    print "\nmove backward for ", walk_time, "second(s)"
    motor_setup(FWL_MOTOR, BACKWARD)
    motor_setup(FWR_MOTOR, BACKWARD)
    motor_setup(BWL_MOTOR, BACKWARD)
    motor_setup(BWR_MOTOR, BACKWARD)

    motor_enable(FWL_MOTOR, True)
    motor_enable(FWR_MOTOR, True)
    motor_enable(BWL_MOTOR, True)
    motor_enable(BWR_MOTOR, True)

    time.sleep(walk_time)
    move_stop()


def move_stop():
    print "\n All motors are stopped"
    try:
        motor_enable(FWL_MOTOR, False)
        motor_enable(FWR_MOTOR, False)
        motor_enable(BWL_MOTOR, False)
        motor_enable(BWR_MOTOR, False)
        pwm1.ChangeDutyCycle(0)
        pwm2.ChangeDutyCycle(0)
        pwm3.ChangeDutyCycle(0)
        pwm4.ChangeDutyCycle(0)
        pwm1.stop()
        pwm2.stop()
        pwm3.stop()
        pwm4.stop()
    except Exception as e:
        print("Error to stop error ={}".format(e))
    # motor_speed_setup(FWR_MOTOR)


def turn_left():
    print "turn left"
    motor_setup(FWL_MOTOR, FORWARD)
    motor_setup(FWR_MOTOR, FORWARD)
    motor_setup(BWL_MOTOR, FORWARD)
    motor_setup(BWR_MOTOR, FORWARD)

    motor_enable(FWL_MOTOR, False)
    motor_enable(FWR_MOTOR, True)
    motor_enable(BWL_MOTOR, False)
    motor_enable(BWR_MOTOR, True)

    time.sleep(0.25)
    move_stop()


def turn_right():
    print "turn right"
    motor_setup(FWL_MOTOR, FORWARD)
    motor_setup(FWR_MOTOR, FORWARD)
    motor_setup(BWL_MOTOR, FORWARD)
    motor_setup(BWR_MOTOR, FORWARD)

    motor_enable(FWL_MOTOR, True)
    motor_enable(FWR_MOTOR, False)
    motor_enable(BWL_MOTOR, True)
    motor_enable(BWR_MOTOR, False)

    time.sleep(0.25)
    move_stop()

FREQ = 10
TURN_LOW_SPEED = 20  # 30 % duty cycle
TURN_HIGH_SPEED = 80  # 50 % duty cycle


def turn_left_speed_daneil(speed):
    print "turn left with speed" , speed
    motor_setup(FWL_MOTOR, FORWARD)
    motor_setup(FWR_MOTOR, FORWARD)
    motor_setup(BWL_MOTOR, FORWARD)
    motor_setup(BWR_MOTOR, FORWARD)

    # motor_enable(FWL_MOTOR, True)
    motor_pwm_set(FWL_MOTOR, FREQ, TURN_HIGH_SPEED)
    # motor_enable(FWR_MOTOR, False)
    motor_pwm_set(FWR_MOTOR, FREQ, TURN_LOW_SPEED)

    # motor_enable(BWL_MOTOR, False)
    motor_pwm_set(BWL_MOTOR, FREQ, TURN_LOW_SPEED)
    # motor_enable(BWR_MOTOR, True)
    motor_pwm_set(BWR_MOTOR, FREQ, TURN_HIGH_SPEED)

    time.sleep(1)
    #move_stop()


def motor_speed_setup(direction):
    print "motor speed setup = "
    motor_setup(FWL_MOTOR, direction)
    motor_setup(FWR_MOTOR, direction)
    motor_setup(BWL_MOTOR, direction)
    motor_setup(BWR_MOTOR, direction)

    # motor_enable(FWL_MOTOR, False)
    motor_pwm_set(FWL_MOTOR, FREQ, 0)
    # motor_enable(FWR_MOTOR, True)
    motor_pwm_set(FWR_MOTOR, FREQ, 0)

    # motor_enable(BWL_MOTOR, True)
    motor_pwm_set(BWL_MOTOR, FREQ, 0)
    # motor_enable(BWR_MOTOR, False)
    motor_pwm_set(BWR_MOTOR, FREQ, 0)


def turn_left_speed(speed):
    step = 5
    print "turn left speed =", speed * step, "%"
    motor_speed_setup(FORWARD)
    motor_change_speed(FWL_MOTOR, speed * step)
    motor_change_speed(FWR_MOTOR, TURN_LOW_SPEED)
    motor_change_speed(BWL_MOTOR, TURN_LOW_SPEED)
    motor_change_speed(BWR_MOTOR, speed * step)

    time.sleep(1)
    #move_stop()


def turn_right_speed(speed):
    step = 5
    print "turn right speed =", speed * step, "%"
    motor_speed_setup(FORWARD)
    motor_change_speed(FWL_MOTOR, speed * step)
    motor_change_speed(FWR_MOTOR, 0)
    motor_change_speed(BWL_MOTOR, speed * step)
    motor_change_speed(BWR_MOTOR, 0)
    """
    motor_speed_setup(FORWARD)
    motor_change_speed(FWL_MOTOR, TURN_LOW_SPEED)
    motor_change_speed(FWR_MOTOR, speed * step)
    motor_change_speed(BWL_MOTOR, speed * step)
    motor_change_speed(BWR_MOTOR, TURN_LOW_SPEED)
    """
    #time.sleep(1)
    #move_stop()


def move_forward_speed(speed):
    step = 5
    print "move forward speed =", speed * step, "%d"
    motor_speed_setup(FORWARD)
    motor_change_speed(FWL_MOTOR, speed * step)
    motor_change_speed(FWR_MOTOR, speed * step)
    motor_change_speed(BWL_MOTOR, speed * step)
    motor_change_speed(BWR_MOTOR, speed * step)

    #time.sleep(1)
    #move_stop()


def move_backward_speed(speed):
    step = 5
    print "move backward speed =", speed * step, "%d"
    motor_speed_setup(BACKWARD)
    motor_change_speed(FWL_MOTOR, speed * step)
    motor_change_speed(FWR_MOTOR, speed * step)
    motor_change_speed(BWL_MOTOR, speed * step)
    motor_change_speed(BWR_MOTOR, speed * step)

    #time.sleep(1)
    #move_stop()

def rover_test():
    port_init()
    motor_gpio_init()
    print_port_info()

    #move_forward(2)
    #move_backward(2)
    while True:
        cmd = raw_input("command, l/r/s or fx or bx x is second:")
        if cmd[0] == "r":
            if len(cmd) == 1:
                speed = 8
            else:
                speed = int(cmd[1])
            turn_right_speed(speed)
        elif cmd[0] == "l":
            if len(cmd) == 1:
                speed = 8
            else:
                speed = int(cmd[1])
            turn_left_speed(speed)
        elif cmd[0] == "f":
            if len(cmd) == 1:
                speed = 8
            else:
                speed = int(cmd[1])
            move_forward_speed(speed)
        elif cmd[0] == "b":
                if len(cmd) == 1:
                    speed = 8
                else:
                    speed = int(cmd[1])
                move_backward_speed(speed)
        elif cmd[0] == "s":
                move_stop()
        elif cmd[0] == "q":
                move_stop()
                print "BYE"
                exit(1)
        else:
            exit(1)
