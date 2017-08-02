import numpy as np
from matplotlib import pyplot as plt


def fbeta(beta):
    def f(precision, recall):
        if precision == 0 or recall == 0:
            return 0
        return (beta**2 + 1) * (precision * recall) / (beta**2 * precision + recall)
    return f


def recall(tp, fn):
    if tp + fn == 0:
        return 0
    return tp / (tp + fn)


def surface_plot(top, score_function, fname, **kwargs):
    fig = plt.figure(figsize=(2.8, 2))
    ax = fig.add_subplot(111)

    step = top / 400
    x_min, x_max = 0, top + step
    y_min, y_max = 0, top + step

    xx, yy = np.meshgrid(np.arange(x_min, x_max, step), np.arange(y_min, y_max, step))
    Z = np.array([score_function(x, y) for x, y in np.c_[xx.ravel(), yy.ravel()]]).reshape(xx.shape)

    cstep = 1 / 400
    cs = ax.contourf(xx, yy, Z, np.arange(0, 1 + cstep, cstep), vmin=0, vmax=1, cmap=plt.cm.coolwarm)
    ax.set_xticks(np.arange(0, top + 0.2, top / 5))
    ax.set_yticks(np.arange(0, top + 0.2, top / 5))

    cbar = plt.colorbar(cs)
    cbar.ax.set_ylim(0, 1)
    cbar.set_ticks(np.arange(0, 1 + 0.1, 0.2))
    cbar.ax.set_ylabel(kwargs.get("legendlabel"))

    ax.set_xlabel(kwargs.get("xlabel"))
    ax.set_ylabel(kwargs.get("ylabel"))
    plt.title(
        kwargs.get("title")
    )
    plt.savefig("../output/examples/{}".format(fname), bbox_inches='tight')


def main():
    surface_plot(10, recall, "recall_score", xlabel="TP", ylabel="FN", title="Recall Score",
                 legendlabel=r'$\frac{\mathrm{TP}}{\mathrm{TP} + \mathrm{FN}}$')
    surface_plot(1, fbeta(0.5), "f05_score", xlabel="Precision", ylabel="Recall", title="$F_{0.5}$ Score",
                 legendlabel=r'$1.25 \cdot \frac{\mathrm{Precision} \cdot \mathrm{Sensitivity}}{0.25 \cdot \mathrm{Precision} + \mathrm{Sensitivity}}$')
    surface_plot(1, fbeta(1), "f1_score", xlabel="Precision", ylabel="Recall", title="$F_1$ Score",
                 legendlabel=r'$2 \cdot \frac{\mathrm{Precision} \cdot \mathrm{Sensitivity}}{\mathrm{Precision} + \mathrm{Sensitivity}}$')
    surface_plot(1, fbeta(2), "f2_score", xlabel="Precision", ylabel="Recall", title="$F_2$ Score",
                 legendlabel=r'$5 \cdot \frac{\mathrm{Precision} \cdot \mathrm{Sensitivity}}{4 \cdot \mathrm{Precision} + \mathrm{Sensitivity}}$')
    surface_plot(1, fbeta(5), "f5_score", xlabel="Precision", ylabel="Recall", title="$F_5$ Score",
                 legendlabel=r'$26 \cdot \frac{\mathrm{Precision} \cdot \mathrm{Sensitivity}}{25 \cdot \mathrm{Precision} + \mathrm{Sensitivity}}$')
    surface_plot(1, fbeta(10), "f10_score", xlabel="Precision", ylabel="Recall", title="$F_{10}$ Score",
                     legendlabel=r'$101 \cdot \frac{\mathrm{Precision} \cdot \mathrm{Sensitivity}}{100 \cdot \mathrm{Precision} + \mathrm{Sensitivity}}$')

if __name__ == "__main__":
    main()
