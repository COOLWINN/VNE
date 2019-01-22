def calculate_adjacent_bw(graph, u, kind='bw'):
    """计算一个节点的相邻链路带宽和，默认为总带宽和，若计算剩余带宽资源和，需指定kind属性为bw-remain"""

    bw_sum = 0
    for v in graph.neighbors(u):
        bw_sum += graph[u][v][kind]
    return bw_sum


def get_path_capacity(graph, path):
    """找到一条路径中带宽资源最小的链路并返回其带宽资源值"""

    bandwidth = 1000
    head = path[0]
    for tail in path[1:]:
        if graph[head][tail]['bw_remain'] <= bandwidth:
            bandwidth = graph[head][tail]['bw_remain']
        head = tail
    return bandwidth
