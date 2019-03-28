import time
from network import Network
from analysis import Analysis
from algorithm import Algorithm
from queue import PriorityQueue as PQ
from event import Event


def main():

    # Step1: 读取底层网络和虚拟网络请求文件
    network_files_dir = 'networks-multi/'
    sub_filename = 'sub-wm.txt'
    networks = Network(network_files_dir)
    sub, requests, child_requests = networks.get_networks(sub_filename, req_num=400, child_req_num=4)
    events = PQ()
    for req in requests:
        events.put(Event(req))
    for child in child_requests:
        events.put(Event(child))

    # Step2: 配置映射算法
    node_arg = 50
    algorithm = Algorithm('ml', node_arg=node_arg, link_arg=5)
    algorithm.configure(sub)

    # Step3: 处理虚拟网络请求事件
    start = time.time()
    algorithm.handle(sub, events, requests)
    time_cost = time.time() - start
    print(time_cost)

    # Step4: 输出映射结果文件
    tool = Analysis('results_multi/')
    tool.save_result(algorithm.evaluation, 'ML-VNE-300.txt')


if __name__ == '__main__':
    main()
