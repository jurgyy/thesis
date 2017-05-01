import matplotlib.pyplot as plt
from sklearn import ensemble


def predict(learn_data, test_data):
    clf = ensemble.RandomForestClassifier(n_estimators=100)

    clf.fit(learn_data["Data"], learn_data["Target"])

    predictions = clf.predict(test_data["Data"])

    correct = 0
    wrong = 0
    for i in range(len(test_data["Data"])):
        if test_data["Target"][i] == predictions[i]:
            correct += 1
        else:
            wrong += 1

    print("Correct: {}\nWrong: {}".format(correct, wrong))

    print("Plotting Important features...")
    importances = clf.feature_importances_
    ls = learn_data["Data Labels"]
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

