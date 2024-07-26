import argparse
from functools import partial

import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

import textdistance
from tqdm import tqdm

def compute_f1_metric(df):
  tp = (df.pred == df.target).sum()
  fp = (df.pred != df.target).sum()
  fn = (df.pred != df.target).sum()
  
  precision = tp / (tp + fp) if (tp + fp) != 0 else 0
  recall = tp / (tp + fn) if (tp + fn) != 0 else 0
  f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) != 0 else 0
  return f1.mean()

def threshold(scores, mentions, correct, correct_mention, threshold):
  # normalize scores in 0-1 for each row
  scores = (scores - scores.min()) / (scores.max() - scores.min())
  return scores[:, 0] < threshold

def top_deviation(scores, mentions, correct, correct_mention, threshold):
  deviation = np.abs(scores[:, 0] - scores[:, 1]) / (0.5 * (scores[:, 0] + scores[:, 1]))
  return deviation < threshold

def mean_deviation(scores, mentions, correct, correct_mention, threshold):
  mean = scores.mean(axis=1)
  deviation = np.abs(scores[:, 0] - mean) / ((scores[:, 0] + mean + 1e-10) / 2)
  return deviation < threshold

def median_deviation(scores, mentions, correct, correct_mention, threshold):
  median = np.median(scores, axis=1)
  deviation = np.abs(scores[:, 0] - median) / (0.5 * (scores[:, 0] + median))
  return deviation < threshold

def string_similarity(scores, mentions, correct, correct_mention, threshold, method=None):
  sim = []
  for i, m in enumerate(mentions):
    sim.append(method.normalized_similarity(m[0].lower().strip(), correct_mention[i].lower().strip()) < threshold)
  return np.array(sim)

def classifier(scores, mentions, correct, correct_mention, threshold, classifier=None):
  X = StandardScaler().fit_transform(scores)
  y = np.array(correct)
  clf = classifier.fit(X, y)
  return clf, clf.predict(X)

HEURISTIC_MAP = {
  "threshold": threshold,
  "top_deviation": top_deviation,
  "dev_from_mean": mean_deviation,
  "dev_from_median": median_deviation,
  "logistic_regression": partial(classifier, classifier=LogisticRegression()),
  "hamming": partial(string_similarity, method=textdistance.hamming),
  "levenshtein": partial(string_similarity, method=textdistance.levenshtein),
  "jaccard": partial(string_similarity, method=textdistance.jaccard),
  "editex": partial(string_similarity, method=textdistance.editex),
  "svm": partial(classifier, classifier=SVC()),
  "dt": partial(classifier, classifier=DecisionTreeClassifier()),
}

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("-f", "--heuristic-function", required=True, choices=HEURISTIC_MAP.keys())
arg_parser.add_argument("-m", "--mhercl", required=True)
arg_parser.add_argument("-c", "--clef", required=True)
arg_parser.add_argument("-o", "--output", required=True)
arg_parser.add_argument("--sweep-resolution", type=float, default=0.001)

if __name__ == "__main__":
  args = arg_parser.parse_args()

  clef_df = pd.read_csv(args.clef)
  mhercl_df = pd.read_csv(args.mhercl)
  
  # extract top-k predictions
  clef_scores = np.array([eval(s) for s in clef_df.scores])
  clef_mentions = [eval(s) for s in clef_df.mentions_candidates]
  mhercl_scores = np.array([eval(s) for s in mhercl_df.scores])
  mhercl_mentions = [eval(s) for s in mhercl_df.mentions_candidates]
  
  clef_df["pred"] = clef_df.winner_qid
  clef_df["target"] = clef_df.QID_gold
  clef_df["is_nil"] = clef_df.QID_gold == "NIL"
  mhercl_df["pred"] = mhercl_df.winner_qid
  mhercl_df["target"] = mhercl_df.QID_gold
  mhercl_df["is_nil"] = mhercl_df.QID_gold == "NIL"

  # apply heuristics
  sweep_df = pd.DataFrame(columns=["method", "threshold", "result_clef", "result_mhercl"])
  
  if args.heuristic_function in ["logistic_regression", "svm", "dt"]:
    h = HEURISTIC_MAP[args.heuristic_function]
    clf, nil_candidates = h(clef_scores, clef_mentions, clef_df.is_nil.to_numpy(), clef_df.mentions_gold.to_list(), None)
    clef_df.loc[nil_candidates, "pred"] = "NIL"
    f1_clef = compute_f1_metric(clef_df)

    # compute on mhercl
    nil_candidates = clf.predict(StandardScaler().fit_transform(mhercl_scores))
    mhercl_df.loc[nil_candidates, "pred"] = "NIL"
    f1_mhercl = compute_f1_metric(mhercl_df)

    sweep_df.loc[len(sweep_df.index)] = (args.heuristic_function, None, f1_clef, f1_mhercl)
  else:
    for t in tqdm(np.linspace(0, 1, int(1 / args.sweep_resolution)), desc=f"{args.heuristic_function}"):
      h = HEURISTIC_MAP[args.heuristic_function]
      nil_candidates = h(clef_scores, clef_mentions, clef_df.is_nil.to_numpy(), clef_df.mentions_gold.to_list(), t)
      clef_df.loc[nil_candidates, "pred"] = "NIL"
      f1_clef = compute_f1_metric(clef_df)
      
      nil_candidates = h(mhercl_scores, mhercl_mentions, mhercl_df.is_nil.to_numpy(), mhercl_df.mentions_gold.to_list(), t)
      mhercl_df.loc[nil_candidates, "pred"] = "NIL"
      f1_mhercl = compute_f1_metric(mhercl_df)
      
      sweep_df.loc[len(sweep_df.index)] = (args.heuristic_function, t, f1_clef, f1_mhercl)
    
  sweep_df.to_csv(args.output)