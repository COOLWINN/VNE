from analysis import Analysis
from algorithm import Algorithm


if __name__ == '__main__':
    tool = Analysis('results_granularity/')
    for i in range(3):
        granularity = i + 1
        algorithm = Algorithm('ML%d' % granularity, node_arg=50, link_arg=5)
        algorithm.execute(network_path='networks/',
                          sub_filename='sub-wm.txt',
                          granularity=granularity)
        tool.save_result(algorithm.evaluation, '%s.txt' % granularity)
