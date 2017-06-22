import pydot
from matplotlib import pyplot as plt
from sklearn.tree import export_graphviz


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
    plt.savefig("../output/feature_importance.png", bbox_inches='tight')


def plot_trees(clf, labels, n=3):
    print("Outputting first three trees")
    for i in range(n):
        export_graphviz(clf,  # clf.estimators_[i],
                        feature_names=labels,
                        filled=True,
                        rounded=True,
                        out_file="output/tree.dot")
        (graph,) = pydot.graph_from_dot_file('output/tree.dot')
        graph.write_png('../output/new_tree_{}.png'.format(i), prog="graphviz/bin/dot.exe")