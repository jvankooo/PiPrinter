import numpy as np
import servo2
import math
import time

savedir="Camera_Data/"

map_A = np.load(savedir+'servoA.npy')
map_B = np.load(savedir+'servoB.npy')

steps = len(map_A)
wait = 0.3

def vect_to_deg(x, y):
	
	servo_A, servo_B = 0, 0
	
	try:
		A = list(map(lambda k: k >= y, map_A)).index(True)-1
		if map_A[A] == y:
			servo_A = A*180/(steps-1)
		else:
			servo_A = A*180/(steps-1) + (y-map_A[A])*(180/(steps-1))/(map_A[A+1]-map_A[A])
	except:
		servo_A = 180
		y = map_A[steps-1]
		
	try:	
		B = list(map(lambda k: k >= x, map_B)).index(True)-1
		if map_B[B] == x:
			servo_B = B*180/(steps-1)
		else:
			servo_B = B*180/(steps-1) + (x-map_B[B])*(180/(steps-1))/(map_B[B+1]-map_B[B])
	except:
		servo_B = 180
		x = map_B[steps-1]

	return servo_A, servo_B, x, y


servo2.home()	
cX, cY = 0.0, 0.0
print("maps : ", map_A, map_B, "\n")

# Main 
while(True):
	y, x = [float(j) for j in input("Location y x :").split()]
	a, b, x, y = vect_to_deg(x, y)
	print("angle A: ", round(a,1), " angle B: ", round(b,1))
	_ = servo2.A(a, wait)
	_ = servo2.B(b, wait)
	time.sleep(wait)
	#  Calculate Displacement
	s = math.sqrt((cX-x)**2+(cY-y)**2)
	cX, cY = x, y
	print("Servo Set. Displacement : ", s)

