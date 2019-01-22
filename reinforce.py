import tensorflow as tf
import numpy as np
from my_mdp import MyEnv


class PolicyGradient:
    def __init__(self, n_actions, n_features, learning_rate, reward_decay, episodes):
        self.n_actions = n_actions
        self.n_features = n_features
        self.lr = learning_rate
        self.gamma = reward_decay
        self.episodes = episodes
        self.ep_obs, self.ep_as, self.ep_rs = [], [], []
        self._build_net()
        self.sess = tf.Session()
        self.sess.run(tf.global_variables_initializer())

    def run(self, sub, vnr):

        # initialize the environment
        env = MyEnv(sub.net, vnr)
        for i_episode in range(self.episodes):

            # reset VNE environment
            observation = env.reset()

            tmp_node_map = {}

            # get a trajectory by sampling from the start-state distribution
            for count in range(vnr.number_of_nodes()):
                action = self.choose_action(observation, sub.net, vnr.nodes[count]['cpu'])
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
                    vt = self.learn(reward)
                    print(vt)

        observation = env.reset()
        node_map = {}
        chosen_nodes = []
        for count in range(vnr.number_of_nodes()):
            action = self.choose_max_action(observation, sub.net, vnr.nodes[count]['cpu'], chosen_nodes)
            if action == -1:
                break
            else:
                observation_, _, done, info = env.step(action)
                chosen_nodes.append(action)
                node_map.update({count: action})

                # after each step, we should update the observation
                observation = observation_

        return node_map

    def _build_net(self):
        with tf.name_scope('inputs'):
            self.tf_obs = tf.placeholder(tf.float32, [None, self.n_actions, self.n_features, 1],
                                         name="observations")
            self.tf_acts = tf.placeholder(tf.int32, [None, ], name="actions_num")
            self.tf_vt = tf.placeholder(tf.float32, [None, ], name="action_value")

        with tf.name_scope("conv"):
            kernel = tf.Variable(tf.truncated_normal([1, self.n_features, 1, 1],
                                                     dtype=tf.float32,
                                                     stddev=0.1),
                                 name="weights")
            conv = tf.nn.conv2d(input=self.tf_obs,
                                filter=kernel,
                                strides=[1, 1, self.n_features, 1],
                                padding="VALID")
            biases = tf.Variable(tf.constant(0.0, shape=[1], dtype=tf.float32),
                                 name="bias")
            conv1 = tf.nn.relu(tf.nn.bias_add(conv, biases))
            self.scores = tf.reshape(conv1, [-1, self.n_actions])

        with tf.name_scope("output"):
            self.probs = tf.nn.softmax(self.scores)

        # conv_flat = tf.reshape(conv, [-1, self.n_actions])
        # all_act = tf.layers.dense(
        #     inputs=conv_flat,
        #     units=self.n_actions,
        #     activation=None,
        #     kernel_initializer=tf.random_normal_initializer(mean=0, stddev=0.3),
        #     bias_initializer=tf.constant_initializer(0.1)
        # )
        #
        # self.all_act_prob = tf.nn.softmax(all_act, name='act_prob')
        # self.all_act_prob = tf.nn.softmax(conv_flat,name='act_prob')
        with tf.name_scope('loss'):
            # 获取策略网络中全部可训练的参数
            self.tvars = tf.trainable_variables()
            # 计算损失函数loss(当前Action对应的概率的对数)
            self.neg_log_prob = -tf.reduce_sum(tf.log(self.probs) * tf.one_hot(self.tf_acts, self.n_actions), axis=1)
            self.loss = tf.reduce_mean(self.neg_log_prob*self.tf_vt)
            # 计算损失函数梯度
            self.newGrads = tf.gradients(self.loss, self.tvars)
            # neg_log_prob = tf.nn.sparse_softmax_cross_entropy_with_logits(logits=conv_flat, labels=self.tf_acts)
            # loss = tf.reduce_mean(neg_log_prob * self.tf_vt)

        # loss function
        # with tf.name_scope('loss'):
        #     neg_log_prob = tf.nn.sparse_softmax_cross_entropy_with_logits(logits=conv_flat, labels=self.tf_acts)
        #     loss = tf.reduce_mean(neg_log_prob * self.tf_vt)

        # Optimizer
        # with tf.name_scope('train'):
        #     self.train_op = tf.train.AdamOptimizer(self.lr).minimize(loss)

        # 梯度更新
        with tf.name_scope('train'):
            # 权重参数梯度
            self.kernel_grad = tf.placeholder(tf.float32, name="batch_grad1")
            # 偏置参数梯度
            self.biases_grad = tf.placeholder(tf.float32, name="batch_grad2")
            # 整合两个梯度
            self.batch_grad = [self.kernel_grad, self.biases_grad]
            # 优化器
            adam = tf.train.AdamOptimizer(learning_rate=self.lr)
            # 更新策略网络参数
            self.train_op = adam.apply_gradients(zip(self.batch_grad, self.tvars))

    def choose_action(self, observation, sub, current_node_cpu):

        x = np.reshape(observation, [1, observation.shape[0], observation.shape[1], 1])
        prob_weights = self.sess.run(self.scores,
                                     feed_dict={self.tf_obs: x})

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

    def choose_max_action(self, observation, sub, current_node_cpu, chosen_nodes):

        x = np.reshape(observation, [1, observation.shape[0], observation.shape[1], 1])
        tf_prob = self.sess.run(self.probs, feed_dict={self.tf_obs: x})
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

    def learn(self, reward):
        discounted_ep_rs_norm = self._discount_and_norm_rewards(reward)
        # 返回求解梯度
        tf_grad = self.sess.run(self.newGrads,
                                feed_dict={self.tf_obs: self.ep_obs,
                                           self.tf_acts: self.ep_as,
                                           self.tf_vt: discounted_ep_rs_norm})
        # 创建存储参数梯度的缓冲器
        grad_buffer = self.sess.run(self.tvars)
        # 将获得的梯度累加到gradBuffer中
        for ix, grad in enumerate(tf_grad):
            grad_buffer[ix] += grad

        self.sess.run(self.train_op,
                      feed_dict={self.kernel_grad: grad_buffer[0],
                                 self.biases_grad: grad_buffer[1]})

        # self.sess.run(self.train_op, feed_dict={
        #     self.tf_obs: np.vstack(self.ep_obs).reshape(len(self.ep_obs), self.n_features[0], self.n_features[1], 1),
        #     # shape=[None, n_obs[0], n_obs[1] ,1]
        #     self.tf_acts: np.array(self.ep_as),  # shape=[None, ]
        #     self.tf_vt: discounted_ep_rs_norm,  # shape=[None, ]
        # })

        self.ep_obs, self.ep_as, self.ep_rs = [], [], []
        return discounted_ep_rs_norm

    # discount episode rewards
    def _discount_and_norm_rewards(self, reward):

        discounted_ep_rs = np.zeros_like(self.ep_rs)
        running_add = 0
        for t in reversed(range(0, len(self.ep_rs))):
            running_add = running_add * self.gamma + self.ep_rs[t]
            discounted_ep_rs[t] = running_add/reward

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
