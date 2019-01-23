from extract import read_requests
from comparison1.grc import GRC
from comparison2.mcts import MCTS
from comparison3.agent import RL
from mine.reinforce import PolicyGradient


def configure(sub, name):

    if name == 'grc':
        grc = GRC(damping_factor=0.9, sigma=1e-6)
        return grc

    elif name == 'mcts':
        mcts = MCTS(computation_budget=5, exploration_constant=0.5)
        return mcts

    elif name == 'rl':
        training_path = 'comparison3/training_set/'
        training_set = read_requests(training_path, 1000)
        rl = RL(sub=sub,
                n_actions=sub.net.number_of_nodes(),
                n_features=4,
                learning_rate=0.05,
                num_epoch=10,
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
