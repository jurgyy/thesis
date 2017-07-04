import pydot
import numpy as np
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
    plt.savefig("output/feature_importance.png", bbox_inches='tight')


def plot_trees(clf, labels, n=3):
    print("Outputting first {} trees".format(n))
    for i in range(n):
        export_graphviz(clf.estimators_[i],
                        feature_names=labels,
                        filled=True,
                        rounded=True,
                        out_file="output/tree.dot")
        (graph,) = pydot.graph_from_dot_file('output/tree.dot')
        graph.write_png('output/new_tree_{}.png'.format(i), prog="graphviz/bin/dot.exe")


def plot_surface(clf, x, y, labels=None, cutoff=None):
    plt.figure()
    print("Plotting surface...")
    importances, indexes = zip(*sorted(zip(clf.feature_importances_, range(len(x[0]))), reverse=True))
    x = np.array(x)[:, indexes[:2]]

    x_min, x_max = x[:, 0].min(), x[:, 0].max()
    y_min, y_max = x[:, 1].min(), x[:, 1].max()
    x_step = (x_max - x_min) / 100
    y_step = (y_max - y_min) / 100
    xx, yy = np.meshgrid(np.arange(x_min, x_max, x_step), np.arange(y_min, y_max, y_step))

    clf.fit(x, y)
    Z = clf.predict_proba(np.c_[xx.ravel(), yy.ravel()])[:, 1]
    Z = Z.reshape(xx.shape)

    cs = plt.contourf(xx, yy, Z, cmap=plt.cm.coolwarm)
    cbar = plt.colorbar(cs)
    cbar.ax.set_ylabel('Probability')
    if cutoff is not None:
        cs_lines = plt.contour(cs, levels=[cutoff], colors='black')
        cbar.add_lines(cs_lines)

    plt.scatter(x[:, 0], x[:, 1], c=y, cmap=plt.cm.Paired, alpha=0.2)

    if labels is not None:
        plt.xlabel(labels[indexes[0]])
        plt.ylabel(labels[indexes[1]])

    plt.title("Surface plot of two most important features")
    plt.savefig("output/surface.png", bbox_inches='tight')
