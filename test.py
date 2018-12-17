import numpy as np
import tensorflow as tf
from network import *
from vne_environment import MyEnv

sub = create_sub('sub.txt')
req = create_req(1,'requests/req1.txt')
env = MyEnv(sub, req)
print(env.observation_space.shape[1])
