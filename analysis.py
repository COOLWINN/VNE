import os
import networkx as nx
import matplotlib.pyplot as plt


class Analysis:

    def __init__(self, result_dir):

        self.result_dir = result_dir
        if not os.path.exists(self.result_dir):
            os.makedirs(self.result_dir)

        self.metric_names = {'acceptance ratio': 'Acceptance Ratio',
                             'average revenue': 'Long Term Average Revenue',
                             'average cost': 'Long Term Average Cost',
                             'R_C': 'Long Term Revenue/Cost Ratio',
                             'node utilization': 'Average Node Utilization',
                             'link utilization': 'Average Link Utilization'}

        self.algorithm_lines = ['b:', 'r--', 'y-.', 'g-']
        self.algorithm_names = ['GRC-VNE', 'MCTS-VNE', 'RL-VNE', 'ML-VNE']

        self.epoch_lines = ['b-', 'r-', 'y-', 'g-', 'c-', 'm-']
        self.epoch_types = ['50', '60', '70', '80', '90', '100']

        self.granularity_lines = ['g-', 'r--', 'b:']
        self.granularity_types = ['cpu', 'cpu, flow', 'cpu, flow, queue']

        self.multi_lines = ['b--', 'r-.', 'g-']
        self.multi_types = ['situation 1', 'situation 2', 'situation 3']

    def save_result(self, evaluation, filename):
        """将一段时间内底层网络的性能指标输出到指定文件内"""

        filename = self.result_dir + filename
        with open(filename, 'w') as f:
            for time, evaluation in evaluation.metrics.items():
                f.write("%-10s\t" % time)
                f.write("%-20s\t%-20s\t%-20s\t%-20s\t%-20s\t%-20s\n" % evaluation)

    def save_runtime(self, node_arg, runtime):
        """将算法的运行时间输出到指定文件内"""

        filename = self.result_dir + 'time.txt'
        with open(filename, 'a') as f:
            f.write("%-10s\t%-20s\n" % (node_arg, runtime))

    def read_result(self, filename):
        """读取结果文件"""

        with open(self.result_dir + filename) as f:
            lines = f.readlines()

        t, acceptance, revenue, cost, r_to_c, node_stress, link_stress = [], [], [], [], [], [], []
        for line in lines:
            a, b, c, d, e, f, g = [float(x) for x in line.split()]
            t.append(a)
            acceptance.append(b)
            revenue.append(c / a)
            cost.append(d / a)
            r_to_c.append(e)
            node_stress.append(f)
            link_stress.append(g)

        return t, acceptance, revenue, cost, r_to_c, node_stress, link_stress

    def draw_result_algorithms(self):
        """绘制实验结果图"""

        results = []
        for alg in self.algorithm_names:
            # if alg == 'MCTS-VNE':
            #     results.append(self.read_result('ML-VNE-simple.txt'))
            # elif alg == 'ML-VNE-simple':
            #     results.append(self.read_result('MCTS-VNE-old.txt'))
            # else:
            #     results.append(self.read_result(alg + '.txt'))
            results.append(self.read_result(alg + '.txt'))

        index = 0
        for metric, title in self.metric_names.items():
            index += 1
            plt.figure()
            for alg_id in range(len(self.algorithm_names)):
                x = results[alg_id][0]
                y = results[alg_id][index]
                plt.plot(x, y, self.algorithm_lines[alg_id], label=self.algorithm_names[alg_id])
            plt.xlim([25000, 50000])
            # if metric == 'acceptance ratio' or metric == 'node utilization' or metric == 'link utilization':
            #     plt.ylim([0, 1])
            plt.ylim([0, 0.5])
            plt.xlabel("time", fontsize=12)
            plt.ylabel(metric, fontsize=12)
            plt.title(title, fontsize=15)
            plt.legend(loc='best', fontsize=12)
            # plt.savefig(self.result_dir + metric + '.png')
        plt.show()

    def draw_result_granularity(self):
        """绘制实验结果图"""

        results = []
        for i in range(3):
            results.append(self.read_result('ML-VNE-%d.txt' % (i+1)))

        index = 0
        for metric, title in self.metric_names.items():
            index += 1
            plt.figure()
            for i in range(3):
                x = results[i][0]
                y = results[i][index]
                plt.plot(x, y, self.granularity_lines[i], label=self.granularity_types[i])
            plt.xlim([25000, 50000])
            if metric == 'acceptance ratio' or metric == 'node utilization' or metric == 'link utilization':
                plt.ylim([0, 1])
            # plt.ylim([0, 0.5])
            plt.xlabel("time", fontsize=12)
            plt.ylabel(metric, fontsize=12)
            plt.title(title, fontsize=15)
            plt.legend(loc='lower right', fontsize=12)
            # plt.savefig(self.result_dir + metric + '.png')
        plt.show()

    def draw_result_epochs(self):
        """绘制实验结果图"""

        results = []
        for i in range(6):
            epochs = (i+5) * 10
            results.append(self.read_result('ML-VNE-%s.txt' % epochs))

        plt.figure()
        for i in range(6):
            x = results[i][0]
            y = results[i][1]
            plt.plot(x, y, self.epoch_lines[i], label=self.epoch_types[i])
        plt.xlim([25000, 50000])
        plt.ylim([0.5, 1])
        plt.xlabel("time", fontsize=12)
        plt.ylabel("acceptance ratio", fontsize=12)
        plt.title("Acceptance Ratio", fontsize=15)
        plt.legend(loc='best', fontsize=12)
        # plt.savefig(self.result_dir + metric + '.png')
        plt.show()

    def draw_result_multi(self):
        """绘制实验结果图"""

        results = []
        for i in range(3):
            index = (i+1) * 1000
            results.append(self.read_result('ML-VNE-%s.txt' % index))

        plt.figure()
        for i in range(3):
            x = results[i][0]
            y = results[i][1]
            plt.plot(x, y, self.multi_lines[i], label=self.multi_types[i])
        plt.xlim([0, 50000])
        plt.ylim([0, 1])
        plt.xlabel("time", fontsize=12)
        plt.ylabel("acceptance ratio", fontsize=12)
        plt.title("Acceptance Ratio", fontsize=15)
        plt.legend(loc='lower right', fontsize=12)
        # plt.savefig(self.result_dir + metric + '.png')
        plt.show()

    def draw_loss(self, loss_filename):
        """绘制loss变化趋势图"""

        with open(self.result_dir + loss_filename) as f:
            lines = f.readlines()
        loss = []
        for line in lines[1:]:
            loss.append(float(line))
        plt.plot(loss)
        plt.show()

    def draw_runtime(self, runtime_filename):
        """绘制时间变化趋势图"""

        with open(self.result_dir + runtime_filename) as f:
            lines = f.readlines()
        epochs, runtimes = [], []
        for line in lines:
            epoch, runtime = [float(x) for x in line.split()]
            epochs.append(epoch)
            runtimes.append(runtime)
        plt.plot(epochs, runtimes)
        plt.xlabel("epoch", fontsize=12)
        plt.ylabel("runtime", fontsize=12)
        plt.show()

    def draw_topology(self, graph, filename):
        """绘制网络拓扑图"""

        nx.draw(graph, with_labels=False, node_color='black', edge_color='gray', node_size=50)
        plt.savefig(self.result_dir + filename + '.png')
        plt.close()


if __name__ == '__main__':
    analysis = Analysis('results_multi/')
    analysis.draw_result_multi()
