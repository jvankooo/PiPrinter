import pigpio
import time

pi = pigpio.pi()

servoPIN_A = 17
servoPIN_B = 27
servoPIN_C = 22
range_A = [1000, 1900]
range_B = [1000, 1950]

t = 0.3

def home():
	pi.set_servo_pulsewidth(servoPIN_A, 1000)
	pi.set_servo_pulsewidth(servoPIN_B, 1000)
	pi.set_servo_pulsewidth(servoPIN_C, 1700)
	time.sleep(t)
	pi.set_servo_pulsewidth(servoPIN_A, 0)
	pi.set_servo_pulsewidth(servoPIN_B, 0)
	pi.set_servo_pulsewidth(servoPIN_C, 0)
	return 1
	
# Convert Degrees to Duty Cycle
def deg_to_duty_A(deg):
    ang = 1000 + (range_A[1]-range_A[0])*deg/180
    return int(ang)
    
def deg_to_duty_B(deg):
    ang = 1000 + (range_B[1]-range_B[0])*deg/180
    return int(ang)
    
def deg_to_duty(deg):
    ang = 1000 + 1000*deg/180
    return int(ang)

def A(d,t):
    x = deg_to_duty_A(d)
    pi.set_servo_pulsewidth(servoPIN_A, x)
    time.sleep(t)
    pi.set_servo_pulsewidth(servoPIN_A, 0)
    return 1

def B(d,t):
    x = deg_to_duty_B(d)
    pi.set_servo_pulsewidth(servoPIN_B, x)
    time.sleep(t)
    pi.set_servo_pulsewidth(servoPIN_B, 0)
    return 1

def C(d,t):
    x = deg_to_duty(d)
    pi.set_servo_pulsewidth(servoPIN_C, x)
    time.sleep(t)
    pi.set_servo_pulsewidth(servoPIN_C, 0)
    return 1
    
def C_home():
    pi.set_servo_pulsewidth(servoPIN_C, 1700)
    time.sleep(t)
    pi.set_servo_pulsewidth(servoPIN_C, 0)
    return 1
    
def exit():
    pi.set_servo_pulsewidth(servoPIN_A, 0)
    pi.set_servo_pulsewidth(servoPIN_B, 0)
    pi.set_servo_pulsewidth(servoPIN_C, 0)
    pi.stop()
