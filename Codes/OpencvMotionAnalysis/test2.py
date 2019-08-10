# USAGE
# python ball_tracking.py --video ball_tracking_example.mp4

# import the necessary packages
from collections import deque
from imutils.video import VideoStream
import numpy as np
import argparse
import cv2
import imutils
import time

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
	help="/ball_tracking_example.mp4")
ap.add_argument("-b", "--buffer", type=int, default=64,
	help="max buffer size")
args = vars(ap.parse_args())


# define the lower and upper boundaries of the colored markers for linear and rotational
rotational_Lower = (35, 43, 46)
rotational_Upper = (77, 255, 255)
rotational_Pts = deque(maxlen=args["buffer"])

linear_Lower = (0, 175, 197)
linear_Upper = (19, 218, 300)
linear_Pts = deque(maxlen=args["buffer"])

# if a video path was not supplied, grab the reference
# to the webcam
if not args.get("video", False):
	vs = VideoStream(src=0).start()

# otherwise, grab a reference to the video file
else:
	vs = cv2.VideoCapture(args["video"])

# allow the camera or video file to warm up
time.sleep(2.0)

rotational_StartCounter = True
rotational_iPositionX = 0
rotational_iPositionY = 0
rotational_startTime = 0
angularSpeed = 0;
rotational_linear_Offset=0;
distance=0;
distance_traveledRound=0;
previous_x=0
current_x=0
previous_y=0
current_y=0

linear_StartCounter = 0
linear_startPosition = 0
linear_startTime = 0

# keep looping
while True:
	# grab the current frame
	frame = vs.read()
	frame = frame[1] if args.get("video", False) else frame

	# if we are viewing a video and we did not grab a frame,
	# then we have reached the end of the video
	if frame is None:
		break
	

	# resize the frame, blur it, and convert it to the HSV
	# color space
	frame = imutils.resize(frame, width=600)
	blurred = cv2.GaussianBlur(frame, (11, 11), 0)
	hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

	# construct a rotational_Mask for the color "green", then perform
	# a series of dilations and erosions to remove any small
	# blobs left in the rotational_Mask
	rotational_Mask = cv2.inRange(hsv, rotational_Lower, rotational_Upper)
	rotational_Mask = cv2.erode(rotational_Mask, None, iterations=2)
	rotational_Mask = cv2.dilate(rotational_Mask, None, iterations=2)

	linear_mask = cv2.inRange(hsv, linear_Lower, linear_Upper)
	linear_mask = cv2.erode(linear_mask, None, iterations=2)
	linear_mask = cv2.dilate(linear_mask, None, iterations=2)
	
	# find contours in the linear_mask and rotational_Mask and initialize the current
	# (x, y) rotational_center of the ball
	rotational_Cnts = cv2.findContours(rotational_Mask.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)
	rotational_Cnts = imutils.grab_contours(rotational_Cnts)
	rotational_center = None
	
	linear_cnts = cv2.findContours(linear_mask.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)
	linear_cnts = imutils.grab_contours(linear_cnts)
	linear_center = None
	

	# linear motion capture
	if len(linear_cnts) > 0:
		# find the largest contour in the linear_mask, then use
		# it to compute the minimum enclosing circle and
		# centroid
		linear_c = max(linear_cnts, key=cv2.contourArea)
		((linear_x, linear_y), linear_radius) = cv2.minEnclosingCircle(linear_c)
		linear_M = cv2.moments(linear_c)
		linear_center = (int(linear_M["m10"] / linear_M["m00"]), int(linear_M["m01"] / linear_M["m00"]))
		
		if linear_StartCounter==0:
			linear_StartCounter+=1
			linear_startPosition=int(linear_x)
			linear_startTime = vs.get(cv2.CAP_PROP_POS_MSEC)
			print(linear_startPosition)

		if int(linear_startPosition)!=int(linear_x):
			f = open('test.txt','a')
			#print(vs.get(cv2.CAP_PROP_POS_MSEC))
			distance = linear_startPosition-int(linear_x)
			current_x=linear_x-linear_startPosition
			timeUsed = vs.get(cv2.CAP_PROP_POS_MSEC) - linear_startTime
			speed = int((distance/timeUsed)*(0.219*1000)*100000)/100000
			print(distance)
			f.write(str(speed)+" "+str(timeUsed)+"\n")
			f.close()
			cv2.putText(frame, str(speed) + " cm/s", (int(linear_x), int(linear_y)+20),cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1)


		# only proceed if the linear_radius meets a minimum size
		if linear_radius > 10:
			# draw the circle and centroid on the frame,
			# then update the list of tracked points
			cv2.circle(frame, (int(linear_x), int(linear_y)), int(linear_radius),
				(0, 255, 255), 2)
			cv2.circle(frame, linear_center, 5, (0, 0, 255), -1)

	# update the points queue
	linear_Pts.appendleft(linear_center)

	# loop over the set of tracked points
	for i in range(1, len(linear_Pts)):
		# if either of the tracked points are None, ignore
		# them
		if linear_Pts[i - 1] is None or linear_Pts[i] is None:
			continue

		# otherwise, compute the thickness of the line and
		# draw the connecting lines
		thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
		cv2.line(frame, linear_Pts[i - 1], linear_Pts[i], (0, 0, 255), thickness)


	# rotational motion capture
	if len(rotational_Cnts) > 0:
		# find the largest contour in the rotational_Mask, then use
		# it to compute the minimum enclosing circle and
		# centroid
		c = max(rotational_Cnts, key=cv2.contourArea)
		((rotational_x, rotational_y), rotational_Radius) = cv2.minEnclosingCircle(c)
		M = cv2.moments(c)
		rotational_center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
		print("x,y")
		print(rotational_x)
		print(rotational_y);
		

		if rotational_StartCounter==True and vs.get(cv2.CAP_PROP_POS_MSEC)>250:
			rotational_StartCounter=False
			rotational_iPositionX=int(rotational_x)
			rotational_linear_Offset=rotational_x-linear_startPosition
			rotational_iPositionY=int(rotational_y)
			rotational_startTime = vs.get(cv2.CAP_PROP_POS_MSEC)
			print("x,y, and time")
			print(rotational_iPositionX)
			print(rotational_iPositionY)
			print(rotational_startTime)
			previous_x=current_x
		
		distance_x=abs(current_x-previous_x)
		distance_y=0;
		if abs(rotational_iPositionY-rotational_y)<3.5 and abs(rotational_x-rotational_iPositionX+distance_x)<5 and vs.get(cv2.CAP_PROP_POS_MSEC)>200+rotational_startTime:
			rotational_iPositionX=rotational_x
			rotational_iPositionY=rotational_y
			reachTime = vs.get(cv2.CAP_PROP_POS_MSEC)
			timePerRevolution = reachTime - rotational_startTime
			timePerRevolution = timePerRevolution/1000
			angularSpeed = int((6.2831/timePerRevolution)*1000)/1000
			rotational_startTime=vs.get(cv2.CAP_PROP_POS_MSEC)
			previous_x=current_x;
			print("angularSpeed")
			print(angularSpeed)

		
		# only proceed if the rotational_Radius meets a minimum size
		if rotational_Radius > 10:
			# draw the circle and centroid on the frame,
			# then update the list of tracked points
			cv2.circle(frame, (int(rotational_x), int(rotational_y)), int(rotational_Radius),
				(0, 255, 255), 2)
			cv2.circle(frame, rotational_center, 5, (0, 0, 255), -1)
	cv2.putText(frame, str(angularSpeed) + " rad/s", (308, 256),cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 32, 255), 1)
	# update the points queue
	rotational_Pts.appendleft(rotational_center)
	

	# loop over the set of tracked points
	for i in range(1, len(rotational_Pts)):
		# if either of the tracked points are None, ignore
		# them
		if rotational_Pts[i - 1] is None or rotational_Pts[i] is None:
			continue

		# otherwise, compute the thickness of the line and
		# draw the connecting lines
		thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
		cv2.line(frame, rotational_Pts[i - 1], rotational_Pts[i], (0, 0, 255), thickness)

	# show the frame to our screen
	cv2.imshow("Frame", frame)
	key = cv2.waitKey(1) & 0xFF

	# if the 'q' key is pressed, stop the loop
	if key == ord("q"):
		break

# if we are not using a video file, stop the camera video stream
if not args.get("video", False):
	vs.stop()

# otherwise, release the camera
else:
	vs.release()

# close all windows
cv2.destroyAllWindows()


