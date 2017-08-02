import string

import numpy as np
from matplotlib import pyplot as plt
import matplotlib.lines as mlines

from practioner_analysis.medication_rate import MedicationRate

colors = plt.cm.tab10


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


def plot_data(data, **kwargs):
    dc = get_data_container(data, split_date=kwargs.get("split_date"))
    plot(dc, **kwargs)


def get_data_container(data, split_date=None):
    data_container = {}

    for practitioner, mr_dict in data.items():
        practitioner_high = []
        practitioner_high_dates = []
        practitioner_low = []
        practitioner_low_dates = []

        for date, medication_rate in mr_dict.items():
            all_medic, all_total = medication_rate.get_count_threshold(0)
            high_medic, high_total = medication_rate.get_count_threshold(2)
            low_medic, low_total = all_medic - high_medic, all_total - high_total

            if high_total > 0:
                practitioner_high.append(high_medic / high_total)
                practitioner_high_dates.append(date)
            if low_total > 0:
                practitioner_low.append(low_medic / low_total)
                practitioner_low_dates.append(date)

        all_dates = list(set(practitioner_high_dates).union(set(practitioner_low_dates)))

        if len(all_dates) < 12 or \
                        len([d for d in all_dates if d < split_date]) <= 12 or \
                        len([d for d in all_dates if d > split_date]) <= 12:
            continue

        if split_date is not None and not (min(all_dates) < split_date < max(all_dates)):
            continue

        data_container[practitioner] = ((practitioner_high, practitioner_high_dates,
                                         practitioner_low, practitioner_low_dates))

    return data_container


def plot(practitioner_data, split_date, mva, fname, legend=None, title=None):
    fig = plt.figure(figsize=(8, 5))
    ax = fig.add_subplot(111)

    lines_high = []
    lines_low = []

    low_marker = 'x'
    high_marker = '.'
    for i, (high, high_dates, low, low_dates) in enumerate(practitioner_data.values()):
        c = colors(i)

        plt.scatter(low_dates, low, color=c, marker=low_marker)
        plt.scatter(high_dates, high, color=c, marker=high_marker)

        if mva is not None:
            pre = int(mva / 2)
            post = mva - pre
            l1 = plt.plot(high_dates[pre:-(post - 1)], moving_average(high, n=mva), color=c)
            l2 = plt.plot(low_dates[pre:-(post - 1)], moving_average(low, n=mva),
                          "--", color=c, label='_nolegend_')
        else:
            l1 = plt.plot(high_dates, high, color=c)
            l2 = plt.plot(low_dates, low, "--", color=c, label='_nolegend_')

        lines_high.append(l1)
        lines_low.append(l2)

    if split_date is not None:
        ax.axvline(split_date, linestyle=":", color="black", label='_nolegend_')
        ax.text(split_date, 0, " Start CDSS", ha="left", va="bottom")

    low_legend = mlines.Line2D([], [], color=colors(0), marker=low_marker, linestyle="--",
                               markersize=7, label='Score < 2')
    high_legend = mlines.Line2D([], [], color=colors(0), marker=high_marker,
                                markersize=8, label='Score $\geq$ 2')

    style_legend = ax.legend(handles=[low_legend, high_legend], loc=3)

    # For privacy's sake, no use of the practitioner names in the legends
    if legend is None:
        ax.legend(string.ascii_uppercase[:len(practitioner_data.keys())], loc=2)
    else:
        ax.legend(legend, loc=2)

    plt.gca().add_artist(style_legend)

    ax.set_xlabel("Month")
    ax.set_ylabel("Medication Rate")

    ax.yaxis.grid(True)
    ax.set_ylim(0, 1)

    if title is not None:
        plt.title(title)

    plt.savefig("output/practitioner/{}".format(fname))


def plot_difference(grouped_data, split_date, mva, fname, title=None):
    fig = plt.figure(figsize=(8, 5))
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

    low_color, low_marker = colors(3), "x"
    high_color, high_marker = colors(4), "."
    if mva is not None:
        plt.plot(x_low[:-(mva - 1)], moving_average(y_low, n=mva), "--", color=low_color,
                 label="Score < 2")
        plt.plot(x_high[:-(mva - 1)], moving_average(y_high, n=mva), color=high_color,
                 label="Score $\geq$ 2")
    else:
        plt.plot(x_low, y_low, "--", color=low_color, label="Score < 2")
        plt.plot(x_high, y_high, color=high_color, label="Score $\geq$ 2")

    plt.scatter(x_low, y_low, marker=low_marker, color=low_color)
    plt.scatter(x_high, y_high, marker=high_marker, color=high_color)

    if split_date is not None:
        ax.axvline(split_date, linestyle=":", color="black", label='_nolegend_')
        ax.text(split_date, ax.get_ylim()[0], " Start CDSS", ha="left", va="bottom")

    low_legend = mlines.Line2D([], [], color=low_color, marker=low_marker, linestyle="--",
                               markersize=7, label='Score < 2')
    high_legend = mlines.Line2D([], [], color=high_color, marker=high_marker,
                                markersize=8, label='Score $\geq$ 2')

    ax.legend(handles=[low_legend, high_legend])

    ax.set_xlabel("Month")
    ax.set_ylabel("$\Delta$ Medication Rate")

    ax.yaxis.grid(True)
    ax.axhline(0, linewidth=2, color='black', alpha=0.4)

    if title is not None:
        plt.title("Difference of Medication Rate")

    plt.savefig("output/practitioner/{}".format(fname))


def plot_medication_breakdown(data, split_date, mva, fname, legend=None, title=None):
    practitioner_data = get_data_container(data, split_date=split_date)

    fig = plt.figure(figsize=(8, 8))
    ax1 = fig.add_subplot(311)
    ax2 = fig.add_subplot(312, sharex=ax1)
    ax3 = fig.add_subplot(313, sharex=ax1)
    axes = [ax1, ax2, ax3]

    lines_high = []
    lines_low = []

    for i, (high, high_dates, low, low_dates) in enumerate(practitioner_data.values()):
        c = colors(i)

        ax1.scatter(high_dates, high, color=c, marker='.')
        ax1.scatter(low_dates, low, color=c, marker='x')

        if mva is not None:
            pre = int(mva / 2)
            post = mva - pre
            l1 = ax1.plot(high_dates[pre:-(post - 1)], moving_average(high, n=mva), color=c)
            l2 = ax1.plot(low_dates[pre:-(post - 1)], moving_average(low, n=mva),
                          "--", color=c, label='_nolegend_')
        else:
            l1 = ax1.plot(high_dates, high, color=c)
            l2 = ax1.plot(low_dates, low, "--", color=c, label='_nolegend_')

        lines_high.append(l1)
        lines_low.append(l2)

    if split_date is not None:
        for ax in axes:
            ax.axvline(split_date, linestyle=":", color="black", label='_nolegend_')
        ax1.text(split_date, 0, " Start CDSS", ha="left", va="bottom")

    style_legend = ax1.legend([lines_high[0][0], lines_low[0][0]], ["Score $\geq$ 2", "Score < 2"], loc=3)

    # For privacy's sake, no use of the practitioner names in the legends
    if legend is None:
        ax1.legend(string.ascii_uppercase[:len(practitioner_data.keys())], loc=2)
    else:
        ax1.legend(legend, loc=2)

    ax1.add_artist(style_legend)

    if title is not None:
        ax1.set_title(title)
    ax1.set_ylabel("Medication Rate")

    for ax in axes:
        ax.yaxis.grid(True)
        ax.set_axisbelow(True)
        ax.set_ylim(0, 1)

    label_table = np.array([("B01AA", "VKA", colors(0)),
                            ("B01AB", "Heparin", colors(1)),
                            ("B01AC", "Platelet", colors(2)),
                            ("B01AD", "Enzymes", colors(3)),
                            ("B01AE", "DTIs", colors(4)),
                            ("B01AF", "xabans", colors(5)),
                            ("B01AX", "B01AX", colors(6)),
                            ("Other", "Other", colors(7))], dtype=object)

    for (group, mr_dict), ax in zip(data.items(), [ax2, ax3]):
        months = list(mr_dict.keys())
        bars = []
        for month, medication_rate in mr_dict.items():
            med_counter = medication_rate.which_medication
            total = sum(med_counter.values())

            bar = np.zeros(len(label_table))
            for code, count in med_counter.items():
                p = count / total
                index = label_table.T[0].tolist().index(code[:5])
                if index is None:
                    print("Unknown code", code)
                    index = len(label_table) - 1
                bar[index] += p

            bars.append(bar)

        bs = []
        ls = []
        bottom = np.zeros(len(months))
        for i, y in enumerate(np.array(bars).T):
            plot_months = np.array(months)
            plot_bottom = np.array(bottom)
            plot_y = np.array(y)
            for j in np.where(y == 0)[0].tolist()[::-1]:
                plot_y = np.delete(plot_y, j)
                plot_months = np.delete(plot_months, j)
                plot_bottom = np.delete(plot_bottom, j)

            if len(plot_y) == 0:
                continue

            l = label_table.T[1][i]
            c = label_table.T[2][i]
            ls.append(l)

            b = ax.bar(plot_months, plot_y, bottom=plot_bottom, width=25, color=c)
            bs.append(b)

            bottom += y

        ax.set_title(group)
        ax.set_ylabel("Rate Medication Group")
        ax.legend(bs, ls)

    axes[-1].set_xlabel("Month")

    fig.tight_layout()
    plt.savefig("output/practitioner/{}".format(fname))
