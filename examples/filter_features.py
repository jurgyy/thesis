import numpy as np
from sklearn import ensemble


def get_data(n_samples):
    x = []
    y = []
    for i in range(n_samples):
        d = list(np.random.uniform(size=5))
        x.append(d)
        if d[0] > 0.6 or d[1] > 0.8 or d[2] > 0.95:
            y.append([1])
        else:
            y.append([0])
    return x, y


def split_data(x, y, test_rate):
    test_size = int(len(x) * test_rate)

    test_x = x[:test_size]
    test_y = y[:test_size]
    learn_x = x[test_size:]
    learn_y = y[test_size:]

    return learn_x, learn_y, test_x, test_y


def main():
    x, y = get_data(10000)
    learn_x, learn_y, test_x, test_y = split_data(x, y, test_rate=0.3)

    clf = ensemble.RandomForestClassifier(n_estimators=100, n_jobs=-1, class_weight='balanced')

    clf.fit(learn_x, learn_y)

    labels = list(range(5))
    importances = clf.feature_importances_
    importances, labels = zip(*sorted(zip(importances, labels), reverse=True))
    for l, v in zip(labels, importances):
        print(l, v)


if __name__ == "__main__":
    main()
