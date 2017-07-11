import numpy as np
from sklearn import ensemble
from sklearn.model_selection import cross_val_score, GroupKFold
from sklearn import metrics

from learning.confusion_matrix import ConfusionMatrix
from learning.plot import *


def analyze_chads_vasc(data):
    cm = ConfusionMatrix(data["Target"], data["Data"], name="CHADS-VASc")
    return cm


def custom_score(cutoff, beta):
    def score_cutoff(clf, x, y):
        ypred = np.array(clf.predict_proba(x)[:, 1] > cutoff).astype(int)
        cm = ConfusionMatrix(y, ypred)
        r = cm.tpr
        s = cm.tnr
        print(cm.calculate_matrix(), r, s)
        return (beta ** 2 + 1) * (s * r) / (beta ** 2 * s + r)

    return score_cutoff


def predict(learn_x, learn_y, groups, test_x, test_y, labels, n_features=.2, cutoff=.1, plot=False):
    clf = ensemble.RandomForestClassifier(n_estimators=100, n_jobs=-1, class_weight='balanced')

    print("# Learn Data Size: {}".format(len(learn_x)))
    print("# Positive Target: {}".format(sum(learn_y)))
    print("# Test Data Size:  {}".format(len(test_x)))
    print("# Positive Target: {}".format(sum(test_y)))
    print("# Features:        {}".format(len(learn_x[0])))

    print("Fitting Whole Dataset... ")
    clf.fit(learn_x, learn_y)

    print("Reducing Feature Space... ")
    importances, indexes = zip(*sorted(zip(clf.feature_importances_, range(len(learn_x[0]))), reverse=True))

    if type(n_features) == float:
        n_features = int(len(importances) * n_features)

    exclude_indeces = indexes[n_features:]
    learn_x = np.delete(learn_x, exclude_indeces, axis=1)
    test_x = np.delete(test_x, exclude_indeces, axis=1)
    labels = np.delete(labels, exclude_indeces)

    if cutoff is None:
        print("Finding Correct Probability Cutoff...")

        # In the unbalanced data set the cutoff will most likely be below .5,
        # to safe time, no cutoffs > .5 are checked.

        gkf = GroupKFold(n_splits=10)

        cutoffs = np.arange(0.025, 0.275, 0.025)
        beta = 2
        cutoff_scores = []
        highest_mean, highest_cutoff = 0, 0
        for c in cutoffs:
            tmp_clf = ensemble.RandomForestClassifier(n_estimators=100, n_jobs=-1, class_weight='balanced')
            validated = cross_val_score(tmp_clf, learn_x, learn_y, cv=gkf.split(learn_x, learn_y, groups),
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
    clf.fit(learn_x, learn_y)

    print("Predicting...")
    predictions = [1 if p[1] > cutoff else 0 for p in clf.predict_proba(test_x)]

    cm = ConfusionMatrix(test_y, predictions, name="Random Forest")

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

        plot_surface(clf, learn_x, learn_y, labels=labels, cutoff=cutoff)
    return cm
