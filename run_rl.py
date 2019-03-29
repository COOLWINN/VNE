from algorithm import Algorithm
from analysis import Analysis

if __name__ == '__main__':
    tool = Analysis('results_ts/')
    name = 'RL'
    algorithm = Algorithm(name, node_arg=100, link_arg=5)
    runtime = algorithm.execute(network_path='networks/',
                                sub_filename='sub-ts.txt')
    tool.save_result(algorithm.evaluation, '%s-VNE.txt' % name)
    print(runtime)
