import copy
import time
from network import Network
from analysis import Analysis
from algorithm import Algorithm
from queue import PriorityQueue
from event import Event
import tensorflow as tf


def main():

    # Step1: 读取底层网络和虚拟网络请求文件
    results_dir = 'results_epoch/'
    tool = Analysis(results_dir)

    network_files_dir = 'networks/'
    sub_filename = 'sub-wm.txt'
    networks = Network(network_files_dir)
    substrate, requests = networks.get_networks_single_layer(sub_filename, 1000)

    for i in range(100):

        # Step1: 数据准备
        sub = copy.deepcopy(substrate)
        events = PriorityQueue()
        for req in requests:
            events.put(Event(req))

        start = time.time()
        tf.reset_default_graph()
        with tf.Session() as sess:
            # Step2: 配置映射算法
            node_arg = (i + 1) * 10
            algorithm = Algorithm('ML', node_arg=node_arg, link_arg=5)
            algorithm.configure(sub, sess)
            # Step3: 处理虚拟网络请求事件
            acc = algorithm.handle(sub, events)
        tf.get_default_graph().finalize()
        runtime = time.time() - start

        # Step4: 统计映射结果
        tool.save_epoch(node_arg, acc, runtime)
        tool.save_result(algorithm.evaluation, '%s.txt' % node_arg)


if __name__ == '__main__':
    main()
