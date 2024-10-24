# Fruit Scanner Nearest Neighbor Classification

#######
# First developed during the summer of 2024 by CEEO Interns
# Modified and adapted for ML workshop October 21, 2024
#######
# PORTS
#   MOTOR in Port B
#   COLOR SENSOR in Port D
#   FORCE SENSOR in Port F
#######

from hub import sound, port, button, light_matrix
from color_sensor import rgbi
import force_sensor
from runloop import run, sleep_ms, until
import runloop
from time import sleep
import motor 
import math

train_data = []
motor_pos = 0

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

light_matrix.show_image(light_matrix.IMAGE_DIAMOND)

async def main():
	print ('Welcome to Fruit Scanner!')
	print ('Move motor dial to the colored brick representing the Banana (left) or Apple (right)')
	print ('Hold fruit over the color sensor and press the force sensor to train')
	print ('Train multiple points for each fruit')
	print ('Press the right button when you are ready to test your scanner')
	
    while True:
    	if force_sensor.pressed(port.F):
    	    print('FORCE PRESSED')
    		if (motor.absolute_position(port.B) > 0):
    			motor_pos = motor.absolute_position(port.B)
    			train_data.append((rgbi(port.D), 1, motor_pos))
    			sound.beep(440, 500, 100)
    			print(train_data)
    			print("apple")
    			print(motor_pos)
    			light_matrix.show_image(light_matrix.IMAGE_ARROW_E)
    			sleep(2)
    			light_matrix.show_image(light_matrix.IMAGE_DIAMOND)
    		if (motor.absolute_position(port.B) < 0):
    			motor_pos = motor.absolute_position(port.B)
    			train_data.append((rgbi(port.D), 0, motor_pos))
    			sound.beep(440, 500, 100)
    			print(train_data)
    			print("banana")
    			print(motor_pos)
    			light_matrix.show_image(light_matrix.IMAGE_ARROW_W)
    			sleep(2)
    			light_matrix.show_image(light_matrix.IMAGE_DIAMOND)
    	if button.pressed(button.RIGHT):
    		print("RIGHT BUTTON WAS PRESSED")
    		sound.beep(800, 500, 100)
    		light_matrix.show_image(light_matrix.IMAGE_TRIANGLE)
    		while button.pressed(button.LEFT) == False:
    			if force_sensor.pressed(port.F):
    				i = nearest_neighbor()
    				if train_data[i][1] == 0:
    					sleep(0.1)
    					sound.beep(800, 50, 100)
    					motor.run_to_absolute_position(port.B, train_data[i][2], 800)
    					light_matrix.write("Banana")
    					sleep(1)
    				if train_data[i][1] == 1:
    					sleep(0.1)
    					sound.beep(800, 50, 100)
    					motor.run_to_absolute_position(port.B, train_data[i][2], 800)
    					light_matrix.write("Apple")
    					sleep(1)
        await sleep_ms(50)

runloop.run(main())
