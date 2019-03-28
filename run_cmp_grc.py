import time
from network import Network
from analysis import Analysis
from algorithm import Algorithm
from queue import PriorityQueue as PQ
from event import Event


def main():

    # Step1: 读取底层网络和虚拟网络请求文件
    network_files_dir = 'networks/'
    sub_filename = 'sub-wm.txt'
    networks = Network(network_files_dir)
    sub, requests = networks.get_networks_single_layer(sub_filename, 1000)
    events = PQ()
    for req in requests:
        events.put(Event(req))

    # Step2: 配置映射算法
    name = 'grc'
    algorithm = Algorithm(name, link_arg=1)
    algorithm.configure(sub)

    # Step3: 处理虚拟网络请求事件
    start = time.time()
    algorithm.handle(sub, events, requests)
    time_cost = time.time() - start
    print(time_cost)

    # Step4: 输出映射结果文件
    tool = Analysis('results_single/')
    tool.save_result(algorithm.evaluation, 'GRC-VNE-0328.txt')


if __name__ == '__main__':
    main()
