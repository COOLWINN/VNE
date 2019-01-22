import networkx as nx
from utils import read_network_file, get_path_capacity
from config import configure
from evaluation import Evaluation


class Substrate:

    def __init__(self, filename):
        self.net = read_network_file(filename)
        self.agent = None
        self.mapped_info = {}
        self.evaluation = Evaluation(self.net)

    def mapping(self, vnr, node_algorithm):
        """two phrases:node mapping and link mapping"""

        self.evaluation.total_arrived += 1

        # mapping virtual nodes
        node_map = self.node_mapping(vnr, node_algorithm)

        if len(node_map) == vnr.number_of_nodes():
            # mapping virtual links
            print("link mapping...")
            link_map = self.link_mapping(vnr, node_map)
            if len(link_map) == vnr.number_of_edges():
                self.mapped_info.update({vnr.graph['id']: (node_map, link_map)})
                self.change_resource(vnr, 'allocate')
                print("Success!")
            else:
                print("Fail at the stage of link mapping!")
        else:
            print("Fail at the stage of node mapping!")

    def node_mapping(self, vnr, algorithm):
        """求解节点映射问题"""

        print("node mapping...")

        # 如果刚开始映射，那么需要对所选用的算法进行配置
        if self.agent is None:
            self.agent = configure(self, algorithm)

        # 使用指定的算法进行节点映射并得到节点映射集合
        node_map = self.agent.run(self, vnr)

        # 返回节点映射集合
        return node_map

    def link_mapping(self, vnr, node_map):
        """求解链路映射问题"""

        link_map = {}
        for vLink in vnr.edges:
            vn_from = vLink[0]
            vn_to = vLink[1]
            sn_from = node_map[vn_from]
            sn_to = node_map[vn_to]
            if nx.has_path(self.net, source=sn_from, target=sn_to):
                for path in nx.all_shortest_paths(self.net, source=sn_from, target=sn_to):
                    if get_path_capacity(self.net, path) >= vnr[vn_from][vn_to]['bw']:
                        link_map.update({vLink: path})
                        break
                    else:
                        continue

        # 返回链路映射集合
        return link_map

    def change_resource(self, req, instruction):
        """分配或释放节点和链路资源"""

        # 读取该虚拟网络请求的映射信息
        req_id = req.graph['id']
        node_map = self.mapped_info[req_id][0]
        link_map = self.mapped_info[req_id][1]

        factor = -1
        if instruction == 'release':
            factor = 1

        # 分配或释放节点资源
        for v_id, s_id in node_map.items():
            self.net.nodes[s_id]['cpu_remain'] += factor * req.nodes[v_id]['cpu']

        # 分配或释放链路资源
        for vl, path in link_map.items():
            link_resource = req[vl[0]][vl[1]]['bw']
            start = path[0]
            for end in path[1:]:
                self.net[start][end]['bw_remain'] += factor * link_resource
                start = end

        if instruction == 'allocate':
            # 增加实验结果
            self.evaluation.add(req, link_map)

        if instruction == 'release':
            # 移除相应的映射信息
            self.mapped_info.pop(req_id)
