import numpy as np
from sklearn import ensemble
from sklearn.model_selection import cross_val_score
from sklearn.metrics import f1_score

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
    clf.fit(learn_x, learn_y)

    predict_y = clf.predict(test_x)
    cf_pre = ConfusionMatrix(test_y, predict_y, name="Priory")
    print("Pre F1 Score: {}".format(cf_pre.f1_score()))

    importances, labels = zip(*sorted(zip(clf.feature_importances_, range(len(learn_x[0]))), reverse=True))
    feature_rate = 0.2
    num_features = int(len(importances) * feature_rate)
    exclude_labels = labels[num_features:]
    learn_x = np.delete(learn_x, exclude_labels, axis=1)
    test_x = np.delete(test_x, exclude_labels, axis=1)
    clf.fit(learn_x, learn_y)

    predict_y = clf.predict(test_x)
    cf_mid = ConfusionMatrix(test_y, predict_y, name="Feature Selection")
    print("Feature Selection F1 Score: {}".format(cf_mid.f1_score()))

    cutoff = 0.1
    if cutoff is None:
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
        cutoff = highest_cutoff

    predictions = [1 if p[1] > cutoff else 0 for p in clf.predict_proba(test_x)]
    cf_post = ConfusionMatrix(test_y, predictions, name="Cutoff and Selection")
    print("Post F1 Score: {}".format(cf_post.f1_score()))
    print("--------------------------------------------")
    cf_post.dump()


if __name__ == "__main__":
    main()
