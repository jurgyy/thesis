import numpy as np
from sklearn import ensemble
from sklearn.feature_selection import SelectFromModel
from sklearn.model_selection import train_test_split
# from sklearn.cross_validation import cross_val_score
from sklearn.model_selection import cross_val_score
from sklearn.metrics import f1_score
from sklearn.metrics.classification import UndefinedMetricWarning

from learning.confusion_matrix import ConfusionMatrix


def get_data(n_samples, n_useless_features):
    x = []
    y = []
    for i in range(n_samples):
        d = list(np.random.uniform(size=(3 + n_useless_features)))
        x.append(d)
        if d[0] > 0.95 or d[1] > 0.8 or d[2] > 0.6:
            if np.random.uniform() > 0.90:
                y.append(1)
            else:
                y.append(0)
        else:
            y.append(0)
    return x, y


def split_data(x, y, test_rate):
    test_size = int(len(x) * test_rate)

    test_x = x[:test_size]
    test_y = y[:test_size]
    learn_x = x[test_size:]
    learn_y = y[test_size:]

    return learn_x, learn_y, test_x, test_y


def cutoff_predict(clf, x, cutoff):
    return np.array(clf.predict_proba(x)[:, 1] > cutoff).astype(int)


def custom_f1(cutoff):
    def f1_cutoff(clf, x, y):
        ypred = cutoff_predict(clf, x, cutoff)
        return f1_score(y, ypred)

    return f1_cutoff


def main():
    x, y = get_data(10000, 200)
    learn_x, learn_y, test_x, test_y = split_data(x, y, test_rate=0.3)

    class_weight = None
    clf = ensemble.RandomForestClassifier(n_estimators=100, n_jobs=-1, class_weight=class_weight)

    cutoffs = np.arange(0.1, 0.9, 0.1)
    highest_mean, highest_cutoff = 0, 0
    for c in cutoffs:
        validated = cross_val_score(clf, learn_x, learn_y, cv=10, scoring=custom_f1(c))
        mean = np.mean(validated)
        if mean > highest_mean:
            highest_mean = mean
            highest_cutoff = c

    if highest_cutoff == 0:
        raise NotImplementedError

    print("Cutoff: {} with mean: {}".format(highest_cutoff, highest_mean))

    clf.fit(learn_x, learn_y)
    # clf.fit(learn_x, learn_y, sample_weight=[1 if i == 1 else 1 for i in learn_y])

    # labels = list(range(len(learn_x[0])))
    # importances = clf.feature_importances_
    # importance_threshold = 0.1
    #
    # importances, labels = zip(*sorted(zip(importances, labels), reverse=True))
    # important_features = [l for (l, v) in zip(labels, importances) if v > importance_threshold]
    # for l, v in zip(labels, importances):
    #     if v < importance_threshold:
    #         break
    #     print(l, v)
    #
    # print("Important features: {}".format(important_features))

    # predictions = clf.predict(test_x)
    predictions = [1 if p[1] > highest_cutoff else 0 for p in clf.predict_proba(test_x)]
    cf_all = ConfusionMatrix(test_y, predictions, name="All features")
    cf_all.dump()

    # sfm = SelectFromModel(clf, threshold=importance_threshold)
    # sfm.fit(learn_x, learn_y)
    #
    # learn_x_imp = sfm.transform(learn_x)
    # test_x_imp = sfm.transform(test_x)
    # clf_imp = ensemble.RandomForestClassifier(n_estimators=100, n_jobs=-1, class_weight=class_weight)
    # clf_imp.fit(learn_x_imp, learn_y, sample_weight=[2 if i == 1 else 1 for i in learn_y])
    #
    # predictions_imp = clf_imp.predict(test_x_imp)
    #
    # cf_imp = ConfusionMatrix(test_y, predictions_imp, name="Important features")
    # cf_imp.dump()


if __name__ == "__main__":
    main()
