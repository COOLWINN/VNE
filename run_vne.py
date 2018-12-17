from reinforce import PolicyGradient
from vne_environment import MyEnv
from network import create_sub
from network import create_req
import copy

# create a substrate network
sub = create_sub('sub.txt')

# create a set of virtual network requests
reqs = []
for i in range(2000):
    filename = 'requests/req%s.txt' % i
    vnr_arrive = create_req(i, filename)
    vnr_leave = copy.deepcopy(vnr_arrive)
    vnr_leave.graph['type'] = 1
    vnr_leave.graph['time'] = vnr_arrive.graph['time'] + vnr_arrive.graph['duration']
    reqs.append(vnr_arrive)
    reqs.append(vnr_leave)

# sort the reqs by their time(including arrive time and depart time)
reqs.sort(key=lambda r: r.graph['time'])

for req in reqs:
    if req.graph['type'] == 0:
        # initialize the environment
        env = MyEnv(sub, req)

        # initialize the agent
        RL = PolicyGradient(env.action_space.n,
                            n_features=env.observation_space.shape,
                            learning_rate=0.02,
                            reward_decay=0.95)

        for i_episode in range(1000):
            observation = env.reset()

            # get a trajectory by sampling from the start-state distribution
            while True:
                action = RL.choose_action(observation)
                observation_, reward, done, info = env.step(action)
                RL.store_transition(observation, action, reward)

                if done:
                    # train on one epoch
                    vt = RL.learn()
                    break

                observation = observation_

            print("%s episode " % i_episode)

        print("vnr%s has been mapped!" % req.graph['id'])
