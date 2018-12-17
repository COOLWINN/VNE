import networkx as nx


def create_sub(path):
    """create a substrate network"""
    with open(path) as file_object:
        lines = file_object.readlines()

    G = nx.Graph()
    node_num, link_num = [int(x) for x in lines[0].split()]
    node_id = 0
    for line in lines[1:node_num + 1]:
        x, y, c = [float(x) for x in line.split()]
        G.add_node(node_id, x_coordinate=x, y_coordinate=y, cpu=c, cpu_remain=c)
        node_id = node_id + 1

    link_id = 0
    for line in lines[-link_num:]:
        src, dst, bw, dis = [float(x) for x in line.split()]
        G.add_edge(int(src), int(dst), link_id=link_id, bw=bw, bw_remain=bw, distance=dis)
        link_id = link_id + 1

    return G


def create_req(i, path):
    """create a new virtual network request"""
    with open(path) as file_object:
        lines = file_object.readlines()

    node_num, link_num, time, duration, maxD = [int(x) for x in lines[0].split()]
    graph = nx.Graph(id=i, type=0, time=time, duration=duration)
    node_id = 0
    for line in lines[1:node_num + 1]:
        x, y, c = [float(x) for x in line.split()]
        graph.add_node(node_id, x_coordinate=x, y_coordinate=y, cpu=c)
        node_id = node_id + 1

    link_id = 0
    for line in lines[-link_num:]:
        src, dst, bw, dis = [float(x) for x in line.split()]
        graph.add_edge(int(src), int(dst), link_id=link_id, bw=bw, distance=dis)
        link_id = link_id + 1

    return graph


def calculate_adjacent_bw(graph, u, kind='bw'):
    """calculate the bandwidth sum of the node u's adjacent links"""
    bw_sum = 0
    for v in graph.neighbors(u):
        if u <= v:
            bw_sum += graph[u][v][kind]
        else:
            bw_sum += graph[v][u][kind]
    return bw_sum
