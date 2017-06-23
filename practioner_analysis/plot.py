import datetime

import numpy as np
from matplotlib import pyplot as plt

from practioner_analysis.medication_rate import MedicationRate

colors = ['C0', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9']


def moving_average(a, n=3):
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n


def group_data(data, inclusive_group, inclusive_name, exclusive_name):
    group_keys = [inclusive_name, exclusive_name]

    date_bins = sorted({date for date in list(data.values())[0]})
    grouped_data = {k: {d: MedicationRate() for d in date_bins} for k in group_keys}

    for practitioner, v in data.items():
        for date, medication_rate in v.items():
            if practitioner in inclusive_group:
                key = group_keys[0]
            else:
                key = group_keys[1]

            grouped_data[key][date] += medication_rate

    return grouped_data


def plot_data(data, split_date=None, mva=None, fname=None):
    dc = get_data_container(data, split_date=split_date)
    plot(dc, split_date, mva, fname)


def get_data_container(data, split_date=None):
    data_container = {}

    for practitioner, v in data.items():
        practitioner_high = []
        practitioner_high_dates = []
        practitioner_low = []
        practitioner_low_dates = []

        for date, medication_rate in v.items():
            all_medic, all_total = medication_rate.get_count_threshold(0)
            high_medic, high_total = medication_rate.get_count_threshold(3)
            low_medic, low_total = all_medic - high_medic, all_total - high_total

            if high_total > 0:
                practitioner_high.append(high_medic / high_total)
                practitioner_high_dates.append(date)
            if low_total > 0:
                practitioner_low.append(low_medic / low_total)
                practitioner_low_dates.append(date)

        all_dates = list(set(practitioner_high_dates).union(set(practitioner_low_dates)))

        if len(all_dates) < 12 or \
                len([d for d in all_dates if d < split_date]) <= 6 or \
                len([d for d in all_dates if d > split_date]) <= 6:
            continue

        if split_date is not None and not (min(all_dates) < split_date < max(all_dates)):
            continue

        data_container[practitioner] = ((practitioner_high, practitioner_high_dates,
                                         practitioner_low, practitioner_low_dates))

    return data_container


def plot(practitioner_data, split_date, mva, fname):
    fig = plt.figure(figsize=(14, 8))
    ax = fig.add_subplot(111)

    lines_high = []
    lines_low = []

    i = 0
    for high, high_dates, low, low_dates in practitioner_data.values():
        c = colors[i % len(colors)]
        i += 1

        plt.scatter(high_dates, high, color=c, marker='.')
        plt.scatter(low_dates, low, color=c, marker='x')

        if mva is not None:
            l1 = plt.plot(high_dates[:-(mva - 1)], moving_average(high, n=mva), color=c)
            l2 = plt.plot(low_dates[:-(mva - 1)], moving_average(low, n=mva),
                          "--", color=c, label='_nolegend_')
        else:
            l1 = plt.plot(high_dates, high, color=c)
            l2 = plt.plot(low_dates, low, "--", color=c, label='_nolegend_')

        lines_high.append(l1)
        lines_low.append(l2)

    if split_date is not None:
        ax.axvline(split_date, linestyle=":", color="black", label='_nolegend_')

    style_legend = ax.legend([lines_high[0][0], lines_low[0][0]], ["Score $\geq$ 3", "Score < 3"], loc=6)
    ax.legend(list(practitioner_data.keys()), loc=7)
    plt.gca().add_artist(style_legend)

    ax.set_xlabel("Month")
    ax.set_ylabel("Medication Rate")

    ax.yaxis.grid(True)
    ax.set_ylim(0, 1)

    plt.title("Medication Rate per Practitioner over time")
    plt.savefig("output/{}".format(fname))


def plot_difference(grouped_data, split_date, mva, fname):
    fig = plt.figure(figsize=(14, 8))
    ax = fig.add_subplot(111)

    dc = get_data_container(grouped_data, split_date=split_date)
    no_high, no_high_dates, no_low, no_low_dates = dc["No CDSS"]
    cdss_high, cdss_high_dates, cdss_low, cdss_low_dates = dc["CDSS"]

    x_high = []
    y_high = []
    for i, date in enumerate(cdss_high_dates):
        try:
            index = no_high_dates.index(date)
        except ValueError:
            continue

        x_high.append(date)
        y_high.append(cdss_high[i] - no_high[index])

    x_low = []
    y_low = []
    for i, date in enumerate(cdss_low_dates):
        try:
            index = no_low_dates.index(date)
        except ValueError:
            continue

        x_low.append(date)
        y_low.append(cdss_low[i] - no_low[index])

    low_color = colors[0]
    high_color = colors[1]
    if mva is not None:
        plt.plot(x_low[:-(mva - 1)], moving_average(y_low, n=mva), color=low_color, label="Score < 3")
        plt.plot(x_high[:-(mva - 1)], moving_average(y_high, n=mva), color=high_color, label="Score $\geq$ 3")
    else:
        plt.plot(x_low, y_low, color=low_color, label="Score < 3")
        plt.plot(x_high, y_high, color=high_color, label="Score $\geq$ 3")

    plt.scatter(x_low, y_low, marker='.')
    plt.scatter(x_high, y_high, marker='.')

    if split_date is not None:
        ax.axvline(split_date, linestyle=":", color="black", label='_nolegend_')

    ax.legend()

    ax.set_xlabel("Month")
    ax.set_ylabel("$\Delta$ Medication Rate")

    ax.yaxis.grid(True)
    ax.axhline(0, linewidth=2, color='black', alpha=0.4)
    plt.title("Difference of Medication Rate")
    # plt.show()
    plt.savefig("output/{}".format(fname))
