from algorithm import Algorithm

if __name__ == '__main__':

    name = 'RL'
    algorithm = Algorithm(name, node_arg=10, link_method=1)
    runtime = algorithm.execute(result_dir='results_new/',
                                network_path='networks/',
                                sub_filename='sub-wm.txt',
                                req_num=1000)
    print(runtime)
