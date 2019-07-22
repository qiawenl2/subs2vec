# -*- coding: utf-8 -*-
# jvparidon@gmail.com
import numpy as np
import pandas as pd
import argparse
import similarities
import analogies
from utensils import log_timer
import logging
logging.basicConfig(format='[{levelname}] {message}', style='{', level=logging.INFO)


class Vectors:
    @log_timer
    def __init__(self, fname, normalize=False, n=1e6, d=300):
        self.n = int(n)
        self.d = d
        logging.info(f'loading vectors {fname}')

        with open(fname, 'r', encoding='utf-8') as vecfile:
            # skip header
            next(vecfile)

            # initialize arrays
            self.vectors = np.zeros((self.n, self.d))
            self.words = np.empty(self.n, dtype=object)

            # fill arrays
            for i, line in enumerate(vecfile):
                if i >= self.n:
                    break
                rowentries = line.rstrip('\n').split(' ')
                self.words[i] = rowentries[0]
                self.vectors[i] = rowentries[1:self.d + 1]

            # truncate empty part of arrays, if necessary
            self.vectors = self.vectors[:i]
            self.words = self.words[:i]
            self.n = i  # reset n to actual array length

            # normalize by L1 norm
            if normalize:
                self.vectors = self.vectors / np.linalg.norm(self.vectors, axis=1).reshape(-1, 1)

    def as_df(self):
        return pd.DataFrame(self.vectors).set_index(self.words)

    def as_dict(self):
        return {self.words[i]: self.vectors[i] for i in range(self.n)}


def write_vecs(vecs, fname):
    with open(fname, 'w') as vecfile:
        for key, value in vecs.items():
            vecfile.write(f'{key} {" ".join([str(num) for num in value])}\n')


def print_result(results):
    results = [str(result) for result in results]
    print('\t'.join(results))
