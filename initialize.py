import numpy as np
import cv2
import glob

savedir="Camera_Data/"

ChessX = 7
ChessY = 4

#Calculate and return homography matrix
def Cal_hom(frame):

	print("Calibrating Camera...")

	ref = cv2.imread("calb_ll.jpg")

	ret1, corners1 = cv2.findChessboardCorners(ref, (ChessY, ChessX), None)
	ret2, corners2 = cv2.findChessboardCorners(frame, (ChessY, ChessX), None)

	if ret2 == True:
		print("Corners Positive")
		h_mat, status = cv2.findHomography(corners2, corners1)
		ref = cv2.drawChessboardCorners(ref, (ChessY, ChessX), corners1,ret1)
		frame = cv2.drawChessboardCorners(frame, (ChessY, ChessX), corners2,ret2)
		cv2.imshow('result', frame)
		cv2.waitKey(0)
		cv2.destroyWindow('result')
		return h_mat
	else:
		print("Chessboard not found")

# Calculate Pixel per millimeters
def Cal_mils(frame):
	ret, corners = cv2.findChessboardCorners(frame, (ChessY, ChessX), None)
	print(corners)
	sumX = 0
	sumY = 0
	if ret == True:
		print("Calculating")
		for i in range(0, ChessY*(ChessX-1)):
			if((i+1)%ChessY != 0):
				frame = cv2.line(frame, tuple(corners[i+1][0]), tuple(corners[i][0]), (255, 0, 0), 3)
				sumY += (corners[i][0][1]-corners[i+1][0][1])
				cv2.waitKey(200)
				frame = cv2.line(frame, tuple(corners[i][0]), tuple(corners[i+ChessY][0]), (255, 0, 255), 3)
				sumX += (corners[i+ChessY][0][0] - corners[i][0][0])
				cv2.imshow("CapFrame", frame)
				cv2.waitKey(200)
		cv2.destroyWindow("CapFrame")
		return sumX/(9*(ChessY-1)*(ChessX-1)), sumY/(9*(ChessY-1)*(ChessX-1))


# Camera Calibration

def Calibrate():

	criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
	# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
	objp = np.zeros((7*4,3), np.float32)

	#add 2.5 to account for 2.5 cm per square in grid
	objp[:,:2] = np.mgrid[0:7,0:4].T.reshape(-1,2)*2.5

	# Arrays to store object points and image points from all the images.
	objpoints = [] # 3d point in real world space
	imgpoints = [] # 2d points in image plane.
	images = glob.glob('Calibration_Images/Cam1/*.jpg')

	win_name="Verify"
	cv2.namedWindow(win_name, cv2.WND_PROP_FULLSCREEN)
	cv2.setWindowProperty(win_name,cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)

	print("getting images")

	for fname in images:
		img = cv2.imread(fname)
		print(fname)
		gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


		# Find the chess board corners
		ret, corners = cv2.findChessboardCorners(gray, (7,4), None)

		# If found, add object points, image points (after refining them)
		if ret == True:
			objpoints.append(objp)
			corners2=cv2.cornerSubPix(gray,corners, (11,11), (-1,-1), criteria)
			imgpoints.append(corners)
			# Draw and display the corners
			cv2.drawChessboardCorners(img, (7,4), corners2, ret)
			cv2.imshow(win_name, img)
			cv2.waitKey(500)
		
	cv2.destroyAllWindows()

	print(">==> Starting calibration")
	ret, cam_mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

	return ret, cam_mtx, dist, rvecs, tvecs, img


#Main
k = input("Calibration required ? y/n :")
if k == 'y':
	ret, cam_mtx, dist, rvecs, tvecs, img = Calibrate()

	# Save the camera Matrix
	print("Camera Matrix")
	print(cam_mtx)
	np.save(savedir+'cam_mtx.npy', cam_mtx)

	# Save the distortion coeff
	print("Distortion Coeff")
	print(dist)
	np.save(savedir+'dist.npy', dist)

	print("r vecs")
	print(rvecs[2])

	print("t Vecs")
	print(tvecs[2])



	print(">==> Calibration ended")


	h,  w = img.shape[:2]
	print("Image Width, Height")
	print(w, h)


	newcam_mtx, roi = cv2.getOptimalNewCameraMatrix(cam_mtx, dist, (w,h), 1, (w,h))

	print("Region of Interest")
	print(roi)
	np.save(savedir+'roi.npy', roi)

	print("New Camera Matrix")
	#print(newcam_mtx)
	np.save(savedir+'newcam_mtx.npy', newcam_mtx)
	print(np.load(savedir+'newcam_mtx.npy'))

	inverse = np.linalg.inv(newcam_mtx)
	print("Inverse New Camera Matrix")
	print(inverse)

else:
	cam_mtx=np.load(savedir+'cam_mtx.npy')
	dist=np.load(savedir+'dist.npy')
	newcam_mtx=np.load(savedir+'newcam_mtx.npy')

# ~ cam = cv2.VideoCapture(0)
cam_address = input("Camera Address : ")
cam = cv2.VideoCapture('http://'+cam_address+':8080/mjpegfeed?640x480')
# Main Loop
while(cam.isOpened()):

	ret, frame = cam.read()
	# undistort
	frame = cv2.undistort(frame, cam_mtx, dist, None, newcam_mtx)

	# Calculation
	if cv2.waitKey(1) & 0xFF == ord('c'):
		try:
			h_mat = Cal_hom(frame)
			print("Homography Matrix Found")
			print(h_mat)
			np.save(savedir+'h_mtx.npy', h_mat)
			cv2.destroyWindow("Camera")
			break
		except:
			print("Calibration Failed")
			continue
	cv2.imshow("Camera", frame)

while(True):
	ret, frame = cam.read()
	frame = cv2.undistort(frame, cam_mtx, dist, None, newcam_mtx)
	cal_frame = cv2.warpPerspective(frame, h_mat, (frame.shape[1], frame.shape[0]))
	cv2.imshow("Warped", cal_frame)
	if cv2.waitKey(1) & 0xFF == ord('c'):
		try:
			a, b = Cal_mils(cal_frame)
			ratio = np.array([a,b])
			print("Pixels per millimeter")
			print(ratio)
			np.save(savedir+'ratio.npy', ratio)
			break
		except:
			print("Calculation Failed")
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break


cam.release()
cv2.destroyAllWindows()
