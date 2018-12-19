from substrate import Substrate
from utils import create_requests, generate_topology_figure
from reinforce import PolicyGradient

# Step1: create the substrate network and VNRs.
directory = 'network_files/'
sub = Substrate(directory + 'sub.txt')
reqs = create_requests(directory)
# generate_topology_figure(sub.net, 'substrate')
# for i in range(5):
#     generate_topology_figure(reqs[i], 'virtual_network%s' % i)
# Step2: initialize the agent
agent = PolicyGradient(100, n_features=(100, 7), learning_rate=0.02, reward_decay=0.95)

# Step3: handle requests
for req in reqs:

    # the id of current request
    req_id = req.graph['id']

    if req.graph['type'] == 0:
        """a request which is newly arrived"""

        print("Try to map request%s" % req_id)

        if sub.mapping_algorithm(req, 'grc', agent):
            print("Success!")
        else:
            print("Failure!")

    if req.graph['type'] == 1:
        """a request which is ready to leave"""
        if req_id in sub.mapped_info.keys():
            sub.change_resource(req, 'release')
            print("End up the service of vnr%s and the occupied resource has benn released..." % req_id)

# Step4: output results
sub.output_results()
