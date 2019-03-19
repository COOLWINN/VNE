from maker import simulate_events_one
from comparison1.grc import GRC
from comparison2.mcts import MCTS
from comparison3.reinforce import RL
from mine.agent import PolicyGradient


def configure(sub, name, arg):

    if name == 'grc':
        grc = GRC(damping_factor=0.9, sigma=1e-6)
        return grc

    elif name == 'mcts':
        mcts = MCTS(computation_budget=5, exploration_constant=0.5)
        return mcts

    elif name == 'rl':
        training_set_path = 'comparison3/training_set/'
        training_set = simulate_events_one(training_set_path, 1000)
        rl = RL(sub=sub,
                n_actions=sub.net.number_of_nodes(),
                n_features=4,
                learning_rate=0.05,
                num_epoch=arg,
                batch_size=100)
        rl.train(training_set)
        return rl

    else:
        pg = PolicyGradient(action_num=sub.net.number_of_nodes(),
                            feature_num=7,
                            learning_rate=0.02,
                            reward_decay=0.95,
                            episodes=arg)
        return pg
