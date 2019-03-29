from algorithm import Algorithm
from analysis import Analysis


if __name__ == '__main__':

    tool = Analysis('results_algorithm/')
    name = 'MCTS'
    algorithm = Algorithm(name, link_arg=1)
    runtime = algorithm.execute(network_path='networks/',
                                sub_filename='sub-wm.txt')
    tool.save_result(algorithm.evaluation, '%s-VNE.txt' % name)
    print(runtime)
