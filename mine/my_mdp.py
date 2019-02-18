import gym
from gym import spaces
import copy
import networkx as nx
import numpy as np


def calculate_adjacent_bw(graph, u, kind='bw'):
    """计算一个节点的相邻链路带宽和，默认为总带宽和，若计算剩余带宽资源和，需指定kind属性为bw-remain"""

    bw_sum = 0
    for v in graph.neighbors(u):
        bw_sum += graph[u][v][kind]
    return bw_sum


class MyEnv(gym.Env):

    def __init__(self, sub, vnr):
        self.count = -1
        self.n_action = sub.number_of_nodes()
        # when we reset,we should also reset the sub,that's why I save an original sub
        self.origin = copy.deepcopy(sub)
        # this sub is for us to change states when we make a step
        self.sub = copy.deepcopy(sub)
        self.vnr = vnr
        self.action_space = spaces.Discrete(self.n_action)
        self.observation_space = spaces.Box(low=0, high=1, shape=(self.n_action, 7), dtype=np.float32)
        cpu_all, bw_all = [], []
        self.degree, self.closeness, self.betweeness = [], [], []
        for u in range(self.n_action):
            cpu_all.append(sub.nodes[u]['cpu'])
            bw_all.append(calculate_adjacent_bw(sub, u))

        # normalization
        self.cpu_all = (cpu_all - np.min(cpu_all)) / (np.max(cpu_all) - np.min(cpu_all))
        self.bw_all = (bw_all - np.min(bw_all)) / (np.max(bw_all) - np.min(bw_all))
        self.cpu_remain = self.cpu_all
        self.bw_all_remain = self.bw_all
        # degree centrality
        for i in nx.degree_centrality(sub).values():
            self.degree.append(i)
        # closeness centrality
        for j in nx.closeness_centrality(sub).values():
            self.closeness.append(j)
        # between centrality
        for k in nx.betweenness_centrality(sub).values():
            self.betweeness.append(k)
        self.state = None

    def step(self, action):
        self.count = self.count + 1
        self.cpu_remain, self.bw_all_remain = [], []
        for u in range(self.n_action):
            adjacent_bw = calculate_adjacent_bw(self.sub, u, 'bw_remain')
            if u == action:
                self.sub.nodes[action]['cpu_remain'] -= self.vnr.nodes[self.count]['cpu']
                adjacent_bw -= calculate_adjacent_bw(self.vnr, self.count)
            self.cpu_remain.append(self.sub.nodes[u]['cpu_remain'])
            self.bw_all_remain.append(adjacent_bw)

        self.cpu_remain = (self.cpu_remain - np.min(self.cpu_remain)) / (
                np.max(self.cpu_remain) - np.min(self.cpu_remain))
        self.bw_all_remain = (self.bw_all_remain - np.min(self.bw_all_remain)) / (
                np.max(self.bw_all_remain) - np.min(self.bw_all_remain))

        self.state = (self.cpu_all,
                      self.cpu_remain,
                      self.bw_all,
                      self.bw_all_remain,
                      self.degree,
                      self.closeness,
                      self.betweeness)

        reward = self.sub.nodes[action]['cpu_remain'] / self.sub.nodes[action]['cpu']
        return np.vstack(self.state).transpose(), reward, False, {}

    def reset(self):
        self.count = -1
        self.sub = copy.deepcopy(self.origin)
        self.cpu_remain = self.cpu_all
        self.bw_all_remain = self.bw_all
        self.state = (self.cpu_all,
                      self.cpu_remain,
                      self.bw_all,
                      self.bw_all_remain,
                      self.degree,
                      self.closeness,
                      self.betweeness)
        return np.vstack(self.state).transpose()

    def render(self, mode='human'):
        pass
