""""
The goal of this file was to find out if the Decision Trees are able to learn diagnoses if 'no diagnosis'
in the 'days-since' features is encoded as an unattainably large value.
It seems like it is working as intended.
"""
from sklearn.tree import DecisionTreeClassifier
from matplotlib import pyplot as plt
import numpy as np

plot_max = 2


def plot_data(x, y, clf):
    a_0, b_0 = [], []
    a_1, b_1 = [], []

    for i in range(len(x)):
        af, bf = x[i]
        if y[i] == 0:
            a_0.append(af)
            b_0.append(bf)
        else:
            a_1.append(af)
            b_1.append(bf)

    npixels = 200
    x = np.linspace(0, plot_max, npixels)
    y = np.linspace(0, plot_max, npixels)
    mesh = []
    for i in x:
        for j in y:
            mesh.append([j, i])  # not exactly sure why [j, i] instead of [i, j]
    bg = clf.predict(mesh)
    bg = np.reshape(bg, (npixels, npixels))
    plt.pcolor(x, y, bg, cmap='plasma')

    plt.scatter(a_0, b_0, marker='o', cmap='brg')
    plt.scatter(a_1, b_1, marker='x', cmap='brg')

    plt.xlabel("a")
    plt.ylabel("b")
    plt.xlim(0, plot_max + 0.05)
    plt.ylim(0, plot_max + 0.05)

    plt.savefig("../output/examples/surface", bbox_inches='tight')


def random_dif():
    return np.random.random() / 5 - 0.1


def distance(a, b):
    return np.linalg.norm(np.array(a) - np.array(b))


def generate_data(n):
    x = []
    y = []
    for i in range(n):
        a = 1 if np.random.random() > 0.1 else 0
        b = 1 if np.random.random() > 0.1 else 0
        v = (a, np.random.random() if a else plot_max,
             b, np.random.random() if b else plot_max)
        x.append((v[1], v[3]))
        # if distance([v[1], v[3]], [0.5, 0.5]) < 0.4:
        # if 0.3 < v[1] < 0.7 and 0.2 < v[3]:
        # if distance([v[1], v[3]], [np.random.normal(1, 0.3), np.random.normal(1, 0.3)]) < 0.3: # < v[1] and np.random.normal(1, 0.3) < v[3]:
        n = np.random.normal(1, 0.1)
        if np.abs(v[1] - n) < 0.3 or np.abs(v[3] - n) < 0.3:
            y.append(1)
        else:
            y.append(0)

    return x, y


def fit(x, y):
    clf = DecisionTreeClassifier(min_samples_leaf=50)
    clf.fit(x, y)
    return clf


def get_lineage(tree, feature_names):
    left = tree.tree_.children_left
    right = tree.tree_.children_right
    threshold = tree.tree_.threshold
    features = [feature_names[i] for i in tree.tree_.feature]

    # get ids of child nodes
    idx = np.argwhere(left == -1)[:, 0]

    def recurse(left, right, child, lineage=None):
        if lineage is None:
            lineage = [child]
        if child in left:
            parent = np.where(left == child)[0].item()
            split = 'l'
        else:
            parent = np.where(right == child)[0].item()
            split = 'r'

        lineage.append((parent, split, threshold[parent], features[parent]))

        if parent == 0:
            lineage.reverse()
            return lineage
        else:
            return recurse(left, right, parent, lineage)

    lin = []
    for child in idx:
        lin.append([])
        for node in recurse(left, right, child):
            # print(node)
            if type(node) == type(child) and node == child:
                lin[-1].append(np.argmax(tree.tree_.value[child][0]))
            else:
                lin[-1].append(node)
    return lin


if __name__ == "__main__":
    np.random.seed(3)

    x, y = generate_data(5000)
    clf = fit(x, y)
    lin = get_lineage(clf, ["af", "bf"])

    np.set_printoptions(threshold=np.nan)
    # print(clf.predict([[0.05, v] for v in np.arange(0.1, 0.5, 0.0001)]))

    plot_data(x, y, clf)
