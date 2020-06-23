import RPi.GPIO as GPIO
import time

servoPIN_A = 17
servoPIN_B = 27
servoPIN_C = 22
range_A = [2.5, 11.5]
range_B = [2.5, 12.0]
GPIO.setmode(GPIO.BCM)
GPIO.setup(servoPIN_A, GPIO.OUT)
GPIO.setup(servoPIN_B, GPIO.OUT)
GPIO.setup(servoPIN_C, GPIO.OUT)
t = 0.3

sA = GPIO.PWM(servoPIN_A, 50) # GPIO 17 for PWM with 50Hz
sB = GPIO.PWM(servoPIN_B, 50)
sC = GPIO.PWM(servoPIN_C, 50)

def home():
    sA.start(2.5)
    sB.start(2.5)
    sC.start(8.0)
    time.sleep(t)
    GPIO.output(servoPIN_A, False)
    GPIO.output(servoPIN_B, False)
    GPIO.output(servoPIN_C, False)
    return 1

# Convert Degrees to Duty Cycle
def deg_to_duty_A(deg):
    ang = 2.5 + (range_A[1]-range_A[0])*deg/180
    return round(ang, 1)
    
def deg_to_duty_B(deg):
    ang = 2.5 + (range_B[1]-range_B[0])*deg/180
    return round(ang, 1)
    
def deg_to_duty(deg):
    ang = 2.5 + 10.0*deg/180
    return round(ang, 1)

def A(d,t):
    GPIO.output(servoPIN_A, True)
    x = deg_to_duty_A(d)
    sA.ChangeDutyCycle(x)
    time.sleep(t)
    GPIO.output(servoPIN_A, False)
    return 1

def B(d,t):
    GPIO.output(servoPIN_B, True)
    x = deg_to_duty_B(d)
    sB.ChangeDutyCycle(x)
    time.sleep(t)
    GPIO.output(servoPIN_B, False)
    return 1

def C(d,t):
    GPIO.output(servoPIN_C, True)
    x = deg_to_duty(d)
    sC.ChangeDutyCycle(x)
    time.sleep(t)
    GPIO.output(servoPIN_C, False)
    return 1
    
def C_home():
    sC.start(8.0)
    time.sleep(t)
    GPIO.output(servoPIN_A, False)
    GPIO.output(servoPIN_B, False)
    GPIO.output(servoPIN_C, False)
    return 1
def exit():
    sA.stop()
    sB.stop()
    sC.stop()
    GPIO.cleanup()
