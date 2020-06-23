import cv2
import numpy as np

savedir="Camera_Data/"

cam_mtx=np.load(savedir+'cam_mtx.npy')
dist=np.load(savedir+'dist.npy')
newcam_mtx=np.load(savedir+'newcam_mtx.npy')
h_mat=np.load(savedir+'h_mtx.npy')
ratio = np.load(savedir+'ratio.npy')

oX, oY = 0, 480
cX, cY = 0, 0
# HSV color range
lower_hue = np.array([0,100,2])
upper_hue = np.array([1,150,50])

def set_origin(u,v):
	global oX, oY
	oX = u
	oY = v

def click_hsv(event, x, y, flags, param):
	if event == cv2.EVENT_LBUTTONDOWN:
		# BGR to HSV pixel value
		bgr = frame[y,x]
		global lower_hue
		global upper_hue
		hsv = cv2.cvtColor(np.uint8([[bgr]]), cv2.COLOR_BGR2HSV)
		print("hsv: ", hsv[0][0])
		bounds = [hsv[0][0][0]-35, hsv[0][0][1]-60, hsv[0][0][2]-30, hsv[0][0][0]+35, hsv[0][0][1]+60, hsv[0][0][2]+30]
		j=0
		for i in bounds:
			if bounds[j] < 0:
				bounds[j] = 0
			if bounds[j] > 255:
				bounds[j] = 255
			j+=1
		lower_hue = np.array([bounds[0], bounds[1], bounds[2]])
		upper_hue = np.array([bounds[3], bounds[4], bounds[5]])
		hsv_range = np.array([lower_hue, upper_hue])
		print("New Bounds: " , lower_hue, upper_hue)
		np.save(savedir+'color.npy', hsv_range)

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
cam_address = input("Camera Address : ")
cam = cv2.VideoCapture('http://'+cam_address+':8080/mjpegfeed?640x480')
# ~ cam.set(cv2.CAP_PROP_BUFFERSIZE, 0)
cv2.namedWindow("video")
cv2.setMouseCallback("video", click_hsv)

while(cam.isOpened()):
	_, frame = cam.read()
	# Apply camera calibration variables
	frame = cv2.undistort(frame, cam_mtx, dist, None, newcam_mtx)
	frame = cv2.warpPerspective(frame, h_mat, (frame.shape[1], frame.shape[0]))

	output = frame.copy()
	frame = cv2.medianBlur(frame, 5)
	hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
	
	mask = cv2.inRange(hsv, lower_hue, upper_hue)

	# Reduce noise in mask
	kernel = np.ones((3,3),np.uint8)
	erosion = cv2.erode(mask, kernel, iterations = 2)
	dilation = cv2.dilate(erosion,kernel,iterations = 2)
	blur = cv2.GaussianBlur(mask,(5,5),0)

	res = cv2.bitwise_and(frame,frame, mask= mask)
	
	contours,_= cv2.findContours(blur, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

	for cnt in contours:
		approx = cv2.approxPolyDP(cnt, 0.01*cv2.arcLength(cnt, True), True)
		if cv2.contourArea(cnt) > 200:
			x, y, w, h = cv2.boundingRect(approx)
			x = x + w/2
			y = y + h/2
			pt = calculate_position(x,y)
			x = np.round(x).astype("int")
			y = np.round(y).astype("int")
			cv2.rectangle(output, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
			cv2.putText(output,str(truncate(pt[0],2)) +", " +str(truncate(pt[1], 2)),(x+10,y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 0,255),2)

	if cv2.waitKey(1) & 0xFF == ord('q'):
		cam.release()
		break

	# show the output image
	cv2.imshow("output", output)
	cv2.imshow("video", np.hstack([frame, res]))
	cv2.waitKey(200)
