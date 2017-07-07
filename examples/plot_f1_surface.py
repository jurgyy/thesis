import numpy as np
from matplotlib import pyplot as plt


def f1(precision, recall):
    if precision == 0 or recall == 0:
        return 0
    return 2 * (precision * recall) / (precision + recall)


def main():
    fig = plt.figure(figsize=(2.8, 2))
    ax = fig.add_subplot(111)

    step = 0.005
    x_min, x_max = 0, 1 + step
    y_min, y_max = 0, 1 + step

    xx, yy = np.meshgrid(np.arange(x_min, x_max, step), np.arange(y_min, y_max, step))
    Z = np.array([f1(x, y) for x, y in np.c_[xx.ravel(), yy.ravel()]]).reshape(xx.shape)

    cs = ax.contourf(xx, yy, Z, np.arange(0, 1 + step, step), vmin=0, vmax=1, cmap=plt.cm.coolwarm)
    ax.set_xticks(np.arange(0, 1 + 0.2, 0.2))
    ax.set_yticks(np.arange(0, 1 + 0.2, 0.2))

    cbar = plt.colorbar(cs)
    cbar.ax.set_ylim(0, 1)
    cbar.set_ticks(np.arange(0, 1 + 0.1, 0.2))
    cbar.ax.set_ylabel("$F_1$ Score")

    ax.set_xlabel("Precision")
    ax.set_ylabel("Recall")
    plt.title(
        r'$2 \cdot \frac{\mathrm{Precision} \cdot \mathrm{Sensitivity}}{\mathrm{Precision} + \mathrm{Sensitivity}}$'
    )
    plt.savefig("../output/examples/f1_score.png", bbox_inches='tight')

if __name__ == "__main__":
    main()