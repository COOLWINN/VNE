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

        self.algorithm_lines = ['b:', 'g--', 'y-.', 'r-']
        self.algorithm_names = ['GRC', 'MCTS', 'RL', 'ML']

        self.epoch_lines = ['b-', 'r-', 'y-', 'g-', 'c-', 'm-']
        self.epoch_types = ['50', '60', '70', '80', '90', '100']

        self.granularity_lines = ['g-', 'r--', 'b:']
        self.granularity_types = ['cpu', 'cpu, flow', 'cpu, flow, queue']

        self.multi_lines = ['g-', 'b--', 'r-.']
        self.multi_types = ['situation 1', 'situation 2', 'situation 3']

    def save_evaluations(self, evaluation, filename):
        """将一段时间内底层网络的性能指标输出到指定文件内"""

        filename = self.result_dir + filename
        with open(filename, 'w') as f:
            for time, evaluation in evaluation.metrics.items():
                f.write("%-10s\t" % time)
                f.write("%-20s\t%-20s\t%-20s\t%-20s\t%-20s\t%-20s\n" % evaluation)

    def save_network_load(self, sub, filename1, filename2):
        """将一段时间内底层网络的性能指标输出到指定文件内"""

        with open(self.result_dir + filename1, 'w') as f:
            for i in range(sub.number_of_nodes()):
                utilization = (sub.nodes[i]['cpu'] - sub.nodes[i]['cpu_remain']) / sub.nodes[i]['cpu']
                f.write("%s\n" % utilization)
        with open(self.result_dir + filename2, 'w') as f:
            for link in sub.edges:
                start, end = link[0], link[1]
                utilization = (sub[start][end]['bw'] - sub[start][end]['bw_remain']) / sub[start][end]['bw']
                f.write("%s\n" % utilization)

    def save_epoch(self, epoch, acc, runtime):
        """保存不同采样次数的实验结果"""

        filename = self.result_dir + 'epoch.txt'
        with open(filename, 'a') as f:
            f.write("%-10s\t%-20s\t%-20s\n" % (epoch, acc, runtime))

    def save_loss(self, runtime, epoch_num, loss_average):
        filename = self.result_dir + 'loss-%s.txt' % epoch_num
        with open(filename, 'w') as f:
            f.write("Training time: %s hours\n" % runtime)
            for value in loss_average:
                f.write(str(value))
                f.write('\n')

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
            results.append(self.read_result(alg + '.txt'))

        index = 0
        for metric, title in self.metric_names.items():
            index += 1
            if index == 2 or index == 3:
                continue
            plt.figure()
            for alg_id in range(len(self.algorithm_names)):
                x = results[alg_id][0]
                y = results[alg_id][index]
                plt.plot(x, y, self.algorithm_lines[alg_id], label=self.algorithm_names[alg_id])
            plt.xlim([25000, 50000])
            if metric == 'acceptance ratio':
                plt.ylim([0.7, 1])
            if metric == 'R_C':
                plt.ylim([0.55, 0.75])
            if metric == 'node utilization':
                plt.ylim([0, 0.7])
            if metric == 'link utilization':
                plt.ylim([0, 0.3])
            plt.xlabel("time", fontsize=12)
            plt.ylabel(metric, fontsize=12)
            plt.title(title, fontsize=15)
            plt.legend(loc='lower right', fontsize=12)
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
            if metric == 'acceptance ratio' or metric == 'node utilization':
                plt.ylim([0, 1])
            if metric == 'link utilization':
                plt.ylim([0, 0.5])
            plt.xlabel("time", fontsize=12)
            plt.ylabel(metric, fontsize=12)
            plt.title(title, fontsize=15)
            plt.legend(loc='lower right', fontsize=12)
            # plt.savefig(self.result_dir + metric + '.png')
        plt.show()

    def draw_result_epochs(self):
        """绘制实验结果图"""

        results = []
        for i in range(16):
            epochs = (i+1) * 10
            results.append(self.read_result('ML-VNE-%s.txt' % epochs))

        plt.figure()
        for i in range(16):
            epochs = (i + 1) * 10
            x = results[i][0]
            y = results[i][1]
            plt.plot(x, y, label=epochs)
        plt.xlim([25000, 50000])
        plt.ylim([0.6, 1])
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

    def draw_epoch(self):
        """绘制时间变化趋势图"""

        with open(self.result_dir + 'epoch.txt') as f:
            lines = f.readlines()
        epoch, acc, runtime = [], [], []
        for line in lines:
            a, b, c = [float(x) for x in line.split()]
            epoch.append(a)
            acc.append(b)
            runtime.append(c)
        runtime.sort()
        plt.plot(epoch, runtime)
        plt.xlabel("epoch", fontsize=12)
        plt.ylabel("runtime", fontsize=12)
        plt.show()

    def draw_acc(self, runtime_filename):
        """绘制时间变化趋势图"""

        with open(self.result_dir + runtime_filename) as f:
            lines = f.readlines()
        epochs, accs = [], []
        for line in lines:
            epoch, acc = [float(x) for x in line.split()]
            epochs.append(epoch)
            accs.append(acc)
        plt.plot(epochs, accs)
        plt.xlabel("epoch", fontsize=12)
        plt.ylabel("acceptance ratio", fontsize=12)
        plt.show()

    def draw_topology(self, graph, filename):
        """绘制网络拓扑图"""

        nx.draw(graph, with_labels=False, node_color='black', edge_color='gray', node_size=50)
        plt.savefig(self.result_dir + filename + '.png')
        plt.close()

    def save_distribution(self):
        """保存不同算法在各指定时刻的网络负载"""

        for i in range(5):
            index = 1000 + 200 * (i + 1) - 1
            for j in range(4):
                # 节点负载
                filename = '%s-node-%s.txt' % (self.algorithm_names[j], index)
                with open(self.result_dir + filename) as f:
                    lines = f.readlines()

                y1, y2, y3, y4, y5 = 0, 0, 0, 0, 0

                for line in lines:
                    stress = float(line)
                    if 0 <= stress <= 0.2:
                        y1 = y1 + 1
                    elif 0.2 < stress <= 0.4:
                        y2 = y2 + 1
                    elif 0.4 < stress <= 0.6:
                        y3 = y3 + 1
                    elif 0.6 < stress <= 0.8:
                        y4 = y4 + 1
                    else:
                        y5 = y5 + 1
                with open(self.result_dir + 'node-distribution-%s.txt' % index, 'a') as f:
                    f.write("%d\t%d\t%d\t%d\t%d\n" % (y1, y2, y3, y4, y5))

                # link
                filename = '%s-link-%s.txt' % (self.algorithm_names[j], index)
                with open(self.result_dir + filename) as f:
                    lines = f.readlines()
                y1, y2, y3, y4, y5 = 0, 0, 0, 0, 0
                for line in lines:
                    stress = float(line)
                    if 0 <= stress <= 0.2:
                        y1 = y1 + 1
                    elif 0.2 < stress <= 0.4:
                        y2 = y2 + 1
                    elif 0.4 < stress <= 0.6:
                        y3 = y3 + 1
                    elif 0.6 < stress <= 0.8:
                        y4 = y4 + 1
                    else:
                        y5 = y5 + 1
                with open(self.result_dir + 'link-distribution-%s.txt' % index, 'a') as f:
                    f.write("%d\t%d\t%d\t%d\t%d\n" % (y1, y2, y3, y4, y5))


if __name__ == '__main__':
    analysis = Analysis('results_new/')
    analysis.save_distribution()
