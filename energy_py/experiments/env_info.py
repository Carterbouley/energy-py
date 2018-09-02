"""
Saves the info dictionary generated by an environment

When an environment is stepped through it returns a dictionary

    next_observation, reward, done, info = env.step(action)

save_env_info() will take this dictionary and save it to csv
"""

import logging
import os

import numpy as np
import pandas as pd

from energy_py.common import ensure_dir


logger = logging.getLogger(__name__)


def save_env_info(env, info, episode, env_hist_path=None):
    """
    Saves the environment info dictionary to a csv

    args
        env (energ_py environment)
        env_info (dict) the info dict returned from env.step()
        episode (int)
    """
    if hasattr(env.observation_space, 'info') and hasattr(env.state_space, 'info'):
        logger.debug('saving env history')

        output = process_env_info(env, info)

        #  TODO split into process info and save csv funcs
        if env_hist_path:
            csv_path = os.path.join(env_hist_path,
                                   'ep_{}'.format(episode),
                                   'info.csv')
            ensure_dir(csv_path)
            output.to_csv(csv_path)

        try:
            logger.debug(output.loc[:, ['action', 'reward']].describe())
        except KeyError:
            pass

    else:
        logger.debug('Not saving env history')

    return output


def process_env_info(env, info):
    state_info = env.state_space.info
    observation_info = env.observation_space.info

    output = []
    for key, info in info.items():
        if isinstance(info[0], np.ndarray):
            df = pd.DataFrame(np.array(info).reshape(len(info), -1))

            #  there must be a better way! TODO
            if key == 'observation' and observation_info:
                df.columns = ['{}_{}'.format(key, o)
                              for o in observation_info]

            elif key == 'next_observation' and observation_info:
                df.columns = ['{}_{}'.format(key, o)
                              for o in observation_info]

            elif key == 'state' and state_info:
                df.columns = ['{}_{}'.format(key, s)
                              for s in state_info]

            elif key == 'next_state' and state_info:
                df.columns = ['{}_{}'.format(key, s)
                              for s in state_info]
            else:
                df.columns = ['{}_{}'.format(key, n)
                              for n in range(df.shape[1])]
        else:
            df = pd.DataFrame(info, columns=[key])

        output.append(df)

    output = pd.concat(output, axis=1)
    output.index = env.state_space.episode.index[:-1]

    return output
