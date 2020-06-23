import cv2
import numpy as np
import servo
import matplotlib.pyplot as plt

savedir="Camera_Data/"

cam_mtx=np.load(savedir+'cam_mtx.npy')
dist=np.load(savedir+'dist.npy')
newcam_mtx=np.load(savedir+'newcam_mtx.npy')
h_mat=np.load(savedir+'h_mtx.npy')
ratio = np.load(savedir+'ratio.npy')
hsv_range = np.load(savedir+'color.npy')


oX, oY = 0, 480
cX, cY = 0, 0
l, m = 0, 0
wait = 0.3
cal_flag = False
cal_angle = False
angle_err = 0.0
# HSV color range
lower_hue = hsv_range[0]
upper_hue = hsv_range[1]

def set_origin(u,v):
	global oX, oY
	oX = u
	oY = v

def calculate_position(u,v):
									  
		#Solve: From Image Pixels, find World Points
		XY = [(u-oX)/ratio[0],(oY-v)/ratio[1]]
		return XY

def truncate(n, decimals=0):
	n=float(n)
	multiplier = 10 ** decimals
	return int(n * multiplier) / multiplier
    
# Main
# ~ cam = cv2.VideoCapture(0)
TriggerTime = 0
steps = int(input("Angular Steps ? "))
delay = int(input("Camera Delay ? "))

cam_address = input("Camera Address : ")
cam = cv2.VideoCapture('http://'+cam_address+':8080/mjpegfeed?640x480')

while(cam.isOpened()):
# while(True):
	_, frame = cam.read()
	# ~ print(delay-TriggerTime)
	if TriggerTime >= delay:
		# Apply camera calibration variables
		frame = cv2.undistort(frame, cam_mtx, dist, None, newcam_mtx)
		frame = cv2.warpPerspective(frame, h_mat, (frame.shape[1], frame.shape[0]))
		# Fix error angle
		if not cal_angle:
			(h, w) = frame.shape[:2]
			M = cv2.getRotationMatrix2D((oX,oY), angle_err, 1.0)
			frame = cv2.warpAffine(frame, M, (w,h))

		output = frame.copy()
		hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
		
		mask = cv2.inRange(hsv, lower_hue, upper_hue)

		# Reduce noise in mask
		kernel = np.ones((3,3),np.uint8)
		erosion = cv2.erode(mask, kernel, iterations = 2)
		dilation = cv2.dilate(erosion,kernel,iterations = 2)
		blur = cv2.GaussianBlur(dilation,(5,5),0)

		res = cv2.bitwise_and(frame,frame, mask= dilation)
		
		contours,_= cv2.findContours(blur, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

		for cnt in contours:
			approx = cv2.approxPolyDP(cnt, 0.01*cv2.arcLength(cnt, True), True)
			if cv2.contourArea(cnt) > 100:
				x, y, w, h = cv2.boundingRect(approx)
				x = x + w/2
				y = y + h/2
				pt = calculate_position(x,y)
				x = np.round(x).astype("int")
				y = np.round(y).astype("int")
				cv2.rectangle(output, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
				cv2.putText(output,str(truncate(pt[0],2)) +", " +str(truncate(pt[1], 2)),(x+10,y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 0,255),2)
				# Update Points
				cX, cY = pt[0], pt[1]
		
		cv2.circle(output, (oX, oY), 4, (0, 255, 255), 4)
		# show the output image
		# ~ cv2.imshow("output", output)
		cv2.imshow("video", np.vstack([res,output]))
		
		k = cv2.waitKey(200)
		
		if k & 0xFF == ord('q'):
			servo.exit()
			break
		
		if k & 0xFF == ord('h'):
			_ = servo.home()
			print("slider at home")
			
		if k & 0xFF == ord('o'):
			set_origin(x, y)
			print("Origin Set to ( ", cX, ", ", cY, " )")

		if k & 0xFF == ord('a'):
			_ = servo.home()
			l = 0
			cal_angle = True
			print("Removing Angular Error")

		if k & 0xFF == ord('c'):
			# ~ steps = int(input("Angular Steps ? "))
			# ~ wait = float(input("Wait Time in sec? "))
			map_A = np.zeros(shape=((steps+1), 2))
			map_B = np.zeros(shape=((steps+1), 2))
			l, m =0, 0
			cal_flag = True
			print("Servo Calibration Started")

		# Calculate Angular Error
		if(cal_angle):
			cv2.waitKey(int(wait*2000))
			# Move in X
			if l == 0:
				pass
			if l == 1:
				_ = servo.A(180,wait)
				angle_err = 0
			if l == 2:
				# Calculate angle - cosine rule
				try:
					delta = x-oX
					side = y-oY
					angle_err = np.sign(delta)*(np.arccos(1-delta**2/(2*side**2)))
				except:
					angle_err = 0
				print("Err Y: ", angle_err)
				_ = servo.A(0,wait)
				_ = servo.B(180,wait)
			if l == 3:
				# Calculate angle - cosine rule
				try:
					delta = oY-y
					side = x-oX
					temp = np.sign(delta)*(np.arccos(1-delta**2/(2*side**2)))
				except:
					temp = 0
				angle_err = (angle_err+temp)/2
				print("Err X: ", temp)
				_ = servo.B(0,wait)
			if l == 4:
				cal_angle = False
				print("Error Angle: ", angle_err, " \n Angle Calibration Done. Slider at Home")
			l+=1



			

		# Calibrate Servos
		if(cal_flag):
			cv2.waitKey(int(wait*2000))
			# X axis
			if l <= steps:
				# Save Position
				map_B[l][0] = l*180/steps
				map_B[l][1] += cX
				# Y axis
				if m <= steps:
					if(m != 0):
						map_A[m-1][1] += cY
						print("servoY: ", map_A[m-1][0], ", Y: ",cY)
					map_A[m][0] = m*180/steps
					_ = servo.A(map_A[m][0], wait)
					m += 1
				else:
					map_A[m-1][1] += cY
					print("servoY: ", map_A[m-1][0], ", Y: ",cY)
					print("servoX: ", map_B[l][0], ", X: ",cX)
					# Set New Angle B
					l += 1
					if(l<steps+1):
						map_B[l][0] = l*180/steps
						_ = servo.B(map_B[l][0], wait)	
						m = 0
						print("Shift X")
			else:
				print("Calibration Successful \n Slider at Home \n")
				_ = servo.home()
				cv2.waitKey(1000)
				angle = np.zeros(shape=(steps+1))
				pltA = np.zeros(shape=(steps+1))
				pltB = np.zeros(shape=(steps+1))
				for l in range (0,steps+1):
					map_A[l][1] = (map_A[l][1]-map_A[0][1])/(steps+1)
					map_B[l][1] = (map_B[l][1]-map_B[0][1])/(steps+1)
					angle[l] = l*180/steps
					pltA[l] = map_A[l][1]
					pltB[l] = map_B[l][1]
				servo.exit()
				print("Servo A : \n", map_A,"\n Servo B : \n", map_B)
				np.save(savedir+'servoA.npy', np.array(pltA))
				np.save(savedir+'servoB.npy', np.array(pltB))
				cal_flag = False
				l, m = 0, 0
				plt.figure()
				ay = plt.subplot(211)
				ay.plot(angle, pltA,'-', angle, pltA, 'ro')
				ay.set_ylabel('Position Y')
				bx = plt.subplot(212)
				bx.plot(angle, pltB,'-', angle, pltB, 'ro')
				bx.set_ylabel('Position X')
				bx.set_xlabel('Servo Angle')
				plt.show()
								
		
		TriggerTime = 0
				

	TriggerTime += 1
