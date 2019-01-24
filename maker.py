import math
import random
import os
import copy
import numpy as np
import networkx as nx

# 仿真时间
TOTAL_TIME = 50000

SCALE = 100

# 仅与虚拟网络请求相关的参数
DURATION_MEAN = 1000
MIN_DURATION = 250
MAX_DISTANCE = 20

# itm和sgb2alt指令的绝对路径
itm = '/home/kuso/ns-2.35/gt-itm/bin/itm'
sgb2alt = '/home/kuso/ns-2.35/gt-itm/bin/sgb2alt'

# 生成文件的存放目录
spec_dir = 'generated/spec/'
alt_dir = 'generated/alt/'
save_path = 'networks/'
if not os.path.exists(spec_dir):
    os.makedirs(spec_dir)
if not os.path.exists(alt_dir):
    os.makedirs(alt_dir)
if not os.path.exists(save_path):
    os.makedirs(save_path)


def calculate_dis(coordinate1, coordinate2):
    """给定两个节点坐标，求解它们之间的欧氏距离"""
    return math.sqrt(pow(coordinate1[0] - coordinate2[0], 2) + pow(coordinate1[1] - coordinate2[1], 2))


def generate_network(network_name, min_res, max_res, time=0, duration=0, transit_nodes=0):
    """生成网络文件"""

    # Step1: 执行itm指令生成.gb文件
    spec_filename = 'spec-%s' % network_name
    cmd = "%s %s" % (itm, spec_dir + spec_filename)
    os.system(cmd)

    # Step2: 执行sgb2alt指令将刚刚生成的gb文件转换为alt文件
    gb_filename = spec_filename + '-0.gb'
    alt_filename = '%s.alt' % network_name
    cmd = "%s %s %s" % (sgb2alt, spec_dir + gb_filename, alt_dir + alt_filename)
    os.system(cmd)

    # Step3: 读取刚刚生成的alt文件
    with open(alt_dir + alt_filename) as f:
        lines = f.readlines()

    # Step4: 生成网络文件
    print("generate %s" % network_name)
    network_filename = '%s.txt' % network_name
    with open(save_path + network_filename, 'w') as network_file:

        coordinates = []

        # Step4-1: 写入网络整体信息
        line_one = lines[1].split()
        num_nodes = int(line_one[0])
        num_edges = int(int(line_one[1]) / 2)
        if network_name == 'sub-wm' or network_name == 'sub-ts':
            # 物理拟网络信息包括：节点数量、链路数量
            network_file.write("%d %d\n" % (num_nodes, num_edges))
        else:
            # 虚拟网络信息包括：节点数量、链路数量、到达时间、持续时间、可映射范围
            network_file.write("%d %d %d %d %d\n" % (num_nodes, num_edges, time, duration, MAX_DISTANCE))

        # Step4-2: 依次写入节点信息（x坐标，y坐标，节点资源）
        for line in lines[4:4 + num_nodes]:
            blocks = line.split()
            x = int(blocks[2])
            y = int(blocks[3])
            coordinates.append((x, y))
            resource = random.uniform(min_res, max_res)
            if network_name == 'sub-ts' and len(coordinates) <= transit_nodes:
                network_file.write("%d %d %f\n" % (x, y, 200 + resource))
                continue
            network_file.write("%d %d %f\n" % (x, y, resource))

        # Step4-3: 依次写入链路信息（起始节点，终止节点，带宽资源，时延）
        for line in lines[-num_edges:]:
            from_id, to_id, length, a = [int(x) for x in line.split()]
            distance = calculate_dis(coordinates[from_id], coordinates[to_id])
            resource = random.uniform(min_res, max_res)
            if network_name == 'sub-ts':
                if from_id < transit_nodes and to_id < transit_nodes:
                    network_file.write("%d %d %f %f\n" % (from_id, to_id, 200 + resource, distance))
                    continue
                if from_id < transit_nodes or to_id < transit_nodes:
                    network_file.write("%d %d %f %f\n" % (from_id, to_id, 100 + resource, distance))
                    continue
            network_file.write("%d %d %f %f\n" % (from_id, to_id, resource, distance))


def make_sub_wm(nodes_number, connect_prob, min_res, max_res):
    """生成物理网络文件（基于waxman随机型网络模型）"""

    network_name = 'sub-wm'

    # 生成GT-ITM配置文件
    spec_filename = 'spec-%s' % network_name
    with open(spec_dir + spec_filename, 'w') as f:
        f.write("geo 1\n")
        f.write("%d %d 2 %f 0.2\n" % (nodes_number, SCALE, connect_prob))

    # 生成基于Waxman随机模型的物理网络文件
    generate_network(network_name, min_res, max_res)


# transits： transit域数量
# stubs: 每个transit节点连接的stub域数量
# transit_nodes: 每个transit域中节点数量
# transit_p: transit域内的连通性
# stub_nodes: 每个stub域中节点数量
# stub_p: stub域内的连通性
def make_sub_ts(transits, stubs, transit_nodes, transit_p, stub_nodes, stub_p, min_res, max_res):
    """生成物理网络文件（基于Transit-Stub模型）"""

    network_name = 'sub-ts'

    # Step1: 生成GT-ITM配置文件
    spec_filename = 'spec-%s' % network_name
    with open(spec_dir + spec_filename, 'w') as f:
        f.write("ts 1 47\n")
        f.write("%d 0 0\n" % stubs)
        f.write("%d 2 3 1.0\n" % transits)
        f.write("%d 5 3 %f\n" % (transit_nodes, transit_p))
        f.write("%d 5 3 %f\n" % (stub_nodes, stub_p))

    # 生成基于transit-stub模型的物理网络文件
    generate_network('sub-ts', min_res, max_res, transit_nodes=transit_nodes)


def make_req(index, min_res, max_res, node_amount, time, duration):
    """生成虚拟网络请求文件"""

    network_name = 'req%d' % index

    # 生成GT-ITM配置文件
    spec_filename = 'spec-%s' % network_name
    with open(spec_dir + spec_filename, 'w') as f:
        f.write("geo 1\n")
        f.write("%d %d 2 0.5 0.2\n" % (node_amount, SCALE))

    # 生成虚拟网络文件
    generate_network(network_name, min_res, max_res, time=time, duration=duration)


# possion_mean：虚拟网络请求的到达服从泊松分布，且平均每1000个时间单位内到达的数量为possion_mean个
# 虚拟节点数量服从[min_num_nodes, max_num_nodes]的均匀分布
def make_batch_req(possion_mean, min_num_nodes, max_num_nodes, min_res, max_res):
    """生成多个虚拟网络请求文件"""

    # 时间间隔
    interval = 1000
    # 虚拟网络请求数量
    req_num = int(possion_mean / interval * TOTAL_TIME)
    # 在一个时间间隔内到达的VNR数量
    k = 0
    # 记录该时间间隔内已到达的VNR数量
    count_k = 0
    # 记录已经经历了多少个时间间隔
    p = 0
    # 每个时间间隔的起始时间
    start = 0

    # 按照以下步骤分别生成req_num个虚拟网络请求文件
    for i in range(req_num):

        if count_k == k:
            k = 0
            while k == 0:
                k = np.random.poisson(possion_mean)
            count_k = 0
            start = p * interval
            p += 1
        count_k += 1

        time = start + ((count_k + 1) / (k + 1)) * interval
        duration = MIN_DURATION + int(-math.log(random.random()) * (DURATION_MEAN - MIN_DURATION))
        node_amount = random.randint(min_num_nodes, max_num_nodes)
        make_req(i, min_res, max_res, node_amount, time, duration)


def extract_network(path, filename):
    """读取网络文件并生成networkx.Graph实例"""

    node_id, link_id = 0, 0

    with open(path + filename) as f:
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

        node_num, link_num, time, duration, max_dis = [int(x) for x in lines[0].split()]
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


def simulate_events(path, number):
    """读取number个虚拟网络，构成虚拟网络请求事件队列"""

    queue = []
    for i in range(number):
        filename = 'req%d.txt' % i
        vnr_arrive = extract_network(path, filename)
        vnr_arrive.graph['id'] = i
        vnr_leave = copy.deepcopy(vnr_arrive)
        vnr_leave.graph['type'] = 1
        vnr_leave.graph['time'] = vnr_arrive.graph['time'] + vnr_arrive.graph['duration']
        queue.append(vnr_arrive)
        queue.append(vnr_leave)

    # 按照时间（到达时间或离开时间）对这些虚拟网络请求从小到大进行排序
    queue.sort(key=lambda r: r.graph['time'])

    return queue


if __name__ == '__main__':
    # 生成节点数为100，连通率为0.5的随机型物理网络
    # make_sub_wm(100, 0.5, 50, 100)

    # 生成节点数为1×4×(1+3×8)=100，连通率为0.5的Transit-Stub型物理网络
    make_sub_ts(1, 3, 4, 0.5, 8, 0.5, 50, 100)

    # 平均每1000个时间单位内到达40个虚拟网络请求， 且虚拟节点数服从3~20的均匀分布，请求资源服从0~50的均匀分布
    # make_batch_req(40, 3, 20, 0, 50)
