import matplotlib.pyplot as plt
from sklearn import ensemble


def predict(learn_data, test_data):
    clf = ensemble.RandomForestClassifier(n_estimators=100)

    clf.fit(learn_data["Data"], learn_data["Target"])

    predictions = clf.predict(test_data["Data"])

    # True Positives, True Negatives, False Positives, False Negatives
    # TP: Stroke in 12 months, predictor target == 1
    # TN: No stroke in 12 months, predictor target == 0
    # FP: No stroke in 12 months, predictor target == 1
    # FN: Stroke in 12 months, predictor target == 0
    TP = TN = FP = FN = 0
    for i in range(len(test_data["Data"])):
        target = test_data["Target"][i]
        prediction = predictions[i]
        if target == prediction == 1:
            TP += 1
        elif target == prediction == 0:
            TN += 1
        elif target == 1 and prediction == 0:
            FN += 1
        else:
            FP += 1

    print("True Positive:  {}".format(TP))
    print("True Negative:  {}".format(TN))
    print("False Positive: {}".format(FP))
    print("False Negative: {}".format(FN))

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

