# -*- coding: utf-8 -*-
# jvparidon@gmail.com
"""Compute rank correlations between word vector cosine similarities and human ratings of semantic similarity."""
import pandas as pd
import argparse
import os
import scipy.spatial.distance
import scipy.stats
from .vecs import Vectors
from .utensils import log_timer
import logging
logging.basicConfig(format='[{levelname}] {message}', style='{', level=logging.INFO)
path = os.path.dirname(__file__)


@log_timer
def compare_similarities(vectors, similarities):
    vecs_dict = vectors.as_df()
    similarities['word1'] = similarities['word1'].str
    similarities['word2'] = similarities['word2'].str
    vecs_dsm = []
    similarities_dsm = []
    word1 = []
    word2 = []
    missing = 0

    for index, pair in similarities.iterrows():
        if all(word in vecs_dict.keys() for word in (pair['word1'], pair['word2'])):
            vecs_dsm.append(1.0 - scipy.spatial.distance.cosine(vecs_dict[pair['word1']], vecs_dict[pair['word2']]))
            similarities_dsm.append(pair['similarity'])
            word1.append(pair['word1'])
            word2.append(pair['word2'])
        else:
            missing += 1

    total = len(similarities)
    penalty = (total - missing) / total
    score = scipy.stats.spearmanr(similarities_dsm, vecs_dsm)[0]
    adjusted_score = scipy.stats.spearmanr(similarities_dsm, vecs_dsm)[0] * penalty
    score = pd.DataFrame({'score': [score], 'adjusted score': [adjusted_score]})
    predictions = pd.DataFrame({'word1': word1, 'word2': word2, 'similarity': similarities_dsm, 'predicted similarity': vecs_dsm})
    return {'scores': score, 'predictions': predictions}


@log_timer
def evaluate_vecs(vecs_fname, lang):
    similarities_path = os.path.join(path, 'evaluation', 'datasets', 'similarities')
    results_path = os.path.join(path, 'evaluation', 'results', 'similarities')
    if not os.path.exists(results_path):
        os.mkdir(results_path)
    logging.info(f'evaluating lexical norm prediction with {vecs_fname}')
    vectors = Vectors(vecs_fname, normalize=True, n=1e6, d=300)
    scores = []
    for similarities_fname in os.listdir(similarities_path):
        if similarities_fname.startswith(lang):
            logging.info(f'predicting norms from {similarities_fname}')
            similarities = pd.read_csv(os.path.join(similarities_path, similarities_fname), sep='\t', comment='#')
            score = compare_similarities(vectors, similarities)['scores']
            score['source'] = similarities_fname
            scores.append(score)
    scores_fname = os.path.split(vecs_fname)[1].replace('.vec', '.tsv')
    if len(scores) > 0:
        pd.concat(scores).to_csv(os.path.join(results_path, scores_fname), sep='\t')


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description='compute rank correlations between word vector cosine similarities and human semantic similarity ratings')
    argparser.add_argument('lang', help='language to compare simarities in (uses two-letter ISO language codes)')
    argparser.add_argument('vecs_fname', help='word vectors to evaluate')
    args = argparser.parse_args()

    results = evaluate_vecs(**vars(args))