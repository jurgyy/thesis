import numpy as np
from matplotlib import pyplot as plt


def moving_average(a, n=3):
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n


def plot_data(data, split_date=None, mva=None):
    colors = ['C0', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9']
    legend = []

    fig = plt.figure()
    ax = fig.add_subplot(111)

    lines_correct = []
    lines_incorrect = []

    i = 0
    for practitioner, v in data.items():
        practitioner_correct = []
        practitioner_correct_dates = []
        practitioner_incorrect = []
        practitioner_incorrect_dates = []

        for date, medication_rate in v.items():
            all_medic, all_total = medication_rate.get_count_threshold(0)
            correct_medic, correct_total = medication_rate.get_count_threshold(3)
            incorrect_medic, incorrect_total = all_medic - correct_medic, all_total - correct_total

            if correct_total > 0:
                practitioner_correct.append(correct_medic / correct_total)
                practitioner_correct_dates.append(date)
            if incorrect_total > 0:
                practitioner_incorrect.append(1 - (incorrect_medic / incorrect_total))
                practitioner_incorrect_dates.append(date)

        all_dates = list(set(practitioner_correct_dates).union(set(practitioner_incorrect_dates)))

        if len(all_dates) < 12 or \
                len([d for d in all_dates if d < split_date]) <= 6 or \
                len([d for d in all_dates if d > split_date]) <= 6:
            continue

        if split_date is not None and not (min(all_dates) < split_date < max(all_dates)):
            continue

        legend.append(practitioner)

        c = colors[i % len(colors)]
        i += 1

        plt.scatter(practitioner_correct_dates, practitioner_correct, color=c, marker='.')
        plt.scatter(practitioner_incorrect_dates, practitioner_incorrect, color=c, marker='x')
        if mva is not None:
            l1 = plt.plot(practitioner_correct_dates[:-(mva - 1)], moving_average(practitioner_correct, n=mva), color=c)
            l2 = plt.plot(practitioner_incorrect_dates[:-(mva - 1)], moving_average(practitioner_incorrect, n=mva),
                          "--", color=c, label='_nolegend_')
        else:
            l1 = plt.plot(practitioner_correct_dates, practitioner_correct, color=c)
            l2 = plt.plot(practitioner_incorrect_dates, practitioner_incorrect, "--", color=c, label='_nolegend_')

        lines_correct.append(l1)
        lines_incorrect.append(l2)

    if split_date is not None:
        plt.plot([split_date, split_date], [0, 1], ":", color="black", label='_nolegend_')

    style_legend = ax.legend([lines_correct[0][0], lines_incorrect[0][0]], ["Score $\geq$ 3", "Score < 3"], loc=1)
    ax.legend(legend)
    plt.gca().add_artist(style_legend)

    plt.show()