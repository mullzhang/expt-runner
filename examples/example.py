import logging
import os
import json

import dimod
import networkx as nx

from expt_runner import BaseExpt

log_format = '[%(asctime)s] %(message)s'
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format=log_format)


class ExptExample(BaseExpt):
    def setup(self):
        logger.info('start making model')

        model_config = self.config.model
        G = nx.complete_graph(model_config.num_variables)
        self.bqm = dimod.generators.random.uniform(G, **model_config.parameters)

        logger.info('finish making model')

    def run(self):
        logger.info('start solving problem')

        solver_config = self.config.solver
        self.solver = get_solver(solver_config.name)
        self.sampleset = self.solver.sample(self.bqm, **solver_config.parameters)
        logger.info(self.sampleset.lowest())

        logger.info('finish solving problem')

    def save_result(self, path_result_dir):
        logger.info('start saving results')

        self.path_save_dir = self.make_save_dir(path_result_dir)
        logger.info(f'saved at {self.path_save_dir}')

        with open(os.path.join(self.path_save_dir, 'sampleset.json'), 'w') as f:
            json.dump(self.sampleset.to_serializable(), f)

        logger.info('finish saving results')


def get_solver(name):
    if name == 'exact':
        solver = dimod.ExactSolver()
    elif name == 'random':
        solver = dimod.RandomSampler()
    else:
        raise ValueError(f'not found solver: {name}')

    return solver


def example_update_config(path_config, path_result_dir):
    """Example of run chaging particular parameters"""
    expt = ExptExample()
    expt.load_config(path_config)

    num_reads_list = [5, 10, 15]
    for n in num_reads_list:
        expt.update_config(
            solver=dict(parameters=dict(num_reads=n))
        )
        logger.info(expt.config)
        expt.setup()
        expt.run()
        # expt.save_result(path_result_dir)


def example_iterative_run(path_config, path_result_dir):
    """Example of running iteratively for the same model"""
    expt = ExptExample()
    expt.load_config(path_config)
    logger.info(expt.config)
    expt.setup()  # ex. Need much time to make model

    num_iters = 10
    for t in range(num_iters):
        logger.info(f'iteration: {t}')
        expt.run()
        # expt.save_result(path_result_dir)


def example_load_result(path_config, path_result_dir):
    """Example of loading results"""
    expt = ExptExample()
    expt.load_config(path_config)
    logger.info(expt.config)
    # expt.setup()  # If necessary

    path_list = expt.search_result(path_result_dir, multiple=True)
    if path_list is None:
        logger.info('not fount results')
        return

    for path_save_dir in path_list:
        logger.info(path_save_dir)


def main():
    path_config = './config/example.yaml'
    path_result_dir = './results'

    # example_update_config(path_config, path_result_dir)
    # example_iterative_run(path_config, path_result_dir)
    example_load_result(path_config, path_result_dir)


if __name__ == '__main__':
    main()
