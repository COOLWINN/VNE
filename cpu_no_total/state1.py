import networkx as nx
import numpy as np
from network import Network


class EnvState:

    def __init__(self, sub):
        self.sub = sub
        self.cpu = self.cpu()
        self.adjacent_bw = self.calculate_adjacent_bw_all()
        self.degree_centrality = self.calculate_degree_centrality()
        self.closeness_centrality = self.calculate_closeness_centrality()
        self.betweeness_centrality = self.calculate_betweeness_centrality()

    def get_sub(self):
        return self.sub

    def cpu(self):

        tmp = []
        for u in range(self.sub.number_of_nodes()):
            tmp.append(self.sub.nodes[u]['cpu_remain'])

        # normalization
        tmp = (tmp - np.min(tmp)) / (np.max(tmp) - np.min(tmp))
        return tmp

    def cpu_all(self):

        tmp = []
        for u in range(self.sub.number_of_nodes()):
            tmp.append(self.sub.nodes[u]['cpu'])

        # normalization
        tmp = (tmp - np.min(tmp)) / (np.max(tmp) - np.min(tmp))
        return tmp

    def calculate_adjacent_bw_all(self):

        tmp = []
        for u in range(self.sub.number_of_nodes()):
            tmp.append(Network.calculate_adjacent_bw(self.sub, u))

        # normalization
        tmp = (tmp - np.min(tmp)) / (np.max(tmp) - np.min(tmp))
        return tmp

    def calculate_degree_centrality(self):
        tmp = []
        # degree centrality
        for i in nx.degree_centrality(self.sub).values():
            tmp.append(i)
        return tmp

    def calculate_closeness_centrality(self):
        tmp = []
        # closeness centrality
        for j in nx.closeness_centrality(self.sub).values():
            tmp.append(j)
        return tmp

    def calculate_betweeness_centrality(self):
        tmp = []
        # between centrality
        for k in nx.betweenness_centrality(self.sub).values():
            tmp.append(k)
        return tmp

    def initial_state(self):
        self.cpu = self.cpu_all()
        self.adjacent_bw = self.calculate_adjacent_bw_all()

    def current_state(self, cpu_remain, bw_all_remain):
        self.cpu = cpu_remain
        self.adjacent_bw = bw_all_remain

    def state_matrix(self):
        matrix = (self.cpu,
                  self.adjacent_bw,
                  self.degree_centrality,
                  self.closeness_centrality,
                  self.betweeness_centrality)
        return np.vstack(matrix).transpose()
