import cv2 #sudo apt-get install python-opencv
import numpy as py
from picamera import PiCamera
import os
import time
from ctypes import *
#load arducam shared object file
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
	

def calculation(camera):
	rawCapture = PiRGBArray(camera) 
	camera.capture(rawCapture,format="bgr", use_video_port=True)
	image = rawCapture.array
	rawCapture.truncate(0)
	return laplacian(image)
	
	
if __name__ == "__main__":
    #vcm init
        arducam_vcm.vcm_init()
    #open camera
	camera = PiCamera()
	
        #open camera preview
	camera.start_preview()
	#set camera resolution to 640x480(Small resolution for faster speeds.)
	camera.resolution = (800, 600)
	camera.annotate_text='ostrzenie'
	
       
        time.sleep(0.1)
        camera.shutter_speed=30000
	print("Start focusing")
	
	max_index = 10
	max_value = 0.0
	last_value = 0.0
	dec_count = 0
	focal_distance = 10


        

	while True:
	    #Adjust focus
		focusing(focal_distance)
		#Take image and calculate image clarity
		val = calculation(camera)
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
	time.sleep(1)
	#set camera resolution to 2592x1944
	camera.resolution = (1920,1080)
	#save image to file.
	camera.capture("test.jpg")
	print("max index = %d,max value = %lf" % (max_index,max_value))
	#while True:
	time.sleep(1)
		
camera.resolution = (800, 600)
camera.framerate = 32
rawCapture2 = PiRGBArray(camera, size=(800, 600))
rawCapture2.truncate(0)
# allow the camera to warmup
time.sleep(0.1)
# capture frames from the camera
for frame2 in camera.capture_continuous(rawCapture2, format="bgr", use_video_port=True):
	# grab the raw NumPy array representing the image, then initialize the timestamp
	# and occupied/unoccupied text
	image2 = frame2.array
	# show the frame
	cv2.imshow("Frame", image2)
	key = cv2.waitKey(1) & 0xFF
	# clear the stream in preparation for the next frame
	rawCapture2.truncate(0)
	# if the `q` key was pressed, break from the loop
	if key == ord("q"):
		break	
        camera.close()
		
	
