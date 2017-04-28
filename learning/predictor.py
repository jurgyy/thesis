import random

import matplotlib.pyplot as plt
from sklearn import ensemble


def random_list_split(lst, rate):
    left_size = round(len(lst) * (1 - rate))

    random.shuffle(lst)
    return lst[0:left_size], lst[left_size:]


def merge_data_target(data, target):
    merge = list(zip(data, target))
    return merge


def split_data_target(merge):
    data = []
    target = []
    data[:], target[:] = zip(*merge)

    return data, target


def predict(input):
    clf = ensemble.RandomForestClassifier(n_estimators=100)

    data = merge_data_target(input["Data"], input["Target"])
    learn_set, test_set = random_list_split(data, 0.3)

    learn_data, learn_target = split_data_target(learn_set)
    test_data, test_target = split_data_target(test_set)

    clf.fit(learn_data, learn_target)

    predictions = clf.predict(test_data)

    correct = 0
    wrong = 0
    for i in range(len(test_data)):
        if test_target[i] == predictions[i]:
            correct += 1
        else:
            wrong += 1

    print("Correct: {}\nWrong: {}".format(correct, wrong))

    print("Plotting Important features...")
    importances = clf.feature_importances_
    ls = input["Data Labels"]
    importances, ls = zip(*sorted(zip(importances, ls), reverse=True))
    for i, v in enumerate(importances):
        if v < 0.002:
            importances = importances[:i]
            ls = ls[:i]
            break

    xs = range(len(importances))

    plt.barh(xs, importances)
    plt.title("Feature Importance")
    plt.yticks(xs, ls)
    plt.show()

