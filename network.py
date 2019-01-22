import math
import random
import os
import numpy as np

POISSON_MEAN = 40
TOTAL_TIME = 50000
NUM_REQ = 2000

SCALE = 100
MAX_DISTANCE = 20

MAX_CPU = 100
MAX_BW = 100

DURATION_MEAN = 1000
MIN_DURATION = 250

MIN_NUM_NODE = 3
MAX_NUM_NODE = 20

itm = '/home/kuso/ns-2.35/gt-itm/bin/itm'
sgb2alt = '/home/kuso/ns-2.35/gt-itm/bin/sgb2alt'

spec_dir = 'generated/spec'
alt_dir = 'generated/alt'
req_dir = 'requests'
if not os.path.exists(spec_dir):
    os.makedirs(spec_dir)
if not os.path.exists(alt_dir):
    os.makedirs(alt_dir)
if not os.path.exists(req_dir):
    os.makedirs(req_dir)


def dis(x1, y1, x2, y2):
    return math.sqrt(pow(x1 - x2, 2) + pow(y1 - y2, 2))


def make_sub(nodes_number, connect_prob):
    """生成物理网络文件（基于随机型网络模型）"""

    x_coordinates, y_coordinates = [], []
    filename = "generated/itm-specsub"
    with open(filename, 'w') as f:
        f.write("geo 1\n")
        f.write("%d %d 2 %f 0.2\n" % (nodes_number, SCALE, connect_prob))

    cmd = "%s %s" % (itm, filename)
    os.system(cmd)
    gb_path = "generated/itm-specsub-0.gb"
    alt_path = "generated/sub.alt"
    cmd = "%s %s %s" % (sgb2alt, gb_path, alt_path)
    os.system(cmd)

    with open(alt_path) as f:
        lines = f.readlines()

    a, b, c, d = [x for x in lines[1].split()]
    num_nodes = int(a)
    num_edges = int(int(b) / 2)

    sub_filename = "requests/sub.txt"
    with open(sub_filename, 'w') as sub_file:
        sub_file.write("%d %d\n" % (num_nodes, num_edges))

        # 依次写入节点信息（x坐标，y坐标，拥有的节点资源）
        for line in lines[4:4 + num_nodes]:
            t1, t2, x, y = [int(x) for x in line.split()]
            x_coordinates.append(x)
            y_coordinates.append(y)
            resource = random.uniform(1, 2) * MAX_CPU * 0.5
            sub_file.write("%d %d %f\n" % (x, y, resource))

        # 依次写入链路信息（起始节点，终止节点，拥有的带宽资源，长度）
        for line in lines[-num_edges:]:
            from_id, to_id, length, a = [int(x) for x in line.split()]
            resource = random.uniform(1, 2) * MAX_BW * 0.5
            distance = dis(x_coordinates[from_id], y_coordinates[from_id],
                           x_coordinates[to_id], y_coordinates[to_id])
            sub_file.write("%d %d %f %f\n" % (from_id, to_id, resource, distance))


# transits： transit域数量
# stubs: 每个transit节点连接的stub域数量
# transit_nodes: 每个transit域中节点数量
# transit_p: transit域内的连通性
# stub_nodes: 每个stub域中节点数量
# stub_p: stub域内的连通性
def make_sub_ts(transits, stubs, transit_nodes, transit_p, stub_nodes, stub_p):
    """生成物理网络文件（基于Transit-Stub模型）"""

    x_coordinates, y_coordinates = [], []
    filename = "generated/itm-specsub-ts"
    with open(filename, 'w') as f:
        f.write("ts 1 47\n")
        f.write("%d 0 0\n" % stubs)
        f.write("%d 2 3 1.0\n" % transits)
        f.write("%d 5 3 %f\n" % (transit_nodes, transit_p))
        f.write("%d 5 3 %f\n" % (stub_nodes, stub_p))

    cmd = "%s %s" % (itm, filename)
    os.system(cmd)
    gb_path = "generated/itm-specsub-ts-0.gb"
    alt_path = "generated/sub-ts.alt"
    cmd = "%s %s %s" % (sgb2alt, gb_path, alt_path)
    os.system(cmd)

    with open(alt_path) as f:
        lines = f.readlines()

    a, b, c, d, e, f, g = [x for x in lines[1].split()]
    num_nodes = int(a)
    num_edges = int(int(b) / 2)

    sub_filename = "requests/sub-ts.txt"
    with open(sub_filename, 'w') as sub_file:
        sub_file.write("%d %d\n" % (num_nodes, num_edges))

        count = 0
        # 依次写入节点信息（x坐标，y坐标，拥有的节点资源）
        for line in lines[4:4 + num_nodes]:
            count += 1
            t1, t2, x, y = [x for x in line.split()]
            x = int(x)
            y = int(y)
            x_coordinates.append(x)
            y_coordinates.append(y)
            resource = random.uniform(1, 2) * MAX_CPU * 0.5
            if count <= 4:
                sub_file.write("%d %d %f\n" % (x, y, 200 + resource))
            else:
                sub_file.write("%d %d %f\n" % (x, y, resource))

        # 依次写入链路信息（起始节点，终止节点，拥有的带宽资源，长度）
        for line in lines[-num_edges:]:
            from_id, to_id, length, a = [int(x) for x in line.split()]
            resource = random.uniform(1, 2) * MAX_BW * 0.5
            distance = dis(x_coordinates[from_id], y_coordinates[from_id],
                           x_coordinates[to_id], y_coordinates[to_id])
            if from_id < 4 and to_id < 4:
                sub_file.write("%d %d %f %f\n" % (from_id, to_id, 200 + resource, distance))
            elif from_id < 4 or to_id < 4:
                sub_file.write("%d %d %f %f\n" % (from_id, to_id, 100 + resource, distance))
            else:
                sub_file.write("%d %d %f %f\n" % (from_id, to_id, resource, distance))


def make_req(req_num, max_node_resource, max_link_resource):
    """生成虚拟网络请求文件"""

    count_k, k = 0, 0
    p, start = 0, 0
    x_coordinates, y_coordinates = [], []

    # 生成GT-ITM配置文件
    for i in range(req_num):
        filename = '%s/itm-spec%d' % (spec_dir, i)
        with open(filename, 'w') as f:
            f.write("geo 1\n")
            t = MIN_NUM_NODE + random.randint(0, MAX_NUM_NODE - MIN_NUM_NODE)
            f.write("%d %d 2 0.5 0.2\n" % (t, SCALE))

    for i in range(req_num):
        # 执行itm指令生成gb文件
        cmd = "%s %s/itm-spec%d" % (itm, spec_dir, i)
        os.system(cmd)

        # 通过执行sgb2alt指令将gb文件转换为alt文件
        cmd = '%s %s/itm-spec%d-0.gb %s/%d.alt' % (sgb2alt, spec_dir, i, alt_dir, i)
        os.system(cmd)

    interval = POISSON_MEAN * TOTAL_TIME / req_num

    # 生成虚拟网络请求文件
    for i in range(req_num):
        print("generate req%d" % i)
        with open('%s/%d.alt' % (alt_dir, i)) as f:
            lines = f.readlines()

        req_filename = "%s/req%d.txt" % (req_dir, i)
        with open(req_filename, 'w') as req_file:

            a, b, c, d = [x for x in lines[1].split()]
            num_nodes = int(a)
            num_edges = int(int(b) / 2)

            if count_k == k:
                k = 0
                while k == 0:
                    k = np.random.poisson(POISSON_MEAN)
                count_k = 0
                start = p * interval
                p += 1
            count_k += 1

            # 虚拟网络请求的到达时间
            time = start + ((count_k + 1) / (k + 1)) * interval

            # 虚拟网络请求的持续时间服从指数分布
            duration = MIN_DURATION + int(-math.log(random.random()) * (DURATION_MEAN - MIN_DURATION))

            # 写入虚拟网络请求整体信息（节点数量、链路数量、到达时间、持续时间、映射范围）
            req_file.write("%d %d %d %d %d\n" % (num_nodes, num_edges, time, duration, MAX_DISTANCE))

            # 依次写入节点信息（x坐标，y坐标，请求的节点资源）
            for line in lines[4:4 + num_nodes]:
                t1, t2, x, y = [int(x) for x in line.split()]
                x_coordinates.append(x)
                y_coordinates.append(y)
                resource = random.random() * max_node_resource
                req_file.write("%d %d %f\n" % (x, y, resource))

            # 依次写入链路信息（起始节点，终止节点，请求的带宽资源，时延）
            for line in lines[-num_edges:]:
                from_id, to_id, length, a = [int(x) for x in line.split()]
                resource = random.random() * max_link_resource
                delay = 1 + random.random() * dis(x_coordinates[from_id], y_coordinates[from_id],
                                                  x_coordinates[to_id], y_coordinates[to_id])
                req_file.write("%d %d %f %f\n" % (from_id, to_id, resource, delay))


if __name__ == '__main__':
    make_sub_ts(1, 3, 4, 0.5, 8, 0.5)
    make_req(NUM_REQ, 50, 50)
