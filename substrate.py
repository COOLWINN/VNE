import networkx as nx
from utils import create_network, create_training_set
from mcts import MCTS
from grc import GRC
from reinforce import PolicyGradient
from reinforce2 import RL


class Substrate:

    def __init__(self, filename):
        self.net = create_network(filename)
        self.agent = None
        self.mapped_info = {}
        self.total_arrived = 0
        self.total_accepted = 0
        self.total_revenue = 0
        self.total_cost = 0
        self.evaluations = {}

    def mapping_algorithm(self, vnr, method):
        """two phrases:node mapping and link mapping"""

        self.total_arrived += 1

        # mapping virtual nodes
        node_map = self.node_mapping(vnr, method)

        if len(node_map) == vnr.number_of_nodes():
            # mapping virtual links
            print("link mapping...")
            link_map = self.link_mapping(vnr, node_map)
            if len(link_map) == vnr.number_of_edges():
                self.mapped_info.update({vnr.graph['id']: (node_map, link_map)})
                self.change_resource(vnr, 'allocate')
                return True

        return False

    def node_mapping(self, vnr, method):
        """solve the virtual node mapping problem"""

        print("node mapping...")

        if method == 'grc':
            grc = GRC(damping_factor=0.9, sigma=1e-6)
            node_map = grc.run(self, vnr)

        elif method == "mcts":
            mcts = MCTS(computation_budget=5, exploration_constant=0.5)
            node_map = mcts.run(self, vnr)

        elif method == "rl":
            if self.agent is None:
                self.agent = RL(sub=self,
                                n_actions=self.net.number_of_nodes(),
                                n_features=(self.net.number_of_nodes(), 4),
                                learning_rate=0.05,
                                num_epoch=50,
                                batch_size=100)
                training_set = create_training_set('data/training/')
                self.agent.train(training_set)
            node_map = self.agent.test(self, vnr)

        else:
            if self.agent is None:
                self.agent = PolicyGradient(n_actions=100,
                                            n_features=(100, 7),
                                            learning_rate=0.02,
                                            reward_decay=0.95,
                                            episodes=50)
            node_map = self.agent.run(self, vnr)

        return node_map

    def link_mapping(self, vnr, node_map):
        """solve the virtual link mapping problem"""

        link_map = {}
        for vLink in vnr.edges:
            vn_from = vLink[0]
            vn_to = vLink[1]
            sn_from = node_map[vn_from]
            sn_to = node_map[vn_to]
            if nx.has_path(self.net, source=sn_from, target=sn_to):
                for path in nx.all_shortest_paths(self.net, source=sn_from, target=sn_to):
                    if self._min_bw(path) >= vnr[vn_from][vn_to]['bw']:
                        link_map.update({vLink: path})
                        break
                    else:
                        continue
        return link_map

    def change_resource(self, req, instruction):
        """allocate or release the resource of an request"""

        requested, occupied = 0, 0

        # read node map and link map from the substrate network
        req_id = req.graph['id']
        node_map = self.mapped_info[req_id][0]
        link_map = self.mapped_info[req_id][1]

        factor = -1
        if instruction == 'allocate':
            factor = -1
        if instruction == 'release':
            factor = 1

        # allocate or release node resource
        for v_id, s_id in node_map.items():
            node_resource = req.nodes[v_id]['cpu']
            self.net.nodes[s_id]['cpu_remain'] += factor * node_resource
            occupied += node_resource
            requested += node_resource

        # allocate or release link resource
        for vl, path in link_map.items():
            link_resource = req[vl[0]][vl[1]]['bw']
            requested += link_resource
            start = path[0]
            for end in path[1:]:
                self.net[start][end]['bw_remain'] += factor * link_resource
                occupied += link_resource
                start = end

        # allocate instruction: update evaluations
        if instruction == 'allocate':
            self.evaluate(req.graph['time'], requested, occupied)

        # release instruction: remove this request's node map and link map
        if instruction == 'release':
            self.mapped_info.pop(req_id)

    def _min_bw(self, path):
        """find the least bandwidth of a path"""
        bandwidth = 1000
        head = path[0]
        for tail in path[1:]:
            if self.net[head][tail]['bw_remain'] <= bandwidth:
                bandwidth = self.net[head][tail]['bw_remain']
            head = tail
        return bandwidth

    def evaluate(self, time, requested, occupied):
        self.total_accepted += 1
        self.total_revenue += requested
        self.total_cost += occupied
        self.evaluations.update({time: (self.total_accepted / self.total_arrived,
                                        self.total_revenue,
                                        self.total_cost,
                                        self.total_revenue / self.total_cost)})

