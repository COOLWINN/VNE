import networkx as nx
import numpy as np
from network import Network


class EnvState:

    def __init__(self, sub):
        self.sub = sub
        self.cpu = self.cpu()
        self.flow = self.flow()
        self.queue = self.queue()
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

    def flow(self):

        tmp = []
        for u in range(self.sub.number_of_nodes()):
            tmp.append(self.sub.nodes[u]['flow_remain'])

        # normalization
        tmp = (tmp - np.min(tmp)) / (np.max(tmp) - np.min(tmp))
        return tmp

    def queue(self):

        tmp = []
        for u in range(self.sub.number_of_nodes()):
            tmp.append(self.sub.nodes[u]['queue_remain'])

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

    def flow_all(self):

        tmp = []
        for u in range(self.sub.number_of_nodes()):
            tmp.append(self.sub.nodes[u]['flow'])

        # normalization
        tmp = (tmp - np.min(tmp)) / (np.max(tmp) - np.min(tmp))
        return tmp

    def queue_all(self):

        tmp = []
        for u in range(self.sub.number_of_nodes()):
            tmp.append(self.sub.nodes[u]['queue'])

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
        self.flow = self.flow_all()
        self.queue = self.queue_all()
        self.adjacent_bw = self.calculate_adjacent_bw_all()

    def current_state(self, cpu_remain, flow_remain, queue_remain, bw_all_remain):
        self.cpu = cpu_remain
        self.flow = flow_remain
        self.queue = queue_remain
        self.adjacent_bw = bw_all_remain

    def state_matrix(self):
        matrix = (self.cpu,
                  self.flow,
                  self.queue,
                  self.adjacent_bw,
                  self.degree_centrality,
                  self.closeness_centrality,
                  self.betweeness_centrality)
        return np.vstack(matrix).transpose()
