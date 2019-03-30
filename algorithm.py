import copy
import time
import networkx as nx
from evaluation import Evaluation
from comparison1.grc import GRC
from comparison2.mcts import MCTS
from comparison3.reinforce import RL
from cpu_no_total.agent1 import Agent1
from cpu_flow.agent2 import Agent2
from cpu_flow_queue.agent3 import Agent3
from cpu_.agent import PolicyGradient
from network import Network
from event import Event
from queue import PriorityQueue
import tensorflow as tf


class Algorithm:

    def __init__(self, name, node_arg=0, link_arg=1):
        self.name = name
        self.agent = None
        self.node_arg = node_arg
        self.link_arg = link_arg
        self.evaluation = None

    def execute(self, network_path, sub_filename, granularity=1):
        networks = Network(network_path)
        sub, requests = networks.get_networks_single_layer(sub_filename, 1000, granularity)
        events = PriorityQueue()
        for req in requests:
            events.put(Event(req))
        tf.reset_default_graph()
        with tf.Session() as sess:
            self.configure(sub, sess)
            start = time.time()
            self.handle(sub, events)
            runtime = time.time()-start
        tf.get_default_graph().finalize()
        return runtime

    def configure(self, sub, sess=None):

        self.evaluation = Evaluation(sub)

        if self.name == 'GRC':
            agent = GRC(damping_factor=0.9, sigma=1e-6)
            self.agent = agent

        elif self.name == 'MCTS':
            agent = MCTS(computation_budget=5, exploration_constant=0.5)
            self.agent = agent

        elif self.name == 'RL':
            training_set_path = 'comparison3/training_set/'
            networks = Network(training_set_path)
            training_set = networks.get_reqs(1000)
            agent = RL(sub=sub,
                       n_actions=sub.number_of_nodes(),
                       n_features=4,
                       learning_rate=0.05,
                       epoch_num=self.node_arg,
                       batch_size=100)
            agent.train(training_set)
            self.agent = agent

        elif self.name == 'ML1':
            agent = PolicyGradient(sess=sess,
                                   action_num=sub.number_of_nodes(),
                                   feature_num=7,
                                   learning_rate=0.02,
                                   reward_decay=0.95,
                                   episodes=self.node_arg)
            self.agent = agent
            # agent = Agent1(action_num=sub.number_of_nodes(),
            #                feature_num=5,
            #                learning_rate=0.02,
            #                reward_decay=0.95,
            #                episodes=self.node_arg)

        elif self.name == 'ML2':
            agent = Agent2(action_num=sub.number_of_nodes(),
                           feature_num=9,
                           learning_rate=0.02,
                           reward_decay=0.95,
                           episodes=self.node_arg)
            self.agent = agent

        elif self.name == 'ML3':
            agent = Agent3(action_num=sub.number_of_nodes(),
                           feature_num=11,
                           learning_rate=0.02,
                           reward_decay=0.95,
                           episodes=self.node_arg)
            self.agent = agent

        elif self.name == 'ML':
            agent = PolicyGradient(sess=sess,
                                   action_num=sub.number_of_nodes(),
                                   feature_num=7,
                                   learning_rate=0.02,
                                   reward_decay=0.95,
                                   episodes=self.node_arg)
            self.agent = agent
        else:
            print("Input Error!")

    def handle(self, sub, events, requests=None):

        total, success = 0, 0

        while not events.empty():

            req = events.get().req
            req_id = req.graph['id']
            parent_id = req.graph['parent']

            if parent_id == -1:
                if req.graph['type'] == 0:
                    self.evaluation.total_arrived += 1
                    print("\nTry to map request%s: " % req_id)
                    if self.mapping(sub, req):
                        req_leave = copy.deepcopy(req)
                        req_leave.graph['type'] = 1
                        req_leave.graph['time'] = req.graph['time'] + req.graph['duration']
                        events.put(Event(req_leave))

                if req.graph['type'] == 1:
                    if req_id in sub.graph['mapped_info'].keys():
                        print("\nRelease the resources which are occupied by request%s" % req_id)
                        self.change_resource(sub, req, 'release')

            else:
                if parent_id in sub.graph['mapped_info'].keys():
                    child_algorithm = Algorithm('mcts', link_arg=5)
                    child_algorithm.configure(req)
                    print("\nTry to map the %sth upper request onto virtual network %s: " % (req_id, parent_id))
                    total = total + 1
                    self.evaluation.total_arrived += 1
                    if child_algorithm.mapping(requests[parent_id], req):
                        print("Success!")
                        self.evaluation.collect(req)
                        success = success + 1
                    else:
                        print("Failure")
        accepted_num = self.evaluation.total_accepted - success
        print("accepted requests: %s" % accepted_num)
        print("arrived child requests: %s" % total)
        print("accepted child requests: %s" % success)
        return accepted_num / self.evaluation.total_arrived

    def mapping(self, sub, req):
        """two phrases:node mapping and link mapping"""

        # mapping virtual nodes
        node_map = self.node_mapping(sub, req)

        if len(node_map) == req.number_of_nodes():
            # mapping virtual links
            print("link mapping...")
            link_map = self.link_mapping(sub, req, node_map, self.link_arg)
            if len(link_map) == req.number_of_edges():
                mapped_info = sub.graph['mapped_info']
                mapped_info.update({req.graph['id']: (node_map, link_map)})
                sub.graph['mapped_info'] = mapped_info
                self.change_resource(sub, req, 'allocate')
                print("Success!")
                return True
            else:
                print("Failed to map all links!")
                return False
        else:
            print("Failed to map all nodes!")
            return False

    def node_mapping(self, sub, req):
        """求解节点映射问题"""

        print("node mapping...")

        # 使用指定的算法进行节点映射并得到节点映射集合
        node_map = self.agent.run(sub, req)

        # 返回节点映射集合
        return node_map

    @staticmethod
    def link_mapping(sub, req, node_map, k=1):
        """求解链路映射问题"""

        link_map = {}
        for vLink in req.edges:
            vn_from = vLink[0]
            vn_to = vLink[1]
            sn_from = node_map[vn_from]
            sn_to = node_map[vn_to]
            if nx.has_path(sub, source=sn_from, target=sn_to):
                for path in Network.k_shortest_path(sub, sn_from, sn_to, k):
                    if Network.get_path_capacity(sub, path) >= req[vn_from][vn_to]['bw']:
                        link_map.update({vLink: path})
                        break
                    else:
                        continue

        # 返回链路映射集合
        return link_map

    def change_resource(self, sub, req, instruction):
        """分配或释放节点和链路资源"""

        # 读取该虚拟网络请求的映射信息
        req_id = req.graph['id']
        node_map = sub.graph['mapped_info'][req_id][0]
        link_map = sub.graph['mapped_info'][req_id][1]

        factor = -1
        if instruction == 'release':
            factor = 1

        # 分配或释放节点资源
        for v_id, s_id in node_map.items():
            sub.nodes[s_id]['cpu_remain'] += factor * req.nodes[v_id]['cpu']

        # 分配或释放链路资源
        for vl, path in link_map.items():
            link_resource = req[vl[0]][vl[1]]['bw']
            start = path[0]
            for end in path[1:]:
                sub[start][end]['bw_remain'] += factor * link_resource
                start = end

        if instruction == 'allocate':
            # 增加实验结果
            self.evaluation.collect(req, link_map)

        if instruction == 'release':
            # 移除相应的映射信息
            mapped_info = sub.graph['mapped_info']
            mapped_info.pop(req_id)
            sub.graph['mapped_info'] = mapped_info

    # def upper_mapping(self, vnr, algorithm, sub):
    #     """only for child virtual network requests"""
    #     self.evaluation.total_arrived += 1
    #     # 如果刚开始映射，那么需要对所选用的算法进行配置
    #     if self.agent is None:
    #         self.agent = configure(self, algorithm, arg=0)
    #
    #     node_map = self.agent.run_run(self, vnr, sub)
    #
    #     if len(node_map) == vnr.number_of_nodes():
    #         link_map = {}
    #         for vLink in vnr.edges:
    #             vn_from = vLink[0]
    #             vn_to = vLink[1]
    #             sn_from = node_map[vn_from]
    #             sn_to = node_map[vn_to]
    #             self.no_solution = True
    #             if nx.has_path(self.net, source=sn_from, target=sn_to):
    #                 for path in k_shortest_path(self.net, sn_from, sn_to):
    #                     if get_path_capacity(path) >= vnr[vn_from][vn_to]['bw']:
    #                         link_map.update({vLink: path})
    #                         self.no_solution = False
    #                         break
    #                     else:
    #                         continue
    #
    #         if len(link_map) == vnr.number_of_edges():
    #             self.mapped_info.update({vnr.graph['id']: (node_map, link_map)})
    #             self.change_resource(vnr, 'allocate')
    #             return True
    #         else:
    #             return False
    #     else:
    #         return False
