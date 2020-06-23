import cv2
import numpy as np

cam = cv2.VideoCapture(0)

while(cam.isOpened()):
	_, frame = cam.read()
	cv2.imshow('cam', frame)
	cv2.waitKey(100)
