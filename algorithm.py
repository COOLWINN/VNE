import os
import copy
import time
from evaluation import Evaluation
from comparison1.grc import GRC
from comparison2.mcts import MCTS
from comparison3.reinforce import RL
from cpu_flow.agent2 import Agent2
from cpu_flow_queue.agent3 import Agent3
from cpu_.agent import PolicyGradient
from network import Network
from event import Event
from queue import PriorityQueue
import tensorflow as tf
from analysis import Analysis


class Algorithm:

    def __init__(self, name, node_arg=10, link_method=1, granularity=1):
        self.name = name
        self.agent = None
        self.node_arg = node_arg
        self.link_method = link_method
        self.granularity = granularity
        self.evaluation = Evaluation()

    def execute(self, result_dir, network_path, sub_filename, req_num=1000, child_num=0):
        tool = Analysis(result_dir)
        networks = Network(network_path)
        sub, requests, children = networks.get_networks(sub_filename, req_num, child_num, self.granularity)
        events = PriorityQueue()
        for req in requests:
            events.put(Event(req))
        tf.reset_default_graph()
        with tf.Session() as sess:
            self.configure(sub, sess)
            start = time.time()
            self.handle(tool, sub, events)
            runtime = time.time() - start
        tf.get_default_graph().finalize()
        tool.save_evaluations(self.evaluation, '%s-VNE.txt' % self.name)
        return runtime

    def configure(self, sub, sess=None):

        if self.name == 'GRC':
            agent = GRC(damping_factor=0.9, sigma=1e-6)

        elif self.name == 'MCTS':
            agent = MCTS(computation_budget=5, exploration_constant=0.5)

        elif self.name == 'RL':
            training_set_path = 'comparison3/training_set/'
            networks = Network(training_set_path)
            training_set = networks.get_reqs_for_train(1000)
            agent = RL(sub=sub,
                       n_actions=sub.number_of_nodes(),
                       n_features=4,
                       learning_rate=0.05,
                       epoch_num=self.node_arg,
                       batch_size=100)
            agent.train(training_set)

        elif self.name == 'ML1':
            agent = PolicyGradient(sess=sess,
                                   action_num=sub.number_of_nodes(),
                                   feature_num=7,
                                   learning_rate=0.02,
                                   reward_decay=0.95,
                                   episodes=self.node_arg)
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

        elif self.name == 'ML3':
            agent = Agent3(action_num=sub.number_of_nodes(),
                           feature_num=11,
                           learning_rate=0.02,
                           reward_decay=0.95,
                           episodes=self.node_arg)

        else:
            agent = PolicyGradient(sess=sess,
                                   action_num=sub.number_of_nodes(),
                                   feature_num=7,
                                   learning_rate=0.02,
                                   reward_decay=0.95,
                                   episodes=self.node_arg)
        self.agent = agent

    def handle(self, tool, sub, events, requests=None):

        child_algorithm = Algorithm('MCTS', link_method=1)

        while not events.empty():

            req = events.get().req
            req_id = req.graph['id']
            parent_id = req.graph['parent']

            if parent_id == -1:
                if req.graph['type'] == 0:
                    print("\nTry to map request%s: " % req_id)

                    if self.mapping(sub, req):
                        req_leave = copy.deepcopy(req)
                        req_leave.graph['type'] = 1
                        req_leave.graph['time'] = req.graph['time'] + req.graph['duration']
                        events.put(Event(req_leave))

                    if ((req_id + 1) - 1000) % 200 == 0:
                        filename1 = '%s-node-%s.txt' % (self.name, req_id)
                        filename2 = '%s-link-%s.txt' % (self.name, req_id)
                        tool.save_network_load(sub, filename1, filename2)

                if req.graph['type'] == 1:
                    Network.recover(sub, req, self.granularity)

            else:

                if parent_id in sub.graph['mapped_info'].keys():
                    child_algorithm.configure(req)
                    print("\nTry to map the %sth upper request onto virtual network %s: " % (req_id, parent_id))
                    self.evaluation.total_arrived += 1
                    if child_algorithm.mapping(requests[parent_id], req):
                        print("Success!")
                        self.evaluation.collect(requests[parent_id], req)
                    else:
                        print("Failure")
        accepted_num = self.evaluation.total_accepted - child_algorithm.evaluation.total_accepted
        print("accepted requests: %s" % accepted_num)
        print("arrived child requests: %s" % child_algorithm.evaluation.total_arrived)
        print("accepted child requests: %s" % child_algorithm.evaluation.total_accepted)

    def mapping(self, sub, req):
        """两步映射：先节点映射阶段再链路映射阶段"""

        self.evaluation.total_arrived += 1

        # mapping virtual nodes
        node_map = self.node_mapping(sub, req)

        if len(node_map) == req.number_of_nodes():
            # mapping virtual links
            print("link mapping...")
            link_map = self.link_mapping(sub, req, node_map)
            if len(link_map) == req.number_of_edges():
                Network.allocate(sub, req, node_map, link_map, self.granularity)
                # 更新实验结果
                self.evaluation.collect(sub, req, link_map)
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

    def link_mapping(self, sub, req, node_map):
        if self.link_method == 1:
            # 剪枝后再寻最短路径
            link_map = Network.cut_then_find_path(sub, req, node_map)
        else:
            # K最短路径
            link_map = Network.find_path(sub, req, node_map, 5)

        return link_map

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
