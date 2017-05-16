import pydot
import matplotlib.pyplot as plt
from sklearn import ensemble
from sklearn.tree import export_graphviz

from learning.confusion_matrix import ConfusionMatrix


def analyze_chads_vasc(data):
    cf = ConfusionMatrix(data["Target"], data["Data"], name="CHADS-VASc")
    return cf


def predict(learn_data, test_data, plot=False):
    clf = ensemble.RandomForestClassifier(n_estimators=100)

    print("# Learn Data Size: {}".format(len(learn_data["Data"])))
    print("# Test Data Size:  {}".format(len(test_data["Data"])))
    print("# Features:        {}".format(len(learn_data["Data"][0])))

    clf.fit(learn_data["Data"], learn_data["Target"])

    predictions = clf.predict(test_data["Data"])

    cf = ConfusionMatrix(test_data["Target"], predictions, name="Random Forest")

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

        dpi = 100
        plt.figure(figsize=(780 / dpi, (len(ls)*17) / dpi), dpi=dpi)
        plt.barh(xs, importances, align='center')
        plt.title("Feature Importance")
        plt.yticks(xs, ls)
        plt.ylim(-1, len(ls) + 1)
        plt.savefig("output/feature_importance.png", bbox_inches='tight')

        print("Outputting first three trees")
        for i in range(3):
            export_graphviz(clf.estimators_[i],
                            feature_names=learn_data["Data Labels"],
                            filled=True,
                            rounded=True,
                            out_file="output/tree.dot")
            (graph,) = pydot.graph_from_dot_file('output/tree.dot')
            graph.write_png('output/tree_{}.png'.format(i), prog="graphviz/bin/dot.exe")

    return cf
