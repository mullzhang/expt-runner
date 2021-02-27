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


def main():
    path_config = './config/example.yaml'
    path_result_dir = './results'

    expt = ExptExample()
    expt.load_config(path_config)
    expt.setup()
    expt.run()
    expt.save_result(path_result_dir)


if __name__ == '__main__':
    main()
