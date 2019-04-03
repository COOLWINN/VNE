from algorithm import Algorithm
from analysis import Analysis

if __name__ == '__main__':
    result_dir = 'results_algorithm/'
    tool = Analysis(result_dir)
    name = 'MCTS'
    algorithm = Algorithm(name, result_dir, link_method=1)
    runtime = algorithm.execute(network_path='networks/',
                                sub_filename='sub-wm.txt',
                                req_num=1000)
    tool.save_evaluations(algorithm.evaluation, '%s-VNE.txt' % name)
    print(runtime)
