import tensorflow as tf


class Pnetwork():

    def __init__(self, n_actions, n_features, learning_rate):

        with tf.name_scope('inputs'):
            self.tf_obs = tf.placeholder(tf.float32,
                                         [None, n_actions, n_features, 1],
                                         name="observations")
            self.tf_acts = tf.placeholder(tf.int32,
                                          [None, ],
                                          name="actions_num")

        with tf.name_scope("conv"):
            kernel = tf.Variable(tf.truncated_normal([1, n_features, 1, 1],
                                                     dtype=tf.float32,
                                                     stddev=0.1),
                                 name="weights")
            conv = tf.nn.conv2d(input=self.tf_obs,
                                filter=kernel,
                                strides=[1, 1, n_features, 1],
                                padding="VALID")
            biases = tf.Variable(tf.constant(0.0, shape=[1], dtype=tf.float32),
                                 name="biases")
            conv1 = tf.nn.relu(tf.nn.bias_add(conv, biases))
            self.scores = tf.reshape(conv1, [-1, n_actions])

        with tf.name_scope("output"):
            self.probs = tf.nn.softmax(self.scores)

        with tf.name_scope('loss'):
            self.tf_vt = tf.placeholder(tf.float32, [None, ], name="action_value")
            # 计算损失函数loss(当前Action对应的概率的对数)
            self.neg_log_prob = -tf.reduce_sum(tf.log(self.probs) * tf.one_hot(self.tf_acts, n_actions), axis=1)
            self.loss = tf.reduce_mean(self.neg_log_prob*self.tf_vt)
            # 获取策略网络中全部可训练的参数
            self.tvars = tf.trainable_variables()
            # 计算损失函数梯度
            self.newGrads = tf.gradients(self.loss, self.tvars)

        with tf.name_scope('train'):
            # 权重参数梯度
            self.kernel_grad = tf.placeholder(tf.float32, name="batch_grad1")
            # 偏置参数梯度
            self.biases_grad = tf.placeholder(tf.float32, name="batch_grad2")
            # 整合两个梯度
            self.batch_grad = [self.kernel_grad, self.biases_grad]
            # 优化器
            adam = tf.train.AdamOptimizer(learning_rate)
            # 更新策略网络参数
            self.train_op = adam.apply_gradients(zip(self.batch_grad, self.tvars))
