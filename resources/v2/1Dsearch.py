# 1D Search via Q-Learning

########
# 1 Dim RL based on Tanushree's code for linear forward and backward
# Code adapted by Bill and CodeRobots.ai (chatGPT)
# For workshop TO DO:
# 1) Add a pleasing tune when the arm swings over Green
# 2) Fix the UI for better overall flow
# 3) Write bullet points for how to use the system and what to look out as the system "learns" the path to the Green brick.  IE --> the reward history and the timesteps history
# 4) Review Tanushree's code an pick-out tinkerable variables....
#########

from hub import port, button, sound, light_matrix
import motor
import runloop
import color_sensor
import urandom

class QLearningAgent:
	def __init__(self, env, alpha=0.1, gamma=0.9, epsilon=0.1):
		self.env = env
		self.alpha = alpha
		self.gamma = gamma
		self.epsilon = epsilon
		self.qtable = self.initialize_qtable()
		self.actions = ["SWEEP_LEFT", "SWEEP_RIGHT"]# Adjusting actions for sweep motion

	def initialize_qtable(self):
		table = {}
		for key, val in enumerate(self.env.states):
			qvalue = [0] * 2
			table[val] = qvalue
		return table

	def choose_action(self, state):
		k = urandom.uniform(0, 1)
		if self.epsilon > k:
			print("Random action chosen")
			action = urandom.choice(self.actions)
		else:
			actions = self.qtable[state]
			max_val = max(actions)
			indices = [ind for ind, val in enumerate(actions) if val == max_val]
			action = self.actions[urandom.choice(indices)]

		self.last_state = state
		self.last_action = self.actions.index(action)
		return action

	def learn(self, reward, next_state):
		predict = self.qtable[self.last_state][self.last_action]
		target = reward + self.gamma * max(self.qtable[next_state])
		self.qtable[self.last_state][self.last_action] += self.alpha * (target - predict)
		print('Reward: {}, Q-table: {}'.format(reward, self.qtable))


class Environment:
	def __init__(self):
		self.states = {
			-1: 'ERR',
			0: "LEGO_BLACK",# Boundary state
			1: "LEGO_MAGENTA",
			3: "LEGO_BLUE",
			4: "LEGO_AZURE",
			6: "LEGO_GREEN",# Goal state
			7: "LEGO_YELLOW",
			9: "LEGO_RED",
			10: "LEGO_WHITE",# Boundary state
		}
		self.path_order = [0, 6, 7, 1, 3, 9, 0]# Order of colors
		self.sweep_degrees = 30# Maintain full sweep size
		self.sweep_speed = 50
		self.goal_state = [6]
		self.boundary_state = [0]# Defining boundary states
		self.high_negative_reward = -10# Increased penalty
		self.reward_default = -1
		self.reward_goal = 10
		self.current_state = None
	
	async def reset(self):
		print("Place the robot's sensor at the starting position and press the left button to start.")
		await debounce_button(button.LEFT)
		self.current_state = color_sensor.color(port.D)
		return self.current_state

	async def step(self, action):
		# Move in full sweep increments
		if action == "SWEEP_LEFT":
			await self.run_motor(-self.sweep_degrees)
		elif action == "SWEEP_RIGHT":
			await self.run_motor(self.sweep_degrees)

		# Update the current state after the complete action
		self.current_state = color_sensor.color(port.D)

		# Display the first letter of the current color
		if self.current_state in self.states:
			color_initial = self.states[self.current_state][0]# First letter
			light_matrix.write(color_initial)
			await runloop.sleep_ms(500)# Pause to view the letter

		# Check if we've hit a boundary or reached the goal
		if self.current_state in self.boundary_state:
			print("Boundary encountered. Penalty incurred and episode ends.")
			sound.beep(1000, 500, 100)# Beep to signal boundary hit
			# Stop the episode, return boundary penalty reward
			return (self.current_state, self.high_negative_reward, True)

		if self.current_state in self.goal_state:
			print("Goal reached. Positive reward and episode ends.")
			# Stop the episode, return goal reward
			return (self.current_state, self.reward_goal, True)

		# If neither a boundary nor a goal state:
		return (self.current_state, self.reward_default, False)

	async def run_motor(self, degrees):
		# Execute motor movement synchronously to have immediate feedback control
		await motor.run_for_degrees(port.B, degrees, self.sweep_speed)


	async def setup_path(self):
		print("Setting up the course path...")
		for color in self.path_order:
			print("Position {} tile and press the left button to proceed.".format(self.states[color]))
			await debounce_button(button.LEFT)
			await self.run_motor(self.sweep_degrees)

async def debounce_button(target_button, delay_ms=500):
	# Debounce by adding a short delay after a button press is detected
	while not button.pressed(target_button):
		await runloop.sleep_ms(50)
	# Delay for debouncing
	await runloop.sleep_ms(delay_ms)

async def main_loop():
	setup_done = False
	prompt_displayed = False
	print("Starting main loop...")

	while True:
		if not prompt_displayed:
			print("Press the right button to set up the course or the left button to start RL.")
			prompt_displayed = True

		if button.pressed(button.RIGHT):
			print("Right button pressed, setting up path...")
			await debounce_button(button.RIGHT)
			await env.setup_path()
			setup_done = True
			prompt_displayed = False
			print("Setup done.")

		elif button.pressed(button.LEFT):
			print("Left button pressed.")
			if setup_done:
				print("Starting RL as setup is done.")
				await debounce_button(button.LEFT)
				break
			else:
				print("Setup not completed yet. Cannot start RL.")

		await runloop.sleep_ms(100)

	for i in range(EPISODES):
		print("EPISODE {}: Position robot over LEGO_BLUE and press left button to begin.".format(i))
		await debounce_button(button.LEFT)
		rew = 0
		ti = 0
		state = await env.reset()
		for j in range(TIMESTEPS):
			print("TIMESTEP {}".format(j))
			action = agent.choose_action(state)
			new_state, reward, done = await env.step(action)
			agent.learn(reward, new_state)
			rew += reward
			state = new_state
			ti += 1
			if done:
				break
		rewards_history.append(rew)
		timesteps.append(ti)
		print("Episode {}: Reward total {}, Rewards History: {}, Timesteps History: {}".format(i,rew,rewards_history,timesteps))


EPSILON = 0.1
env = Environment()
agent = QLearningAgent(env, epsilon=EPSILON)

rewards_history = []
timesteps = []
EPISODES = 10
TIMESTEPS = 15

runloop.run(main_loop())
