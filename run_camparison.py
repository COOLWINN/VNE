from analysis import Analysis
from algorithm import Algorithm


if __name__ == '__main__':

    names = ['RL', 'GRC', 'MCTS']
    tool = Analysis('results_algorithm/')
    for i in range(3):
        algorithm = Algorithm(names[i])
        runtime = algorithm.execute(network_path='networks/',
                                    sub_filename='sub-wm.txt')
        tool.save_evaluations(algorithm.evaluation, '%s-VNE.txt' % names[i])
        print(runtime)
