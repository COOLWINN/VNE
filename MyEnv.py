import gym
from gym import spaces


class MyEnv(gym.Env):

    def __init__(self):
        self.action_space = spaces.Discrete(100)
        self.observation_space = spaces.Box(low=0, high=1, shape=(100, 7))


    def render(self, mode='human'):
        pass

    def step(self, action):


    def reset(self):
        pass
