from algorithm import Algorithm
from analysis import Analysis


if __name__ == '__main__':

    tool = Analysis('results_ts/')
    algorithm = Algorithm('GRC', link_arg=1)
    runtime = algorithm.execute(network_path='networks/',
                                sub_filename='sub-ts.txt')
    tool.save_result(algorithm.evaluation, '%s-VNE.txt' % 'GRC')
    print(runtime)
