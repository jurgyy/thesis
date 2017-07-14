import numpy as np
from sklearn import ensemble
from sklearn.model_selection import cross_val_score, GroupKFold
from sklearn import metrics

from learning.confusion_matrix import ConfusionMatrix
from learning.plot import *


def custom_score(cutoff, beta):
    def score_cutoff(clf, x, y):
        ypred = np.array(clf.predict_proba(x)[:, 1] > cutoff).astype(int)
        cm = ConfusionMatrix(y, ypred)
        r = cm.tpr
        s = cm.tnr
        return (beta ** 2 + 1) * (s * r) / (beta ** 2 * s + r)

    return score_cutoff


def predict(x_learn, y_learn, groups, x_test, y_test, labels, n_features=.4, cutoff=.1, plot=False):
    clf = ensemble.RandomForestClassifier(n_estimators=100, n_jobs=-1, class_weight='balanced')

    print("# Learn Data Size:  {}".format(len(x_learn)))
    print("# Positive Target:  {}".format(sum(y_learn)))
    print("# Test Data Size:   {}".format(len(x_test)))
    print("# Positive Target:  {}".format(sum(y_test)))
    print("# Features:         {}".format(len(labels)))

    print("Fitting Whole Dataset... ")
    clf.fit(x_learn, y_learn)

    print("Reducing Feature Space... ")
    importances, indexes = zip(*sorted(zip(clf.feature_importances_, range(len(x_learn[0]))), reverse=True))

    if type(n_features) == float:
        n_features = int(len(importances) * n_features)

    excluded_indeces = indexes[n_features:]
    x_learn = np.delete(x_learn, excluded_indeces, axis=1)
    x_test = np.delete(x_test, excluded_indeces, axis=1)
    labels = np.delete(labels, excluded_indeces)

    print("# Features Reduced: {}".format(len(labels)))

    if cutoff is None:
        print("Finding Correct Probability Cutoff...")

        # In the unbalanced data set the cutoff will most likely be below .5,
        # to safe time, no cutoffs > .5 are checked.

        gkf = GroupKFold(n_splits=10)

        cutoffs = np.arange(0.05, 0.15, 0.025)
        beta = 3
        cutoff_scores = []
        highest_mean, highest_cutoff = 0, 0
        for c in cutoffs:
            tmp_clf = ensemble.RandomForestClassifier(n_estimators=100, n_jobs=-1, class_weight='balanced')
            validated = cross_val_score(tmp_clf, x_learn, y_learn, cv=gkf.split(x_learn, y_learn, groups),
                                        scoring=custom_score(c, beta))
            cutoff_scores.append(validated)
            mean = np.mean(validated)

            print("Cutoff: {} with mean: {} | {}".format(c, mean, validated))
            if mean > highest_mean:
                highest_mean = mean
                highest_cutoff = c

        if highest_cutoff == 0:
            raise NotImplementedError

        print("Best Cutoff: {} with mean: {}".format(highest_cutoff, highest_mean))
        cutoff = highest_cutoff

        if plot:
            plot_cutoffs(cutoffs, cutoff_scores, ylabel="$S_{%s}$ Score" % beta)

    print("Fitting Reduced Dataset...")
    clf.fit(x_learn, y_learn)

    print("Predicting...")
    predictions = [1 if p[1] > cutoff else 0 for p in clf.predict_proba(x_test)]

    cm = ConfusionMatrix(y_test, predictions, name="Random Forest")

    if plot:
        try:
            plot_features(clf, labels)
        except:
            print("Error plotting features. Continuing...")
        try:
            # plot_trees(clf, labels, n=1)
            pass
        except:
            print("Error plotting trees. Continuing...")

        plot_surface(clf, x_learn, y_learn, labels=labels, cutoff=cutoff)
    return cm
