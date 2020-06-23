import numpy as np
import cv2
import servo2
import math
import time

savedir="Camera_Data/"

map_A = np.load(savedir+'servoA.npy')
map_B = np.load(savedir+'servoB.npy')
ratio = np.load(savedir+'ratio.npy')

steps = len(map_A)
wait = 0.3
scale = 1.0
servoC = 100

# Camera settimgs
p_width = map_B[steps-1]*ratio[0]
p_height = map_A[steps-1]*ratio[1]
print("Image resolution : ", p_width, "x", p_height)


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


_ = servo2.home()	
cX, cY = 0.0, 0.0
print("maps : ", map_A, map_B, "\n")

# Initialize the camera
# ~ cam = cv2.VideoCapture(0)
# ~ cv2.waitKey(500)
# ~ _, frame = cam.read()
frame = cv2.imread('Images/print.jpg')

if(frame.shape[1]/p_width > frame.shape[0]/p_height):
	scale = frame.shape[1]/p_width
else:
	scale = frame.shape[0]/p_height
	
print("Scale : ", scale)

while(True):
	
	# ~ _, frame = cam.read()
	cv2.imshow("Camera", frame)
	k = cv2.waitKey(10)
		
	if k & 0xFF == ord('c'):
		newX, newY = int(frame.shape[1]/scale), int(frame.shape[0]/scale)
		scaled = cv2.resize(frame,(newX, newY))
		gray = cv2.cvtColor(scaled, cv2.COLOR_BGR2GRAY)
		bnw = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)[1]
		cv2.imshow("Capture", bnw)
		cv2.waitKey(200)
		cv2.destroyWindow("Capture")
		
	if k & 0xFF == ord('w'):
		servoC -= 5
		_ = servo2.C(servoC,wait)
		time.sleep(wait)
		_ = servo2.C_home()
		
	if k & 0xFF == ord('s'):
		servoC += 5
		_ = servo2.C(servoC,wait)
		time.sleep(wait)
		_ = servo2.C_home()
		
	if k & 0xFF == ord('p'):
		rows,cols = bnw.shape
		line = False
		for i in range(rows):
			sA, _, _, _ = vect_to_deg(0/ratio[0],i/ratio[1])
			_ = servo2.A(sA, wait)
			time.sleep(wait)
			for j in range(cols):
				_, sB, _, _ = vect_to_deg(j/ratio[0],i/ratio[1])
				print(sB,sA,bnw[i,j])
				if(bnw[i,j]==0 and not line):
					line = True
					_ = servo2.B(sB, wait)
					time.sleep(wait)
				if(line and bnw[i,j] == 255):
					line = False
					_ = servo2.C(servoC, wait)
					_ = servo2.B(sB, wait)
					time.sleep(wait)
					_ = servo2.C_home()

				k = cv2.waitKey(10)
				bnw[i,j] = 0
				cv2.imshow("Printing", bnw)
				
				if k & 0xFF == ord('w'):
					servoC -= 5
					
				if k & 0xFF == ord('s'):
					servoC += 5
		print("---------------- Print Job Complete ------------------")
		_ = servo2.home()
		

	if k & 0xFF == ord('q'):
		break
	
servo2.exit()	
cam.release()
cv2.destroyAllWindows()
