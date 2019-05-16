from analysis import Analysis
from algorithm import Algorithm


if __name__ == '__main__':

    tool = Analysis('results_multi_new/')
    name = 'ML'
    algorithm = Algorithm(name, param=120)
    runtime = algorithm.execute(network_path='networks-multi/',
                                sub_filename='sub-wm.txt',
                                req_num=400,
                                child_num=4)
    tool.save_evaluations(algorithm.evaluation, 'ML-VNE-1000.txt')
    print(runtime)
