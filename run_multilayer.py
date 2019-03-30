import time
from network import Network
from analysis import Analysis
from algorithm import Algorithm
from queue import PriorityQueue
from event import Event
import tensorflow as tf


def main():

    # Step1: 读取底层网络和虚拟网络请求文件
    network_files_dir = 'networks-multi/'
    sub_filename = 'sub-wm.txt'
    networks = Network(network_files_dir)
    sub, requests, child_requests = networks.get_networks(sub_filename, req_num=400, child_req_num=0)
    print(len(child_requests))
    events = PriorityQueue()
    for req in requests:
        events.put(Event(req))
    for child in child_requests:
        events.put(Event(child))

    start = time.time()
    with tf.Session() as sess:
        # Step2: 配置映射算法
        node_arg = 50
        algorithm = Algorithm('ml', node_arg=node_arg, link_arg=5)
        algorithm.configure(sub, sess)
        # Step3: 依次处理虚拟网络请求事件
        algorithm.handle(sub, events, requests)
    runtime = time.time() - start
    print(runtime)

    # Step4: 输出映射结果文件
    tool = Analysis('results_multi/')
    tool.save_evaluations(algorithm.evaluation, 'ML-VNE-1000.txt')


if __name__ == '__main__':
    main()
