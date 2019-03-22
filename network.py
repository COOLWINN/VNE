import copy
import networkx as nx
from itertools import islice


class Network:
    def __init__(self, path):
        self.files_dir = path

    def get_networks(self, sub_filename, req_num, child_req_num=0):
        """读取number个虚拟网络及其自虚拟网络请求，构成底层虚拟网络请求事件队列和子虚拟网络请求事件队列"""
        # 底层物理网络
        sub = self.read_network_file(sub_filename)
        # 第1层虚拟网络请求
        queue1 = self.get_reqs(req_num)
        # 第2层虚拟网络请求
        queue2 = self.get_child_reqs(req_num, child_req_num)
        return sub, queue1, queue2

    def get_reqs(self, req_num):
        """读取req_num个虚拟网络请求文件，构建虚拟网络请求事件队列"""
        queue = []
        for i in range(req_num):
            filename = 'req%d.txt' % i
            req_arrive = self.read_network_file(filename)
            req_arrive.graph['id'] = i
            req_leave = copy.deepcopy(req_arrive)
            req_leave.graph['type'] = 1
            req_leave.graph['time'] = req_arrive.graph['time'] + req_arrive.graph['duration']
            queue.append(req_arrive)
            queue.append(req_leave)
        # 按照时间（到达时间或离开时间）对这些虚拟网络请求从小到大进行排序
        queue.sort(key=lambda r: r.graph['time'])
        return queue

    def get_child_reqs(self, req_num, child_req_num):
        """读取子虚拟网络请求文件，构建子虚拟网络请求事件队列"""
        queue = []
        for i in range(req_num):
            for j in range(child_req_num):
                child_req_filename = 'req%d-%d.txt' % (i, j)
                child_req = self.read_network_file(child_req_filename)
                child_req.graph['id'] = j
                queue.append(child_req)
        return queue

    def read_network_file(self, filename):
        """读取网络文件并生成networkx.Graph实例"""

        mapped_info = {}
        node_id, link_id = 0, 0

        with open(self.files_dir + filename) as f:
            lines = f.readlines()

        if len(lines[0].split()) == 2:
            """create a substrate network"""

            node_num, link_num = [int(x) for x in lines[0].split()]
            graph = nx.Graph(mapped_info=mapped_info)
            for line in lines[1: node_num + 1]:
                x, y, c = [float(x) for x in line.split()]
                graph.add_node(node_id, x_coordinate=x, y_coordinate=y, cpu=c, cpu_remain=c)
                node_id = node_id + 1

            for line in lines[-link_num:]:
                src, dst, bw, dis = [float(x) for x in line.split()]
                graph.add_edge(int(src), int(dst), link_id=link_id, bw=bw, bw_remain=bw, distance=dis)
                link_id = link_id + 1
        else:
            """create a virtual network"""
            node_num, link_num, time, duration, max_dis = [int(x) for x in lines[0].split()]
            graph = nx.Graph(type=0, time=time, duration=duration, mapped_info=mapped_info)
            for line in lines[1:node_num + 1]:
                x, y, c = [float(x) for x in line.split()]
                graph.add_node(node_id, x_coordinate=x, y_coordinate=y, cpu=c, cpu_remain=c)
                node_id = node_id + 1

            for line in lines[-link_num:]:
                src, dst, bw, dis = [float(x) for x in line.split()]
                graph.add_edge(int(src), int(dst), link_id=link_id, bw=bw, bw_remain=bw, distance=dis)
                link_id = link_id + 1

        return graph

    @staticmethod
    def get_path_capacity(sub, path):
        """找到一条路径中带宽资源最小的链路并返回其带宽资源值"""

        bandwidth = 1000
        head = path[0]
        for tail in path[1:]:
            if sub[head][tail]['bw_remain'] <= bandwidth:
                bandwidth = sub[head][tail]['bw_remain']
            head = tail
        return bandwidth

    @staticmethod
    def calculate_adjacent_bw(graph, u, kind='bw'):
        """计算一个节点的相邻链路带宽和，默认为总带宽和，若计算剩余带宽资源和，需指定kind属性为bw-remain"""

        bw_sum = 0
        for v in graph.neighbors(u):
            bw_sum += graph[u][v][kind]
        return bw_sum

    @staticmethod
    def k_shortest_path(graph, source, target, k=5):
        """K最短路径算法"""
        return list(islice(nx.shortest_simple_paths(graph, source, target), k))
