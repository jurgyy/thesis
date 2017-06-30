from sklearn import ensemble

from learning.confusion_matrix import ConfusionMatrix
from learning.plot import plot_features, plot_trees


def analyze_chads_vasc(data):
    cf = ConfusionMatrix(data["Target"], data["Data"], name="CHADS-VASc")
    return cf


def predict(learn_features, learn_target, test_features, test_target, labels, plot=False):
    clf = ensemble.RandomForestClassifier(n_estimators=100, n_jobs=-1, class_weight='balanced')

    print("# Learn Data Size: {}".format(len(learn_features)))
    print("# Positive Target: {}".format(sum(learn_target)))
    print("# Test Data Size:  {}".format(len(test_features)))
    print("# Positive Target: {}".format(sum(test_target)))
    print("# Features:        {}".format(len(learn_features[0])))

    print("Fitting... ")
    clf.fit(learn_features, learn_target)
    print("Predicting...")
    predictions = clf.predict(test_features)
    print("Predictions:\n{}, {}".format(sum(predictions), predictions))
    # for i in range(len(predictions)):
    #     if predictions[i]:
    #         print(predictions[i], test_target[i])

    cf = ConfusionMatrix(test_target, predictions, name="Random Forest")

    if plot:
        try:
            plot_features(clf, labels)
        except:
            print("Error plotting features. Continuing...")
        try:
            pass
            # plot_trees(clf, labels, n=3)
        except:
            print("Error plotting trees. Continuing...")
    return cf
