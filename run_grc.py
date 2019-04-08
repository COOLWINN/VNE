from algorithm import Algorithm
from analysis import Analysis

if __name__ == '__main__':

    tool = Analysis('results_algorithm/')
    name = 'GRC'
    algorithm = Algorithm(name)
    runtime = algorithm.execute(network_path='networks/',
                                sub_filename='sub-wm.txt',
                                req_num=1000)
    tool.save_evaluations(algorithm.evaluation, '%s-1.txt' % name)
    print(runtime)
