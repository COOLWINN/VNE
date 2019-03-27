import gym
from gym import spaces
import copy
import numpy as np
from network import Network
from .state2 import EnvState


class MyEnv(gym.Env):

    def __init__(self, sub, vnr):
        self.count = -1
        self.action_num = sub.number_of_nodes()
        self.feature_num = 6
        self.action_space = spaces.Discrete(self.action_num)
        self.observation_space = spaces.Box(low=0, high=1, shape=(self.action_num, self.feature_num), dtype=np.float32)
        self.state = EnvState(sub)
        self.sub = None
        self.vnr = vnr

    def step(self, action):
        self.count = self.count + 1
        cpu_remain, flow_remain, bw_all_remain = [], [], []
        for u in range(self.action_num):
            adjacent_bw = Network.calculate_adjacent_bw(self.sub, u, 'bw_remain')
            if u == action:
                self.sub.nodes[action]['cpu_remain'] -= self.vnr.nodes[self.count]['cpu']
                self.sub.nodes[action]['flow_remain'] -= self.vnr.nodes[self.count]['flow']
                adjacent_bw -= Network.calculate_adjacent_bw(self.vnr, self.count)
            cpu_remain.append(self.sub.nodes[u]['cpu_remain'])
            flow_remain.append(self.sub.nodes[u]['flow_remain'])
            bw_all_remain.append(adjacent_bw)
        cpu_remain = (cpu_remain - np.min(cpu_remain)) / (np.max(cpu_remain) - np.min(cpu_remain))
        flow_remain = (flow_remain - np.min(flow_remain)) / (np.max(flow_remain) - np.min(flow_remain))
        bw_all_remain = (bw_all_remain - np.min(bw_all_remain)) / (np.max(bw_all_remain) - np.min(bw_all_remain))
        self.state.current_state(cpu_remain, flow_remain, bw_all_remain)
        reward = (self.sub.nodes[action]['cpu_remain']+self.sub.nodes[action]['flow_remain']) / (self.sub.nodes[action]['cpu']+self.sub.nodes[action]['flow'])
        return self.state.state_matrix(), reward, False, {}

    def reset(self):
        # reset count
        self.count = -1
        # reset state
        self.state.initial_state()
        # reset sub
        self.sub = copy.deepcopy(self.state.get_sub())
        # return state matrix
        return self.state.state_matrix()

    def render(self, mode='human'):
        pass
