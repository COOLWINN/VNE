import tensorflow as tf
import numpy as np
from environment1 import MyEnv


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
        node_map = {}
        # initialize the environment
        env = MyEnv(sub.net, vnr)
        for i_episode in range(self.episodes):

            # reset VNE environment
            observation = env.reset()

            node_map.clear()

            # get a trajectory by sampling from the start-state distribution
            for count in range(vnr.number_of_nodes()):
                action = self.choose_action(observation, sub.net, vnr.nodes[count]['cpu'])
                observation_, reward, done, info = env.step(action)
                self.store_transition(observation, action, reward)
                node_map.update({count: action})

                # after each step, we should update the observation
                observation = observation_

            # when all the virtual nodes have found their host nodes, train our policy network
            vt = self.learn()
            print(vt)

        return node_map

    def _build_net(self):
        with tf.name_scope('inputs'):
            self.tf_obs = tf.placeholder(tf.float32, [None, self.n_features[0], self.n_features[1], 1],
                                         name="observations")
            self.tf_acts = tf.placeholder(tf.int32, [None, ], name="actions_num")
            self.tf_vt = tf.placeholder(tf.float32, [None, ], name="action_value")

        conv = tf.layers.conv2d(inputs=self.tf_obs,
                                filters=1,
                                kernel_size=[1, self.n_features[1]],
                                strides=(1, self.n_features[1]),
                                activation=tf.nn.relu)

        conv_flat = tf.reshape(conv, [-1, self.n_actions])

        # all_act = tf.layers.dense(
        #     inputs=conv_flat,
        #     units=self.n_actions,
        #     activation=None,
        #     kernel_initializer=tf.random_normal_initializer(mean=0, stddev=0.3),
        #     bias_initializer=tf.constant_initializer(0.1)
        # )
        #
        # self.all_act_prob = tf.nn.softmax(all_act, name='act_prob')

        self.all_act_prob = tf.nn.softmax(conv_flat,name='act_prob')
        with tf.name_scope('loss'):
            neg_log_prob = tf.nn.sparse_softmax_cross_entropy_with_logits(logits=conv_flat, labels=self.tf_acts)
            loss = tf.reduce_mean(neg_log_prob * self.tf_vt)


        # # loss function
        # with tf.name_scope('loss'):
        #     neg_log_prob = tf.nn.sparse_softmax_cross_entropy_with_logits(logits=all_act, labels=self.tf_acts)
        #     loss = tf.reduce_mean(neg_log_prob * self.tf_vt)

        # Optimizer
        with tf.name_scope('train'):
            self.train_op = tf.train.AdamOptimizer(self.lr).minimize(loss)

    def choose_action(self, observation, sub, current_node_cpu):
        prob_weights = self.sess.run(self.all_act_prob,
                                     feed_dict={self.tf_obs: observation[np.newaxis, :, :, np.newaxis]})
        arr = prob_weights.ravel().tolist()

        new_actions = []
        new_probs = []
        for index in range(prob_weights.shape[1]):
            if index not in self.ep_as and \
                    sub.nodes[index]['cpu_remain'] >= current_node_cpu:
                new_actions.append(index)
                new_probs.append(arr[index])

        new_softmax = np.exp(new_probs)/np.sum(np.exp(new_probs))
        action = np.random.choice(new_actions, p=new_softmax)
        return action

    def store_transition(self, s, a, r):
        self.ep_obs.append(s)
        self.ep_as.append(a)
        self.ep_rs.append(r)

    def learn(self):
        discounted_ep_rs_norm = self._discount_and_norm_rewards()

        self.sess.run(self.train_op, feed_dict={
            self.tf_obs: np.vstack(self.ep_obs).reshape(len(self.ep_obs), self.n_features[0], self.n_features[1], 1),
            # shape=[None, n_obs[0], n_obs[1] ,1]
            self.tf_acts: np.array(self.ep_as),  # shape=[None, ]
            self.tf_vt: discounted_ep_rs_norm,  # shape=[None, ]
        })

        self.ep_obs, self.ep_as, self.ep_rs = [], [], []
        return discounted_ep_rs_norm

    # discount episode rewards
    def _discount_and_norm_rewards(self):
        node_map = {}
        # for i in range(len(self.ep_as)):
        #     node_map.update({i: self.ep_as[i]})
        # link_map = self.sub.link_mapping(self.vnr, node_map)
        # if len(link_map) == self.vnr.number_of_edges():
        #     requested, occupied = 0, 0
        #
        #     # node resource
        #     for vn_id, sn_id in node_map.items():
        #         node_resource = self.vnr.nodes[vn_id]['cpu']
        #         occupied += node_resource
        #         requested += node_resource
        #
        #     # link resource
        #     for vl, path in link_map.items():
        #         link_resource = self.vnr[vl[0]][vl[1]]['bw']
        #         requested += link_resource
        #         occupied += link_resource * (len(path) - 1)
        #     total = occupied-requested
        # else:
        #     total = -1000

        discounted_ep_rs = np.zeros_like(self.ep_rs)
        running_add = 0
        for t in reversed(range(0, len(self.ep_rs))):
            running_add = running_add * self.gamma + self.ep_rs[t]
            discounted_ep_rs[t] = running_add

        discounted_ep_rs -= np.mean(discounted_ep_rs)
        discounted_ep_rs /= np.std(discounted_ep_rs)
        return discounted_ep_rs
