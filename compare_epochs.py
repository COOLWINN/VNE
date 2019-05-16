from analysis import Analysis
from algorithm import Algorithm

if __name__ == '__main__':

    tool = Analysis('results_epoch_new/')
    for i in range(20):
        epoch = (i + 1) * 10
        algorithm = Algorithm(name='ML', param=epoch)
        runtime = algorithm.execute(network_path='networks/',
                                    sub_filename='sub-wm.txt',
                                    req_num=2000)
        tool.save_evaluations(algorithm.evaluation, '%s.txt' % epoch)
        tool.save_epoch(epoch, algorithm.evaluation.acc_ratio, runtime)
