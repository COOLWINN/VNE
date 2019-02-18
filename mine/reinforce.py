import os
import tensorflow as tf
import numpy as np
from mine.my_mdp import MyEnv
from .model import Pnetwork


class PolicyGradient:

    def __init__(self, n_actions, n_features, learning_rate, reward_decay, episodes):
        self.n_actions = n_actions
        self.n_features = n_features
        self.lr = learning_rate
        self.gamma = reward_decay
        self.episodes = episodes
        self.ep_obs, self.ep_as, self.ep_rs = [], [], []
        self.p_network = Pnetwork(n_actions, n_features, learning_rate)
        self.sess = tf.InteractiveSession()

    def run(self, sub, vnr):

        # 初始化环境
        env = MyEnv(sub.net, vnr)

        self.sess.run(tf.global_variables_initializer())

        for i_episode in range(self.episodes):

            # 重置VNE环境
            observation = env.reset()

            tmp_node_map = {}

            # 采样
            for count in range(vnr.number_of_nodes()):
                action = self.choose_action(self.p_network, observation, sub.net, vnr.nodes[count]['cpu'])
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
                    print(vt)

        observation = env.reset()
        node_map = {}
        chosen_nodes = []
        for count in range(vnr.number_of_nodes()):
            action = self.choose_max_action(self.p_network, observation, sub.net, vnr.nodes[count]['cpu'], chosen_nodes)
            if action == -1:
                break
            else:
                observation_, _, done, info = env.step(action)
                chosen_nodes.append(action)
                node_map.update({count: action})

                # after each step, we should update the observation
                observation = observation_

        return node_map

    def choose_action(self, model, observation, sub, current_node_cpu):

        x = np.reshape(observation, [1, observation.shape[0], observation.shape[1], 1])
        prob_weights = self.sess.run(model.scores, feed_dict={model.tf_obs: x})

        candidate_action = []
        candidate_score = []
        for index, score in enumerate(prob_weights.ravel()):
            if index not in self.ep_as and sub.nodes[index]['cpu_remain'] >= current_node_cpu:
                candidate_action.append(index)
                candidate_score.append(score)
        if len(candidate_action) == 0:
            return -1
        else:
            candidate_prob = np.exp(candidate_score) / np.sum(np.exp(candidate_score))
            # 选择动作
            action = np.random.choice(candidate_action, p=candidate_prob)
            return action

    def choose_max_action(self, model, observation, sub, current_node_cpu, chosen_nodes):

        x = np.reshape(observation, [1, observation.shape[0], observation.shape[1], 1])
        tf_prob = self.sess.run(model.probs, feed_dict={model.tf_obs: x})
        filter_prob = tf_prob.ravel()
        for index, score in enumerate(filter_prob):
            if index in chosen_nodes or sub.nodes[index]['cpu_remain'] < current_node_cpu:
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
        saver = tf.train.Saver()
        discounted_ep_rs_norm = self._discount_and_norm_rewards(reward)
        # 返回求解梯度
        tf_grad = self.sess.run(model.newGrads,
                                feed_dict={model.tf_obs: self.ep_obs,
                                           model.tf_acts: self.ep_as,
                                           model.tf_vt: discounted_ep_rs_norm})
        # 创建存储参数梯度的缓冲器
        grad_buffer = self.sess.run(model.tvars)
        # 将获得的梯度累加到gradBuffer中
        for ix, grad in enumerate(tf_grad):
            grad_buffer[ix] += grad

        self.sess.run(model.train_op,
                      feed_dict={model.kernel_grad: grad_buffer[0],
                                 model.biases_grad: grad_buffer[1]})
        model_path = "model_saved/model.cptk"
        if not os.path.exists(model_path):
            os.makedirs(model_path)
        saver.save(self.sess, model_path)

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

        link_map = sub.link_mapping(req, node_map)
        if len(link_map) == req.number_of_edges():
            requested, occupied = 0, 0

            # node resource
            for vn_id, sn_id in node_map.items():
                node_resource = req.nodes[vn_id]['cpu']
                occupied += node_resource
                requested += node_resource

            # link resource
            for vl, path in link_map.items():
                link_resource = req[vl[0]][vl[1]]['bw']
                requested += link_resource
                occupied += link_resource * (len(path) - 1)

            reward = occupied - requested

            return reward + 0.01
        else:
            return -1.0
