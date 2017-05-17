import pydot
import matplotlib.pyplot as plt
from sklearn import ensemble
from sklearn.tree import export_graphviz

from learning.confusion_matrix import ConfusionMatrix


def analyze_chads_vasc(data):
    cf = ConfusionMatrix(data["Target"], data["Data"], name="CHADS-VASc")
    return cf


def predict(learn_data, test_data, plot=False):
    clf = ensemble.RandomForestClassifier(n_estimators=100, n_jobs=-1)

    print("# Learn Data Size: {}".format(len(learn_data["Data"])))
    print("# Test Data Size:  {}".format(len(test_data["Data"])))
    print("# Features:        {}".format(len(learn_data["Data"][0])))

    clf.fit(learn_data["Data"], learn_data["Target"])

    predictions = clf.predict(test_data["Data"])

    cf = ConfusionMatrix(test_data["Target"], predictions, name="Random Forest")

    if plot:
        try:
            plot_features(clf, learn_data["Data Labels"])
        except:
            print("Error plotting features. Continuing...")
        try:
            plot_trees(clf, learn_data["Data Labels"], n=3)
        except:
            print("Error plotting trees. Continuing...")
    return cf


def plot_features(clf, labels):
    print("Plotting Important features...")
    importances = clf.feature_importances_
    importances, labels = zip(*sorted(zip(importances, labels), reverse=True))
    for i, v in enumerate(importances):
        if v < 0.002:
            importances = importances[:i]
            labels = labels[:i]
            break

    xs = range(len(importances))

    dpi = 100
    plt.figure(figsize=(780 / dpi, (len(labels) * 17) / dpi), dpi=dpi)
    plt.barh(xs, importances, align='center')
    plt.title("Feature Importance")
    plt.yticks(xs, labels)
    plt.ylim(-1, len(labels) + 1)
    plt.savefig("output/feature_importance.png", bbox_inches='tight')


def plot_trees(clf, labels, n=3):
    print("Outputting first three trees")
    for i in range(n):
        export_graphviz(clf.estimators_[i],
                        feature_names=labels,
                        filled=True,
                        rounded=True,
                        out_file="output/tree.dot")
        (graph,) = pydot.graph_from_dot_file('output/tree.dot')
        graph.write_png('output/new_tree_{}.png'.format(i), prog="graphviz/bin/dot.exe")
