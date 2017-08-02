import datetime

import numpy as np
import pandas as pd

from matplotlib import pyplot as plt
from collections import Counter
from dateutil.relativedelta import relativedelta

from disease_groups import atrial_fib
from simulations.simulations import patient_month_generator


def breakdown(patients, timestamp):
    print("Score breakdown:")

    patient_count = 0
    female_count = 0
    data = {i: BreakdownRow() for i in range(10)}
    for patient in patients.values():
        patient_count += 1
        if patient.is_female():
            female_count += 1

        if not patient.is_alive(timestamp):
            continue

        score = patient.calculate_chads_vasc(timestamp)
        data[score].update(patient.calculate_age(timestamp), patient.is_female())

    d = dict()
    d['# Patients'] = pd.Series([len(r.ages) for r in data.values()])
    d['Mean Age'] = pd.Series([r.mean_std_age()[0] for r in data.values()])
    d['Std Age'] = pd.Series([r.mean_std_age()[1] for r in data.values()])
    d['% Female'] = pd.Series([r.percentage_female() for r in data.values()])

    print("Total number of patients: {}".format(patient_count))
    print("Number of female patients: {} ({}%)".format(female_count, female_count / patient_count * 100))

    df = pd.DataFrame(d, index=range(10))

    print(df)


def plot_AF_count(datasets, start, end, legend_labels=None):
    fig = plt.figure()
    ax = fig.add_subplot(111)

    n = len(datasets)
    w = 320
    offsets = np.arange(0, w, w/n) - 0.5 * (n - 1) * w/n

    rects = []
    for i, patients in enumerate(datasets):
        patient_counter = Counter()
        for patient, date, _ in patient_month_generator(patients, start, end, step=12, include_meds=True):
            if patient.has_disease_group(atrial_fib, date, chronic=True):
                patient_counter[date] += 1

        x = list(patient_counter.keys())
        x = [v + datetime.timedelta(days=offsets[i]) for v in x]
        y = list(patient_counter.values())

        label = legend_labels[i] if legend_labels else None
        rects.append(ax.bar(x, y, width=w/n, label=label))

    plt.legend()
    ax.set_xlabel("Year")
    ax.set_ylabel("Number of patients")
    plt.title("Living AF patients over time")
    # plt.show()
    plt.savefig("output/breakdown/AF_patients", bbox_inches='tight')


def plot_stroke_counter(counter):
    fig = plt.figure(figsize=(8, 4))
    ax = fig.add_subplot(111)

    labels, values = zip(*sorted(counter.items()))
    indexes = np.arange(len(labels))
    width = 0.9

    ax.bar(indexes, values, width)
    ax.set_xticks(indexes)
    ax.set_xticklabels(labels)
    ax.set_axisbelow(True)
    ax.yaxis.grid(which='both')

    plt.title("Occurrences of multiple strokes")
    plt.xlabel("Number of strokes occurred")
    plt.ylabel("Number of patients")

    # plt.show()
    plt.savefig("output/breakdown/stroke_occurrence", bbox_inches='tight')


def plot_stroke_count_score(count):
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111)

    x = list(range(10))
    y = [count[v] for v in x]

    ax.bar(x, y)
    ax.set_xticks(x)
    ax.set_axisbelow(True)
    ax.yaxis.grid(which='both')

    plt.title(r"Occurrence of stroke per CHA$_2$DS$_2$-VASc score")
    plt.xlabel("Score")
    plt.ylabel("Number of patients")

    plt.savefig("output/breakdown/stroke_score", bbox_inches='tight')


def stroke_analysis(patients):
    stroke_patients = 0
    death_after_stroke = 0
    mult_stroke_counts = Counter()
    stroke_count_score = Counter()
    for patient in patients.values():
        if not patient.strokes:
            continue

        stroke_patients += 1
        mult_stroke_counts[len(set(patient.strokes))] += 1

        for s in patient.strokes:
            stroke_count_score[patient.calculate_chads_vasc(s - relativedelta(days=+1))] += 1
            if not patient.is_alive(s + relativedelta(months=+12)):
                death_after_stroke += 1
                continue

    print("Number of patients with at least 1 stroke: {}".format(stroke_patients))
    print("{} of which died within a year after diagnosis".format(death_after_stroke))
    print("Multiple stroke count: {}".format(mult_stroke_counts))
    print("Plotting stroke count...")
    plot_stroke_counter(mult_stroke_counts)
    plot_stroke_count_score(stroke_count_score)


def get_disease_frequency(diseases, diagnoses):
    frequency = {d: 0 for d in diseases}

    for patient_diagnoses in diagnoses.values():
        for diagnosis in patient_diagnoses:
            if diagnosis.disease not in frequency:
                continue
            frequency[diagnosis.disease] += 1

    return frequency


def plot_disease_frequency(diseases, diagnoses):
    print("Plotting Disease Frequency...")
    fig = plt.figure()
    ax = fig.add_subplot(111)

    frequency = get_disease_frequency(diseases, diagnoses)

    labels, y = map(list, zip(*frequency.items()))
    labels = map(str, labels)

    y, labels = zip(*sorted(zip(y, labels)))
    print("Total number of diagnoses: {}".format(sum(y)))
    print("Number of different diagnoses: {}".format(len(y)))
    print("Most frequent three are: {} ({}), {} ({}) and {} ({})".format(
        labels[-1], y[-1], labels[-2], y[-2], labels[-3], y[-3]))

    x = range(len(labels))
    ax.bar(x, y, log=True, width=4)
    ax.set_xlim(-50, max(x) + 100)
    ax.set_xlabel("Diagnosis")
    ax.set_ylabel("Frequency (log scale)")

    ax.set_axisbelow(True)
    ax.yaxis.grid(which='both')
    ax.yaxis.grid(which='minor', alpha=0.2)
    ax.yaxis.grid(which='major', alpha=0.5)

    plt.title("Diagnosis frequency of all patients")
    # plt.yticks(x, labels)
    # plt.show()
    plt.savefig("output/breakdown/diagnosis_frequency", bbox_inches='tight')


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