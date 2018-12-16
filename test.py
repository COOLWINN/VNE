import numpy as np
import tensorflow as tf

M = np.array([[[2], [1], [2], [-1]], [[0], [-1], [3], [0]], [[2], [1], [-1], [4]], [[-2], [0], [-3], [4]]],
             dtype="float32").reshape(1, 4, 4, 1)
print(M)

filter_weight = tf.get_variable("weights", [2, 2, 1, 1], initializer=tf.constant_initializer([[-1, 4], [2, 1]]))

biases = tf.get_variable("bias", [1], initializer=tf.constant_initializer(1))
x = tf.placeholder('float32', [1, None, None, 1])

conv = tf.nn.conv2d(x, filter_weight, strides=[1, 1, 1, 1], padding="SAME")
add_bias = tf.nn.bias_add(conv, biases)

init_op = tf.global_variables_initializer()
with tf.Session() as sess:
    init_op.run()
    M_conv = sess.run(add_bias, feed_dict={x: M})

print("M after convolution: \n", M_conv)
