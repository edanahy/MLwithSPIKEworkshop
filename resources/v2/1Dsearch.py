# 1D Search via Q-Learning

########
# First developed by Tanushree Burman, Tufts CEEO 2024
# Modified and adapted for ML workshop October 21, 2024
#######
# PORTS
#   MOTOR in Port B
#   COLOR SENSOR in Port D
#######

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
        self.actions = ["SWEEP_LEFT", "SWEEP_RIGHT"]

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
            0: "LEGO_BLACK",
            1: "LEGO_MAGENTA",
            3: "LEGO_BLUE",
            4: "LEGO_AZURE",
            6: "LEGO_GREEN",
            7: "LEGO_YELLOW",
            9: "LEGO_RED",
            10: "LEGO_WHITE",
        }
        self.sweep_speed = 30
        self.goal_state = [6]
        self.boundary_state = [0]
        self.high_negative_reward = -10
        self.reward_default = -1
        self.reward_goal = 10
        self.current_state = None

    async def reset(self):
        print("Place the robot's sensor at the starting position and press the left button to start.")
        await debounce_button(button.LEFT)
        self.current_state = color_sensor.color(port.D)
        return self.current_state

    async def step(self, action):
        if action == "SWEEP_LEFT":
            await self.sweep_until_next_color(direction=-1)
        elif action == "SWEEP_RIGHT":
            await self.sweep_until_next_color(direction=1)

        if self.current_state in self.states:
            color_initial = self.states[self.current_state][0]
            light_matrix.write(color_initial)
            await runloop.sleep_ms(500)

        if self.current_state in self.boundary_state:
            print("Boundary encountered. Penalty incurred and episode ends.")
            sound.beep(1000, 500, 100)
            return (self.current_state, self.high_negative_reward, True)

        if self.current_state in self.goal_state:
            print("Goal reached. Positive reward and episode ends.")
            return (self.current_state, self.reward_goal, True)

        return (self.current_state, self.reward_default, False)

    async def sweep_until_next_color(self, direction):
        """
        Moves the motor arm in the given direction until a new complete color is detected.
        :param direction: Direction to sweep in: 1 for right, -1 for left.
        """
        current_color = self.current_state
        motor.run(port.B, direction * self.sweep_speed)# Begin moving motor

        # Initial State: Detect edge of current brick
        detected_transition = False

        while not detected_transition:
            await runloop.sleep_ms(100)
            observed_color = color_sensor.color(port.D)

            if observed_color != current_color:
                # Transition across the edge
                reads = [color_sensor.color(port.D) for _ in range(5)]

                # Check if the readings stabilize on a new color (ignoring -1 as a valid stable state)
                if all(r == observed_color and r != -1 for r in reads):
                    self.current_state = observed_color
                    detected_transition = True
                    print("Stable color detected: {}".format(self.states.get(observed_color, 'Unknown')))

        motor.stop(port.B,stop=motor.COAST)# Stop motor upon detecting stable new color


async def debounce_button(target_button, delay_ms=500):
    while not button.pressed(target_button):
        await runloop.sleep_ms(50)
    await runloop.sleep_ms(delay_ms)

async def main_loop():
    print("Starting main loop...")

    print("Place the LEGO bricks in the desired arc, starting and stopping with black bricks as boundaries.")
    print("Press the left button to start RL training.")

    while True:
        if button.pressed(button.LEFT):
            print("Left button pressed. Starting RL.")
            await debounce_button(button.LEFT)
            break

        await runloop.sleep_ms(100)

    for i in range(EPISODES):
        print("EPISODE {}: Position robot over starting LEGO brick and press left button to begin.".format(i))
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
EPISODES = 20
TIMESTEPS = 15

runloop.run(main_loop())

