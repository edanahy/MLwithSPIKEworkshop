# Fruit Scanner Nearest Neighbor Classification

#######
# October 17, 2024; Prep for LEGO workshop; test
# Notice --> you can train on yellow via RGB values and see the resulting "prediction" when running the ML model even though the LEGO software does not "predict" yellow (it may not have a color or predict a different color)
# In other words, a well trained nearest neighbor algorithm is an improvement over the fixed algorithm provided within the API for color detection
######
# TO DO:
# 1) Switch out force sensor for left hub button
# 2) Provide text instructions for the UI in the console
# 3) instead of 90 and -90 do 45 and -45 so the motor moves to the absolute positions via shortest distance on one side of the motor's hub circle
# 4) Add a third fruit
# 5) add console messages that go with the prediction so you can line up motor position with fruit prediction
#########

from hub import sound, port, button
from color_sensor import rgbi
import force_sensor
from runloop import run, sleep_ms, until
from time import sleep
import motor 
import math

train_data = []

def distance(RGB, rgb2):
	return math.sqrt(((RGB[0] - rgb2[0])**2) + ((RGB[1] - rgb2[1])**2) + ((RGB[2] - rgb2[2])**2)) 

def nearest_neighbor():
	RGB = rgbi(port.D)
	min = 999
	min_idx = 0
	for i in range(1,len(train_data)):
		
		dist = distance(RGB, train_data[i][0])
		if dist <= min:
			min = dist
			min_idx = i
	return min_idx

while True: 
	
	#
	if force_sensor.pressed(port.F):
		if (motor.absolute_position(port.B) > 0):
			train_data.append((rgbi(port.D), 1))
			sound.beep(440, 500, 100)
			print(train_data)
			print("apple")
			print(motor.absolute_position(port.B))
			sleep(3)
		if (motor.absolute_position(port.B) < 0):
			train_data.append((rgbi(port.D), 0))
			sound.beep(440, 500, 100)
			print(train_data)
			print("banana")
			print(motor.absolute_position(port.B))
			sleep(3)

	if button.pressed(button.RIGHT):
		print("RIGHT BUTTON WAS PRESSED")
		sound.beep(800, 500, 100)
		while button.pressed(button.LEFT) == False:
			if force_sensor.pressed(port.F):
				i = nearest_neighbor()
				if train_data[i][1] == 0:
					sleep(0.1)
					sound.beep(800, 50, 100)
					motor.run_to_absolute_position(port.B, -90, 800)
					sleep(2)
				if train_data[i][1] == 1:
					sleep(0.1)
					sound.beep(800, 50, 100)
					motor.run_to_absolute_position(port.B, 90, 800)
					sleep(2)
