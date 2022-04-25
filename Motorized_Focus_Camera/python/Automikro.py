import cv2# import the necessary packages
from picamera.array import PiRGBArray
import numpy as py
from picamera import PiCamera
import time
import os
from ctypes import *
arducam_vcm= CDLL('./lib/libarducam_vcm.so')
try:
	import picamera
	from picamera.array import PiRGBArray
except:
	sys.exit(0)
	
def focusing(val):
        arducam_vcm.vcm_write(val)
        #print("focus value: {}".format(val))
	
def sobel(img):
	img_gray = cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)
	img_sobel = cv2.Sobel(img_gray,cv2.CV_16U,1,1)
	return cv2.mean(img_sobel)[0]

def laplacian(img):
	img_gray = cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)
	img_sobel = cv2.Laplacian(img_gray,cv2.CV_16U)
	return cv2.mean(img_sobel)[0]
	

def calculation(camera,x1,y1,x2,y2):
	rawCapture = PiRGBArray(camera) 
	camera.capture(rawCapture,format="bgr", use_video_port=True)
	image = rawCapture.array
	roi=image[x1:y2,y1:y2]
	cv2.rectangle(image, (x1, y1), (x2, y2), (255,0,0), 2)
	cv2.imshow("Frame", image)
	key = cv2.waitKey(1) & 0xFF
	rawCapture.truncate(0)
	return laplacian(roi)
	


# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
if __name__ == "__main__":
    #vcm init
    arducam_vcm.vcm_init()
camera.resolution = (800, 600)
camera.framerate = 20


max_index = 10
max_value = 0.0
last_value = 0.0
dec_count = 0
focal_distance = 10


        

while True:
	    #Adjust focus
		focusing(focal_distance)
		#Take image and calculate image clarity
		val = calculation(camera,312,284,512,484)
		#Find the maximum image clarity
		if val > max_value:
			max_index = focal_distance
			max_value = val
			
		#If the image clarity starts to decrease
		if val < last_value:
			dec_count += 1
		else:
			dec_count = 0
		#Image clarity is reduced by six consecutive frames
		if dec_count > 6:
			break
		last_value = val
		
		#Increase the focal distance
		focal_distance += 5
		if focal_distance > 1000:
			break

    #Adjust focus to the best
focusing(max_index)
camera.stop_preview()
camera.annotate_text=False
camera.resolution = (1920, 1080)


print("max index = %d,max value = %lf" % (max_index,max_value))
rawCapture = PiRGBArray(camera, size=(1920, 1080))
# allow the camera to warmup
time.sleep(0.1)
# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
	# grab the raw NumPy array representing the image, then initialize the timestamp
	# and occupied/unoccupied text
	image = frame.array
	# show the frame
	cv2.imshow("Frame", image)
	key = cv2.waitKey(1) & 0xFF
	# clear the stream in preparation for the next frame
	rawCapture.truncate(0)
	# if the `q` key was pressed, break from the loop
	if key == ord("q"):
		break