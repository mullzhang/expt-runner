import logging
import os
from datetime import datetime
from glob import glob
from collections.abc import Mapping

from omegaconf import OmegaConf

logger = logging.getLogger(__name__)

CONFIG_FNAME = 'config.yaml'


class BaseExpt:
    def __init__(self, **config):
        self._config = OmegaConf.create(config)

    @property
    def config(self):
        try:
            return self._config
        except AttributeError:
            self._config = config = OmegaConf.create({})
            return config

    @staticmethod
    def gen_timestamp(format='%y%m%d%H%M%S%f'):
        return str(datetime.now().strftime(format))

    def make_save_dir(self, path_result_dir, name=None):
        if name is None:
            name = self.gen_timestamp()
        
        path_save_dir = os.path.join(path_result_dir, name)
        if not os.path.exists(path_save_dir):
            os.makedirs(path_save_dir)

        self.save_config(path_save_dir)
        return path_save_dir

    def load_config(self, path, inplace=True):
        def none_to_empty_dict(conf):
            for k, v in conf.items():
                if v is None:
                    conf[k] = {}
                elif isinstance(v, Mapping):
                    none_to_empty_dict(conf[k])
            return conf

        with open(path) as f:
            config = OmegaConf.load(f)

        config.update(none_to_empty_dict(config))
        if inplace:
            self._config = config
        else:
            return config

    def save_config(self, path, fname=CONFIG_FNAME):
        with open(os.path.join(path, fname), 'w') as f:
            OmegaConf.save(self._config, f)

    def update_config(self, **config):
        def iter_update(dict_base, other):
            for k, v in other.items():
                if isinstance(v, Mapping) and k in dict_base:
                    iter_update(dict_base[k], v)
                else:
                    dict_base[k] = v
            return dict_base

        self._config.update(iter_update(self._config, config))

    def search_result(self, path_save_dir, fname=CONFIG_FNAME, multiple=False):
        def equal_config(config1, config2):
            is_matched = True
            for k, v in config1.items():
                if k in config2:
                    if isinstance(v, Mapping):
                        if not equal_config(v, config2[k]):
                            is_matched = False
                            break
                    else:
                        if v != config2[k]:
                            is_matched = False
                            break
            return is_matched

        path_list = []
        for path in glob(os.path.join(path_save_dir, '*')):
            path_config = os.path.join(path, fname)
            if not os.path.exists(path_config):
                continue

            config = self.load_config(path_config, inplace=False)
            if equal_config(self.config, config):
                if multiple:
                    path_list.append(path)
                else:
                    return path

        return path_list

    def setup(self):
        pass

    def run(self):
        pass

    def save_result(self, path_result_dir):
        pass
