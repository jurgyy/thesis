import matplotlib.pyplot as plt
from sklearn import ensemble

from learning.confusion_matrix import ConfusionMatrix


def analyze_chads_vasc(data):
    cf = ConfusionMatrix(data["Data"], data["Target"], name="CHADS-VASc")
    return cf


def predict(learn_data, test_data, plot=False):
    clf = ensemble.RandomForestClassifier(n_estimators=100)

    clf.fit(learn_data["Data"], learn_data["Target"])

    predictions = clf.predict(test_data["Data"])

    cf = ConfusionMatrix(predictions, test_data["Target"], name="Random Forest")

    if plot:
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

    return cf
