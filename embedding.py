from substrate import Substrate
from utils import create_requests, generate_topology_figure
# from reinforce import PolicyGradient


def main():
    # Step1: create the substrate network and VNRs.
    directory = 'network_files/'
    sub = Substrate(directory + 'sub.txt')
    reqs = create_requests(directory)

    # Step2: choose an algorithm to run
    algorithm = input("Please select an algorithm('grc','mcts','pg'): ")

    # Step3: handle requests
    for req in reqs:

        # the id of current request
        req_id = req.graph['id']

        if req.graph['type'] == 0:
            """a request which is newly arrived"""

            print("Try to map request%s" % req_id)

            # agent = PolicyGradient(100, sub, req, n_features=(100, 7), learning_rate=0.02, reward_decay=0.95)

            if sub.mapping_algorithm(req, algorithm):
                print("Success!")
            else:
                print("Failure!")

        if req.graph['type'] == 1:
            """a request which is ready to leave"""
            if req_id in sub.mapped_info.keys():
                sub.change_resource(req, 'release')
                print("End up the service of vnr%s and the occupied resource has benn released..." % req_id)

    # Step4: output results
    sub.output_results('result-%s.txt' % algorithm)


if __name__ == '__main__':
    main()
