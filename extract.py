import networkx as nx
import copy


def read_network_file(filename):
    """读取网络拓扑文件并生成一个networkx.Graph实例"""

    node_id, link_id = 0, 0

    with open(filename) as f:
        lines = f.readlines()

    if len(lines[0].split()) == 2:
        """create a substrate network"""

        node_num, link_num = [int(x) for x in lines[0].split()]
        graph = nx.Graph()
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

        node_num, link_num, time, duration, maxD = [int(x) for x in lines[0].split()]
        graph = nx.Graph(type=0, time=time, duration=duration)
        for line in lines[1:node_num + 1]:
            x, y, c = [float(x) for x in line.split()]
            graph.add_node(node_id, x_coordinate=x, y_coordinate=y, cpu=c)
            node_id = node_id + 1

        for line in lines[-link_num:]:
            src, dst, bw, dis = [float(x) for x in line.split()]
            graph.add_edge(int(src), int(dst), link_id=link_id, bw=bw, distance=dis)
            link_id = link_id + 1

    return graph


def read_requests(path):
    """创建虚拟网络请求事件队列"""

    queue = []
    for i in range(2000):
        filename = '%sreq%s.txt' % (path, i)
        vnr_arrive = read_network_file(filename)
        vnr_arrive.graph['id'] = i
        vnr_leave = copy.deepcopy(vnr_arrive)
        vnr_leave.graph['type'] = 1
        vnr_leave.graph['time'] = vnr_arrive.graph['time'] + vnr_arrive.graph['duration']
        queue.append(vnr_arrive)
        queue.append(vnr_leave)

    # sort the data by their time(arrive time or depart time)
    queue.sort(key=lambda r: r.graph['time'])
    return queue


def create_training_set(path):
    """创建虚拟网络请求事件队列"""

    queue = []
    for i in range(1000):
        filename = '%sreq%s.txt' % (path, i)
        vnr_arrive = read_network_file(filename)
        vnr_arrive.graph['id'] = i
        vnr_leave = copy.deepcopy(vnr_arrive)
        vnr_leave.graph['type'] = 1
        vnr_leave.graph['time'] = vnr_arrive.graph['time'] + vnr_arrive.graph['duration']
        queue.append(vnr_arrive)
        queue.append(vnr_leave)

        # sort the data by their time(arrive time or depart time)
    queue.sort(key=lambda r: r.graph['time'])
    return queue
