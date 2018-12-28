from substrate import Substrate
from utils import create_requests
import time
from analysis import *


def main():

    # Step1: create the substrate network and VNRs.
    directory = 'data/'
    sub = Substrate(directory + 'sub.txt')
    reqs = create_requests(directory)

    # Step2: choose an algorithm to run
    algorithm = input("Please select an algorithm('grc','mcts','rl','mine'): ")

    # Step3: handle requests
    start = time.time()
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

    end = time.time()-start
    print(end)

    # Step4: output results
    save_result(sub, '%s-VNE.txt' % algorithm)


if __name__ == '__main__':
    main()
