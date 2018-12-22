from substrate import Substrate
from utils import create_requests


def main():
    # Step1: create the substrate network and VNRs.
    directory = 'network_files/'
    sub = Substrate(directory + 'sub.txt')
    reqs = create_requests(directory + 'requests/')

    # Step2: choose an algorithm to run
    algorithm = input("Please select an algorithm('grc','mcts','pg'): ")

    # Step3: handle requests
    for req in reqs:

        # the id of current request
        req_id = req.graph['id']

        if req.graph['type'] == 0:
            """a request which is newly arrived"""

            print("Try to map request%s: " % req_id)

            if sub.mapping_algorithm(req, algorithm):
                print("Success!")
            else:
                print("Failure!")

        if req.graph['type'] == 1:
            """a request which is ready to leave"""

            print("Release the resources which are occupied by request%s" % req_id)

            if req_id in sub.mapped_info.keys():
                sub.change_resource(req, 'release')

    # Step4: output results
    sub.output_results('result-%s.txt' % algorithm)


if __name__ == '__main__':
    main()
