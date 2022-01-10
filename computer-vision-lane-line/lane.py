#!/usr/bin/env python
#from picamera import PiCamera
import cv2
import numpy as np
from matplotlib import pyplot as plt
import math
import Servo
import Motor
import time
import logging


def detect_edges(frame):
	hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
	#cv2.imwrite('hsvcolor.jpg', hsv)
	lower_blue = np.array([90, 60, 60])
	upper_blue = np.array([150, 255, 255])
	mask = cv2.inRange(hsv, lower_blue, upper_blue)
	#cv2.imwrite('makse.jpg', mask)
	edges = cv2.Canny(mask, 200, 400)
	return edges

def region_of_interest(edges):
	height, width = edges.shape
	mask = np.zeros_like(edges)
	polygon = np.array([[
		(0, height),
		(width, height),
		(width, height/2),
		(0, height/2),
		]], np.int32)
	cv2.fillPoly(mask, polygon, 255)
	cropped_edges = cv2.bitwise_and(edges, mask)
	return cropped_edges

def detect_line_segments(cropped_edges):
	rho = 1 #distance precision in pixel
	angle = np.pi / 180 #angular precision in radians
	min_threshold = 10 #minimum number of votes to consider a line
	minLineLength = 8 #minimum length of line segment in pixels
	maxLineGap = 4 #maximum gap between each line.
	line_segments = cv2.HoughLinesP(cropped_edges, rho, angle,
									min_threshold, np.array([ ]),
									 minLineLength, maxLineGap)
	return line_segments


'''def create_coordinates(image, line_parameters):
	slope, intercept = line_parameters
	y1 = image.shape[0]
	y2 = int(y1 * (1 / 2))
	x1 = int((y1 - intercept) / slope)
	x2 = int((y2 - intercept) / slope)
	return np.array([x1, y1, x2, y2])'''

def create_coordinates(frame, line):
	try:
		slope, intercept = line
	except TypeError:
		slope, intercept = 0.001, 0
	#slope, intercept = line_parameters
	y1 = frame.shape[0]
	y2 = int(y1 * (3 / 5))
	x1 = int((y1 - intercept) / slope)
	x2 = int((y2 - intercept) / slope)
	return np.array([x1, y1, x2, y2])

def average_slope_intercept(image, lines):
	lane_lines = []
	if lines is None:
		logging.info('No line_segment segments detected')
		return lane_lines

	height, width, _ = image.shape
	left_fit = []
	right_fit = []

	boundary = 1 / 3
	left_region_boundary = width * (1 - boundary)
	right_region_boundary = width * boundary

	for line in lines:
		x1, y1, x2, y2 = line.reshape(4)
		fit = np.polyfit((x1, x2), (y1, y2), 1)
		slope = fit[0]
		intercept = fit[1]
		if slope < 0:
			left_fit.append((slope, intercept))
		else:
			right_fit.append((slope, intercept))

		#print(sum(list(right_fit)))

		#print(left_fit)
		#print(sum(list(left_fit)))
		if len(right_fit) == 0:
			right_line = [0, 0, 0, 0]
		else:
			right_fit_average = np.average(right_fit, axis = 0)
			right_line = create_coordinates(image, right_fit_average)
		if len(left_fit) == 0:
			left_line = [0,0,0,0]
		else:
			left_fit_average = np.average(left_fit, axis = 0)
			left_line = create_coordinates(image, left_fit_average)
		lane_lines = np.array([left_line, right_line])

		#draw_lines = np.array([left_line, right_line])
		#print(draw_lines)

	return lane_lines

#image = cv2.imread('bluelane.jpg')
#lane_lines = detect_lane(image)

def display_lines(image, lines):
	line_image = np.zeros_like(image)
	for x1, y1, x2, y2 in lines:
		cv2.line(line_image, (x1, y1), (x2, y2), (0, 255, 0), 10)
	return line_image

#line_image = display_lines(image, lane_lines)
#combo_image = cv2.addWeighted(image, 0.8, line_image, 1, 1)

#cv2.imshow("results.jpg", combo_image)

def get_steering_angle(frame, lane_lines):
	height, width, _ = frame.shape

	if np.all(lane_lines[0]) == False:
		x1, _, x2, _ = lane_lines[1]
		x_offset = (x2 - x1)
		y_offset = int(height / 2)

	elif np.all(lane_lines[1]) == False:
		x1, _, x2, _ = lane_lines[0][0]
		x_offset = x2 - x1
		y_offset = int(height / 2)

	elif np.all(lane_lines[0]) == False and np.all(lane_lines[1]) == False:
		x_offset = 0
		y_offset = int(height / 2)

	else:
		left_x2 = lane_lines[0][0]
		right_x2 = lane_lines[1][0]

		mid = int(width / 2)
		x_offset = (left_x2 + right_x2) / 2 - mid
		y_offset = int(height / 2)

	angle_to_mid_radian = math.atan(x_offset / y_offset)
	angle_to_mid_deg = int(angle_to_mid_radian * 180.0 / math.pi)
	steering_angle = angle_to_mid_deg + 90
	return steering_angle

def stabilize_steering_angle(curr_steering_angle, new_steering_angle, 
	lane_lines, max_angle_deviation_two_lines=5, max_angle_deviation_one_lane=1):

	if np.all(lane_lines[0]) == False:
		# if both lane lines detected, then we can deviate more
		max_angle_deviation = max_angle_deviation_one_lines
	elif np.all(lane_lines[1]) == False:
		# if both lane lines detected, then we can deviate more
		max_angle_deviation = max_angle_deviation_one_lines
	else :
		# if only one lane detected, don't deviate too much
		max_angle_deviation = max_angle_deviation_two_lane
	
	angle_deviation = new_steering_angle - curr_steering_angle
	if abs(angle_deviation) > max_angle_deviation:
		stabilized_steering_angle = int(curr_steering_angle
										+ max_angle_deviation * angle_deviation / abs(angle_deviation))
	else:
		stabilized_steering_angle = new_steering_angle
	return stabilized_steering_angle


#steering_angle = get_steering_angle(image, lane_lines)

def display_heading_line(frame, steering_angle):
	# print(frame.shape)
	line_color = (0, 0, 255)
	line_width = 2
	heading_image = np.zeros_like(frame)
	height, width, _ = frame.shape

	steering_angle_radian = steering_angle / 180 * math.pi
	x1 = int(width / 2)
	y1 = height
	x2 = int(x1 - height / 2 / math.tan(steering_angle_radian))
	y2 = int(height / 2)

	cv2.line(heading_image, (x1, y1), (x2, y2), line_color, line_width)
	heading_image = cv2.addWeighted(frame, 0.8, heading_image, 1, 1)
	return heading_image

def detect_lane(frame):
	#image = cv2.imread('bluelane.jpg')
	edges = detect_edges(image)
	crop = region_of_interest(edges)
	cv2.imwrite('ecrop.jpg', crop)
	line_segments = detect_line_segments(crop)
	lane_lines = average_slope_intercept(image, line_segments)
	print(lane_lines)
	line_image = display_lines(image, lane_lines)
	combo_image = cv2.addWeighted(image, 0.8, line_image, 1, 1)
	steering_angle = get_steering_angle(image, lane_lines)
	print(steering_angle)
	heading_image = display_heading_line(combo_image, steering_angle)
	cv2.imwrite("steering3.jpg", heading_image)
	cv2.waitKey(0)
	cv2.destroyAllWindows()
	#print(lane_lines)

def steer(steering_angle):
	if 45 <= steering_angle <= 135:
		steer = steering_angle
	return steer

def final():
	cap = cv2.VideoCapture(0)
	last_recorded_time = time.time()
	PWM = Motor.Motor()
	PWS = Servo.Servo()

	while(cap.isOpened()):
		try:
			print('camera on and wait 1 second')
			time.sleep(1)

			curr_time = time.time()

			_, image = cap.read()
			cv2.rotate(image, cv2.ROTATE_180)

			if curr_time - last_recorded_time >= 0.4:
				edges = detect_edges(image)
				crop = region_of_interest(edges)
				line_segments = detect_line_segments(crop)
				lane_lines = average_slope_intercept(image, line_segments)
				steering_angle = get_steering_angle(image, lane_lines)
				if 45 <= steering_angle <= 135:

					print(steer)
					PWS.setServoPwm('4', steering_angle)
					PWM.setMotorModel(30, 30)

				last_recorded_time = curr_time

			
		except KeyboardInterrupt:
			PWM.setMotorModel(0, 0)
			PWS.setServoPwm('4', 90)
	
	cap.release()

	cv2.destroyAllWindows()
	

if __name__ == '__main__':

	#image = cv2.imread('newlane.jpg')
	#detect_lane(image)
	cap = cv2.VideoCapture(0)
	PWM = Motor.Motor()
	PWS = Servo.Servo()
	curr_steering_angle = 90

	while(cap.isOpened()):
		print('camera on')
		try:			
			_, image = cap.read()
			cv2.rotate(image, cv2.ROTATE_180)
			
			
			edges = detect_edges(image)
			crop = region_of_interest(edges)
			line_segments = detect_line_segments(crop)
			lane_lines = average_slope_intercept(image, line_segments)
			new_steering_angle = get_steering_angle(image, lane_lines)
			for steering_angle in new_steering_angle:
				angle_deviation = steering_angle - curr_steering_angle
				if abs(angle_deviation) > 2:
					stabilized_steering_angle = int(curr_steering_angle
									+ 1 * angle_deviation / abs(angle_deviation))
				else:
					stabilized_steering_angle = steering_angle
			
			print(stabilized_steering_angle)
			PWS.setServoPwm('4', stabilized_steering_angle)
			#PWM.setMotorModel(50, 40)
			
					
						
		except KeyboardInterrupt:
			print("program interrupted")
			PWM.setMotorModel(0, 0)
			PWS.setServoPwm('4', 90)
				
	cap.release()
			
	cv2.destroyAllWindows()

'''if __name__ == '__main__':

	image = cv2.imread('tester4.jpg')
	detect_lane(image)'''
			
				
















