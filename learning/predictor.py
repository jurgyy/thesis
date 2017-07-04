import numpy as np
from sklearn import ensemble
from sklearn.model_selection import cross_val_score
from sklearn.metrics import f1_score

from learning.confusion_matrix import ConfusionMatrix
from learning.plot import plot_features, plot_trees, plot_surface


def analyze_chads_vasc(data):
    cf = ConfusionMatrix(data["Target"], data["Data"], name="CHADS-VASc")
    return cf


def custom_f1(cutoff):
    def f1_cutoff(clf, x, y):
        ypred = np.array(clf.predict_proba(x)[:, 1] > cutoff).astype(int)
        return f1_score(y, ypred)

    return f1_cutoff


def predict(learn_x, learn_y, test_x, test_y, labels, n_features=.2, cutoff=.1, plot=False):
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
        cutoffs = np.arange(0.05, 0.5, 0.05)
        highest_mean, highest_cutoff = 0, 0
        for c in cutoffs:
            validated = cross_val_score(clf, learn_x, learn_y, cv=10, scoring=custom_f1(c))
            mean = np.mean(validated)

            print("Cutoff: {} with mean: {}".format(c, mean))
            if mean > highest_mean:
                highest_mean = mean
                highest_cutoff = c

        if highest_cutoff == 0:
            raise NotImplementedError

        print("Best Cutoff: {} with mean: {}".format(highest_cutoff, highest_mean))
        cutoff = highest_cutoff

    print("Fitting Reduced Dataset...")
    clf.fit(learn_x, learn_y)

    print("Predicting...")
    predictions = [1 if p[1] > cutoff else 0 for p in clf.predict_proba(test_x)]

    cf = ConfusionMatrix(test_y, predictions, name="Random Forest")

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

        plot_surface(clf, learn_x, learn_y, labels=labels)
    return cf
