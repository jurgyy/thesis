import numpy as np
import pandas as pd

from matplotlib import pyplot as plt
from collections import Counter
from dateutil.relativedelta import relativedelta


def breakdown(patients, timestamp):
    print("Score breakdown:")
    data = {i: BreakdownRow() for i in range(10)}
    for patient in patients.values():
        if not patient.is_alive(timestamp):
            continue
        score = patient.calculate_chads_vasc(timestamp)
        data[score].update(patient.calculate_age(timestamp), patient.is_female())

    d = dict()
    d['# Patients'] = pd.Series([len(r.ages) for r in data.values()])
    d['Mean Age'] = pd.Series([r.mean_std_age()[0] for r in data.values()])
    d['Std Age'] = pd.Series([r.mean_std_age()[1] for r in data.values()])
    d['% Female'] = pd.Series([r.percentage_female() for r in data.values()])

    df = pd.DataFrame(d, index=range(10))

    print(df)

    stroke_analysis(patients)


def plot_stroke_counter(counter):
    fig = plt.figure(figsize=(10, 5))
    ax = fig.add_subplot(111)

    labels, values = zip(*sorted(counter.items()))
    indexes = np.arange(len(labels))
    width = 0.9

    ax.bar(indexes, values, width)
    ax.set_xticks(indexes)
    ax.set_xticklabels(labels)

    plt.title("Occurrences of multiple strokes")
    plt.xlabel("Number of strokes occurred")
    plt.ylabel("Number of patients")

    # plt.show()
    plt.savefig("output/stroke_occurrence", bbox_inches='tight')


def stroke_analysis(patients):
    stroke_patients = 0
    death_after_stroke = 0
    stroke_counts = Counter()
    for patient in patients.values():
        if not patient.strokes:
            continue

        stroke_patients += 1
        stroke_counts[len(set(patient.strokes))] += 1

        for s in patient.strokes:
            if not patient.is_alive(s + relativedelta(months=+1)):
                death_after_stroke += 1
                continue

    print("Number of patients with at least 1 stroke: {}".format(stroke_patients))
    print("{} of which died within a month after diagnosis".format(death_after_stroke))
    print("Multiple stroke count: {}".format(stroke_counts))
    print("Plotting stroke count...")
    plot_stroke_counter(stroke_counts)


class BreakdownRow:
    def __init__(self):
        self.ages = []
        self.female_count = 0

    def update(self, age, is_female):
        self.ages.append(age)
        if is_female:
            self.female_count += 1

    def mean_std_age(self):
        arr = np.array(self.ages)
        return arr.mean(), arr.std()

    def percentage_female(self):
        return 100 * self.female_count / len(self.ages)
