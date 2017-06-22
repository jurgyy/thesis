""""
The goal of this file was to get more insight in the inner workings of the split algorithms.
"""
import timeit

import numpy as np
import matplotlib.pyplot as plt


def gini_index(p):
    return 2 * p * (1 - p)


def normalized_gini_index(p):
    return 2 * gini_index(p)


def cross_entropy(p):
    with np.errstate(divide='ignore', invalid='ignore'):
        return p * np.log(np.divide(1, p)) + (1 - p) * np.log(np.divide(1, (1 - p)))


def normalized_cross_entropy(p):
    with np.errstate(divide='ignore', invalid='ignore'):
        return np.divide(1, np.log(2)) * cross_entropy(p)


def misclassiﬁcation_error(p):
    return np.array([1 - max([v, 1 - v]) for v in p])


def normalized_misclassiﬁcation_error(p):
    return 2 * misclassiﬁcation_error(p)


def plot_functions():
    epsilon = 10 ** -6
    step = 0.002
    t1 = np.arange(0.0, 1.0 + step, step)
    t1 += epsilon

    plt.figure(1)
    plt.subplot(111)
    plt.plot(t1, gini_index(t1), 'C0', label="Gini index")
    plt.plot(t1, normalized_gini_index(t1), 'C0', linestyle='--')

    plt.plot(t1, cross_entropy(t1), 'C1', label="Cross-Entropy")
    plt.plot(t1, normalized_cross_entropy(t1), 'C1', linestyle='--')

    plt.plot(t1, misclassiﬁcation_error(t1), 'C2', label="Misclassification\nError")
    plt.plot(t1, normalized_misclassiﬁcation_error(t1), 'C2', linestyle='--')

    plt.xlabel("p")
    plt.legend(loc="upper right")

    plt.grid()
    plt.xlim(0, 1)
    plt.ylim(0, 1.1)

    plt.savefig("output/cost_functions.png", bbox_inches='tight')


def calculate_cost(node_pair, classes, cost_function=gini_index):
    cost = 0.0
    class_k = classes[1]
    for node in node_pair:
        size = len(node)
        if size == 0:
            continue
        p = get_portion(node, class_k)
        cost += cost_function(p)
    return cost


def get_portion(node, class_k):
    return sum([1 if target == class_k else 0 for (feature, target) in node]) / len(node)


def get_split(index, value, features, target):
    left, right = list(), list()
    for x, y in zip(features, target):
        if x[index] < value:
            left.append((x, y))
        else:
            right.append((x, y))
    return left, right


def best_split(data):
    features = data["Data"]
    target = data["Target"]

    classes = list(set(target))
    n_features = len(features[0])
    best_node_pair, best_cost, split_value = None, float('inf'), -1

    for i in range(n_features):
        for x, y in zip(features, target):
            node_pair = get_split(i, x[i], features, target)
            cost = calculate_cost(node_pair, classes, gini_index)
            # print('X%d < %.3f Gini=%.3f' % ((i + 1), x[i], cost))
            if cost < best_cost:
                best_cost, best_node_pair, split_value = cost, node_pair, x[i]

    return best_cost, best_node_pair, split_value


def best_split_sorted(data):
    features = data["Data"]
    target = data["Target"]

    target_vector = target.reshape(len(features), 1)
    matrix = np.append(features, target_vector)

    classes = list(set(target))
    n_features = len(features[0])
    best_node_pair, best_cost, split_value = None, float('inf'), -1

    for i in range(n_features):
        last_node_pair, last_cost, last_value = None, float('inf'), -1
        m_sorted = matrix[matrix[:, i].argsort()]

        for row in m_sorted:
            x, y = row[:-1], row[-1]

            node_pair = get_split(i, x[i], features, target)
            cost = calculate_cost(node_pair, classes, gini_index)
            # print('X%d < %.3f Gini=%.3f' % ((i + 1), x[i], cost))

            if cost > last_cost:
                if last_cost < best_cost:
                    best_cost, best_node_pair, split_value = last_cost, last_node_pair, last_value
                break
            if cost < last_cost:
                last_cost, last_node_pair, last_value = cost, node_pair, x[i]

    return best_cost, best_node_pair, split_value


def get_test_data():
    return {"Data": [[2.771244718, 1.784783929],
                     [1.728571309, 1.169761413],
                     [3.678319846, 2.812813570],
                     [3.961043357, 2.619950320],
                     [2.999208922, 2.209014212],
                     [7.497545867, 3.162953546],
                     [9.002203260, 3.339047188],
                     [7.444542326, 0.476683375],
                     [10.12493903, 3.234550982],
                     [6.642287351, 3.319983761]],
            "Target": [0, 0, 0, 0, 0, 1, 1, 1, 1, 1]}


def get_random_data(n):
    return {"Data": [[r] for r in (np.random.random(n) / 2).tolist() + (np.random.random(n) / 2 + 0.5).tolist()],
            "Target": [0] * n + [1] * n}


if __name__ == "__main__":
    # data = get_random_data(4000)
    data = get_test_data()

    # t = np.array(data["Data"])
    # print(t)

    methods = [best_split, best_split_sorted]
    for m in methods:
        start_timer = timeit.default_timer()
        best_cost, node_pair, split_value = m(data)
        stop_timer = timeit.default_timer()
        print("Best split: {}".format(split_value))
        print("node pair: {}".format(node_pair))
        print("Elapsed time: {}\n".format(stop_timer - start_timer))

    # print('Cost {}\npair {}'.format(best_cost, node_pair))
