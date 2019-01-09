from utils import create_training_set
from grc import GRC
from mcts import MCTS
from reinforce import PolicyGradient
from reinforce2 import RL


def configure(sub, name):

    if name == 'grc':
        grc = GRC(damping_factor=0.9, sigma=1e-6)
        return grc

    elif name == 'mcts':
        mcts = MCTS(computation_budget=5, exploration_constant=0.5)
        return mcts

    elif name == 'rl':
        directory = 'data/training/'
        training_set = create_training_set(directory)
        rl = RL(sub=sub,
                n_actions=sub.net.number_of_nodes(),
                n_features=4,
                learning_rate=0.05,
                num_epoch=40,
                batch_size=100)
        rl.train(training_set)
        return rl

    else:
        pg = PolicyGradient(n_actions=100,
                            n_features=7,
                            learning_rate=0.02,
                            reward_decay=0.95,
                            episodes=50)
        return pg
