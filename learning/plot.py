import pydot
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import patches as mpatches
from matplotlib import markers
from sklearn.tree import export_graphviz

from disease_groups import *


def plot_features(clf, labels, nlabels=25):
    print("Plotting Important features...")
    importances = clf.feature_importances_
    importances, labels = zip(*sorted(zip(importances, labels), reverse=True))

    if type(nlabels) == float:
        nlabels = int(len(importances) * nlabels)
        importances = importances[:nlabels]
        labels = labels[:labels]

        # for i, v in enumerate(importances):
        #     if v < 0.002:
        #         importances = importances[:i]
        #         labels = labels[:i]
        #         break
    else:
        importances = importances[:nlabels]
        labels = labels[:nlabels]

    xs = range(len(importances))

    groups = [(chads_vasc_c, "C", plt.cm.tab10(3)),
              (chads_vasc_h, "H", plt.cm.tab10(4)),
              (chads_vasc_d, "D", plt.cm.tab10(5)),
              (chads_vasc_s, "S", plt.cm.tab10(6)),
              (chads_vasc_v, "V", plt.cm.tab10(7))]

    colors = []
    for label in labels:
        if label == "Age":
            colors.append(plt.cm.tab10(1))
            continue
        elif label == "Gender":
            colors.append(plt.cm.tab10(2))
            continue

        in_group = False
        for g, letter, color in groups:
            if in_group:
                break
            for disease in g:
                if label.lower() == str(disease).lower():
                    in_group = True
                    colors.append(color)
                    break
        if not in_group:
            colors.append(plt.cm.tab10(0))

    legend_labels = ["New", "Age", "Gender"] + [letter for _, letter, _ in groups]

    handles = [mpatches.Patch(color=plt.cm.tab10(i), label=legend_labels[i]) for i in range(len(legend_labels))]

    dpi = 100
    plt.figure(figsize=(480 / dpi, (len(labels) * 17) / dpi), dpi=dpi)
    plt.barh(xs, importances, align='center', color=colors)
    plt.title("Feature Importance")
    plt.yticks(xs, labels)
    plt.ylim(-1, len(labels) + 1)
    plt.legend(handles=handles)
    plt.savefig("output/learning/feature_importance.png", bbox_inches='tight')


def plot_trees(clf, labels, n=3):
    print("Outputting first {} trees".format(n))
    for i in range(n):
        export_graphviz(clf.estimators_[i],
                        feature_names=labels,
                        filled=True,
                        rounded=True,
                        out_file="output/learning/tree.dot")
        (graph,) = pydot.graph_from_dot_file('output/learning/tree.dot')
        graph.write_png('output/learning/new_tree_{}.png'.format(i), prog="graphviz/bin/dot.exe")


def plot_cutoffs(cutoffs, data, ylabel=""):
    print("Plotting cutoff box plots...")
    fig = plt.figure(figsize=(4, 3))
    ax = fig.add_subplot(111)

    ax.boxplot(data, whis='range')

    ax.set_xlabel("Cutoff")
    ax.set_ylabel(ylabel)
    ax.set_xticklabels(cutoffs, rotation=45, ha='right')
    plt.title("10-fold cross validated scores with different cutoffs")
    plt.savefig("output/learning/cutoff_boxplot", bbox_inches='tight')


def plot_matrices(confusion_matrices, s_beta):
    fig = plt.figure(figsize=(8, 4))
    ax = fig.add_subplot(111)

    labels = ["True Positive\nRate", "False Positive\nRate", "False Negative\nRate", "True Negative\nRate",
              "$S_3$ Score"]
    n = len(confusion_matrices)
    ind = np.arange(len(labels))
    w = 0.8
    offsets = np.arange(0, w, w/n) - 0.5 * (n - 1) * w/n

    rects, names = [], []
    for i, cm in enumerate(confusion_matrices):
        names.append(cm.name)
        y = [cm.tpr, cm.fpr, cm.fnr, cm.tnr, cm.s_beta(s_beta)]
        x = [j + offsets[i] for j in range(len(y))]

        r = ax.bar(x, y, width=w/n)
        rects.append(r)

    ax.set_ylim(0, 1)
    ax.set_xticks(ind)
    ax.set_xticklabels(labels)
    ax.legend(rects, names, loc=3)
    ax.yaxis.grid(True)
    ax.set_axisbelow(True)

    plt.title("Performance comparison of different models")
    plt.savefig("output/learning/performance", bbox_inches='tight')


def round_nearest(num, order):
    return np.round(num * order) / order


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

    cs = plt.contourf(xx, yy, Z, np.arange(0, 1, .02), vmin=0, vmax=1, cmap=plt.cm.coolwarm)
    cbar = plt.colorbar(cs)
    cbar.ax.set_ylim(0, 1)
    cbar.ax.set_ylabel('Probability $y = 1$')
    if cutoff is not None:
        cs_lines = plt.contour(cs, levels=[cutoff], style="--", colors='black')
        cbar.add_lines(cs_lines)

        cbar_labels = [w.get_text() for w in cbar.ax.get_yticklabels()]
        cbar_locs = [round_nearest(v, 20) for v in cbar.ax.get_yticks()]
        if cutoff in cbar_locs:
            i = cbar_locs.index(cutoff)
            cbar_labels[i] = "{} {}".format(cbar_labels[i], "Cutoff")
        else:
            cbar_locs.append(cutoff)
            cbar_labels.append("Cutoff")

        cbar.set_ticklabels(cbar_labels)
        cbar.set_ticks(cbar_locs)

    # TODO: optimize
    x0 = [v for v, w in zip(x[:, 0], y) if w == 0]
    y0 = [v for v, w in zip(x[:, 1], y) if w == 0]
    x1 = [v for v, w in zip(x[:, 0], y) if w == 1]
    y1 = [v for v, w in zip(x[:, 1], y) if w == 1]
    plt.scatter(x0, y0, c=plt.cm.Paired(0), label="No Stroke")
    plt.scatter(x1, y1, c=plt.cm.Paired(11), label="Stroke")
    legend = plt.legend(bbox_to_anchor=(1.6, 1))

    if labels is not None:
        plt.xlabel(labels[indexes[0]])
        plt.ylabel(labels[indexes[1]])

    plt.title("Surface plot of two most important features")
    plt.savefig("output/learning/surface.png", bbox_extra_artists=(legend,), bbox_inches='tight')
