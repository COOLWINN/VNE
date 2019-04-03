from analysis import Analysis
from algorithm import Algorithm

if __name__ == '__main__':

    result_dir = 'results_epoch/'
    tool = Analysis(result_dir)
    for i in range(100):
        epoch = (i + 1) * 10
        algorithm = Algorithm('ML', result_dir, node_arg=epoch, link_method=5)
        runtime = algorithm.execute(network_path='networks/',
                                    sub_filename='sub-wm.txt')
        tool.save_evaluations(algorithm.evaluation, '%s.txt' % epoch)
        tool.save_epoch(epoch, algorithm.evaluation.acc_ratio, runtime)
