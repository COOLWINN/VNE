import tensorflow as tf
import numpy as np
from .my_mdp2 import MyEnv
from .model2 import Pnetwork
import networkx as nx
from network import Network


class Agent2:

    def __init__(self, action_num, feature_num, learning_rate, reward_decay, episodes):
        self.action_num = action_num
        self.p_network = Pnetwork(action_num, feature_num, learning_rate)
        self.gamma = reward_decay
        self.episodes = episodes
        self.ep_obs, self.ep_as, self.ep_rs = [], [], []
        self.sess = tf.Session()
        self.sess.run(tf.global_variables_initializer())

    def train(self, sub, vnr):
        """通过蒙特卡洛采样不断尝试映射该虚拟网络请求，以获得效果最佳的策略网络"""

        # 初始化环境
        env = MyEnv(sub, vnr)

        for i_episode in range(self.episodes):
            print('Iteration %s' % i_episode)
            # 重置VNE环境
            observation = env.reset()

            tmp_node_map = {}

            # 采样
            for count in range(vnr.number_of_nodes()):
                action = self.choose_action(self.p_network, observation, sub, vnr.nodes[count]['cpu'], vnr.nodes[count]['flow'])
                if action == -1:
                    break
                else:
                    observation_, reward, done, info = env.step(action)
                    self.store_transition(observation, action, reward)
                    tmp_node_map.update({count: action})

                    # after each step, we should update the observation
                    observation = observation_

            if len(tmp_node_map) == vnr.number_of_nodes():
                reward = self.calculate_reward(sub, vnr, tmp_node_map)
                if reward != -1:
                    vt = self.learn(self.p_network, reward)

        print("\nFinish training!\n")
        return env

    def run(self, sub, vnr):
        """使用训练好的策略网络映射虚拟节点"""

        env = self.train(sub, vnr)
        observation = env.reset()
        node_map = {}
        chosen_nodes = []
        for count in range(vnr.number_of_nodes()):
            action = self.choose_best_action(self.p_network, observation, sub, vnr.nodes[count]['cpu'], vnr.nodes[count]['flow'], chosen_nodes)
            if action == -1:
                break
            else:
                if sub.nodes[action]['cpu_remain'] < vnr.nodes[count]['cpu'] and sub.nodes[action]['flow_remain'] < vnr.nodes[count]['flow']:
                    pass
                observation_, _, done, info = env.step(action)
                chosen_nodes.append(action)
                node_map.update({count: action})

                # 每执行一个step，都需要更新环境状态
                observation = observation_

        return node_map

    def choose_action(self, model, observation, sub, current_node_cpu, current_node_flow):

        x = np.reshape(observation, [1, observation.shape[0], observation.shape[1], 1])
        prob_weights = self.sess.run(model.scores, feed_dict={model.tf_obs: x})

        candidate_action = []
        candidate_score = []
        for index, score in enumerate(prob_weights.ravel()):
            if index not in self.ep_as and sub.nodes[index]['cpu_remain'] >= current_node_cpu and sub.nodes[index]['flow_remain'] >= current_node_flow:
                candidate_action.append(index)
                candidate_score.append(score)
        if len(candidate_action) == 0:
            return -1
        else:
            candidate_prob = np.exp(candidate_score) / np.sum(np.exp(candidate_score))
            # 选择动作
            action = np.random.choice(candidate_action, p=candidate_prob)
            return action

    def choose_best_action(self, model, observation, sub, current_node_cpu, current_node_flow, chosen_nodes):

        x = np.reshape(observation, [1, observation.shape[0], observation.shape[1], 1])
        tf_prob = self.sess.run(model.probs, feed_dict={model.tf_obs: x})
        filter_prob = tf_prob.ravel()

        for index, score in enumerate(filter_prob):
            if index in chosen_nodes:
                filter_prob[index] = 0.0
        candidate = np.argmax(filter_prob)

        for index, score in enumerate(filter_prob):
            if sub.nodes[index]['cpu_remain'] < current_node_cpu and sub.nodes[index]['flow_remain'] < current_node_flow:
                filter_prob[index] = 0.0
        action = np.argmax(filter_prob)

        if filter_prob[action] == 0.0:
            return -1
        else:
            return action

    def store_transition(self, s, a, r):
        s = np.reshape(s, [s.shape[0], s.shape[1], 1])
        self.ep_obs.append(s)
        self.ep_as.append(a)
        self.ep_rs.append(r)

    def learn(self, model, reward):
        # saver = tf.train.Saver()
        discounted_ep_rs_norm = self._discount_and_norm_rewards(reward)
        epy = np.eye(self.action_num)[self.ep_as]
        # 返回求解梯度
        tf_grad = self.sess.run(model.newGrads,
                                feed_dict={model.tf_obs: self.ep_obs,
                                           model.input_y: epy,
                                           model.tf_vt: discounted_ep_rs_norm})
        # tf_grad = self.sess.run(model.newGrads,
        #                         feed_dict={model.tf_obs: self.ep_obs,
        #                                    model.tf_acts: self.ep_as,
        #                                    model.tf_vt: discounted_ep_rs_norm})
        # 创建存储参数梯度的缓冲器
        grad_buffer = self.sess.run(model.tvars)
        # 将获得的梯度累加到gradBuffer中
        for ix, grad in enumerate(tf_grad):
            grad_buffer[ix] += grad

        self.sess.run(model.train_op,
                      feed_dict={model.kernel_grad: grad_buffer[0],
                                 model.biases_grad: grad_buffer[1]})
        # model_path = "model_saved/model.cptk"
        # if not os.path.exists(model_path):
        #     os.makedirs(model_path)
        # saver.save(self.sess, model_path)

        self.ep_obs, self.ep_as, self.ep_rs = [], [], []
        return discounted_ep_rs_norm

    # discount episode rewards
    def _discount_and_norm_rewards(self, reward):

        discounted_ep_rs = np.zeros_like(self.ep_rs)
        running_add = 0
        for t in reversed(range(0, len(self.ep_rs))):
            running_add = running_add * self.gamma + self.ep_rs[t]
            discounted_ep_rs[t] = running_add / reward

        discounted_ep_rs -= np.mean(discounted_ep_rs)
        discounted_ep_rs /= np.std(discounted_ep_rs)
        return discounted_ep_rs

    def calculate_reward(self, sub, req, node_map):

        link_map = {}
        for vLink in req.edges:
            vn_from = vLink[0]
            vn_to = vLink[1]
            sn_from = node_map[vn_from]
            sn_to = node_map[vn_to]
            if nx.has_path(sub, source=sn_from, target=sn_to):
                for path in Network.k_shortest_path(sub, sn_from, sn_to, 1):
                    if Network.get_path_capacity(sub, path) >= req[vn_from][vn_to]['bw']:
                        link_map.update({vLink: path})
                        break
                    else:
                        continue
        if len(link_map) == req.number_of_edges():
            reward = 0
            # link resource
            for vl, path in link_map.items():
                link_resource = req[vl[0]][vl[1]]['bw']
                reward += link_resource * (len(path) - 2)

            return reward + 0.01
        else:
            return -1.0
