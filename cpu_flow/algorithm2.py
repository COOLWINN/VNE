import networkx as nx
from evaluation import Evaluation
from .agent2 import Agent
from network import Network


class Algorithm:

    def __init__(self, node_arg=0, link_arg=1):
        self.agent = None
        self.node_arg = node_arg
        self.link_arg = link_arg
        self.evaluation = None

    def configure(self, sub):
        self.evaluation = Evaluation(sub)
        agent = Agent(action_num=sub.number_of_nodes(),
                      feature_num=6,
                      learning_rate=0.02,
                      reward_decay=0.95,
                      episodes=self.node_arg)

        self.agent = agent

    def handle(self, sub, queue1, queue2):
        for req in queue1:

            # the id of current request
            req_id = req.graph['id']

            if req.graph['type'] == 0:
                """a request which is newly arrived"""

                print("\nTry to map request%s: " % req_id)
                self.mapping(sub, req)

            if req.graph['type'] == 1:
                """a request which is ready to leave"""
                if req_id in sub.graph['mapped_info'].keys():
                    print("\nRelease the resources which are occupied by request%s" % req_id)
                    self.change_resource(sub, req, 'release')

        print("accepted requests: %s" % self.evaluation.total_accepted)
        print("arrived requests: %s" % self.evaluation.total_arrived)

    def mapping(self, sub, req):
        """two phrases:node mapping and link mapping"""

        self.evaluation.total_arrived += 1

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

    def link_mapping(self, sub, req, node_map, k=1):
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
            sub.nodes[s_id]['flow_remain'] += factor * req.nodes[v_id]['flow']

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
