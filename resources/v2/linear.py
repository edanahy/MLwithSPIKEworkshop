# Supervised Classification via Linear Regression

# Necessary Module Imports
from hub import button, port, sound
import motor
import distance_sensor
import runloop

# Calculate slope and intercept for linear regression
def calculate_linear_regression(x, y, n):
	sum_x = sum(x)
	sum_y = sum(y)
	sum_xy = sum([xi*yi for xi, yi in zip(x, y)])
	sum_xx = sum([xi**2 for xi in x])
	
	m = (n * sum_xy - sum_x * sum_y) / (n * sum_xx - sum_x**2)
	c = (sum_y - m * sum_x) / n
	
	return m, c

# Data Collection
async def collect_data(distances, speeds):
	# confirm taking data
	print('Collect Data')
	sound.beep(440, 250, 100)

	# Get Distance Measurement
	distance = distance_sensor.distance(port.B)

	# Get Speed Measurement
	speed = motor.absolute_position(port.E)

	# Store Data
	distances.append(distance)
	speeds.append(speed)
	
	print('New Data:')
	print('- Distances:', distances)
	print('- Speeds:', speeds)

	# Wait to Prevent Double Readings
	await runloop.sleep_ms(750)
	print('** Ready for next datapoint')

	return distances, speeds

# Controller
async def proportional_control(distances, speeds):
	# confirm running code
	sound.beep(880, 250, 100)
	if (len(distances) < 2 or len(speeds) < 2):
		print('ERROR: need more data')
		return
	print('Calculating')
	# pause to prevent double readings
	await runloop.sleep_ms(750)

	# calculate coefficients for line of best fit
	m, c = calculate_linear_regression(distances, speeds, len(distances))
	print('- m:', m, ', c:', c)

	print('Proportional Control Started')    
	print('- Press Right Button to Stop')        
	while (not button.pressed(button.RIGHT)):
		# read distance and calculate output
		distance = distance_sensor.distance(port.B)
		new_val = m * distance + c
		# scale up from angle to motor speed
		new_speed = int(new_val * 3)
		# set motor speed
		motor.run(port.A, new_speed)
		await runloop.sleep_ms(50)
		# loop back and calculate next value
		
	# done running; pause
	sound.beep(220, 250, 100)
	print('Proportional Control Stopped')            
	motor.stop(port.A)
	await runloop.sleep_ms(250)
	print('Return to Main Loop')

# Main Task: monitor buttons for functions
async def main():
	# Variables to store data
	distances = []
	speeds = []
	# Be sure stopped
	motor.stop(port.A)
	print('')
	print('Linear Regression:')
	print('- left button to add data')
	print('- right button to run model')
	while True:
		if button.pressed(button.LEFT):
			print('Button Left Pushed')
			distances, speeds = await collect_data(distances, speeds)
			print('- left button to add data')
			print('- right button to run model')
		elif button.pressed(button.RIGHT):
			print('Button Right Pushed')
			await proportional_control(distances, speeds)
			# reset data
			distances = []
			speeds = []
			print('Data Reset')
			print('- left button to add data')
			print('- right button to run model')
		await runloop.sleep_ms(100)

# Run the Main Task
runloop.run(main())

