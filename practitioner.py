import datetime
from collections import Counter
import numpy as np
from dateutil.relativedelta import relativedelta
from matplotlib import pyplot as plt

from disease import Disease


def get_month_bins(start, end, bin_size):
    date_bins = []
    cur_bin = start
    while cur_bin < end:
        date_bins.append(cur_bin)
        cur_bin += relativedelta(months=bin_size)

    date_bins.append(cur_bin)

    return date_bins


def get_practitioners(patients, spec=None):
    practitioners = set()

    for patient in patients.values():
        for diagnosis in patient.diagnoses.iter_diagnoses():
            if not diagnosis.practitioner:
                continue
            if diagnosis.disease.spec == spec or spec is None:
                practitioners.add(diagnosis.practitioner)

    return practitioners


def get_diagnosis_tuples(patients, disease=None):
    tuples = []
    for patient in patients.values():
        if disease:
            if disease not in patient.diagnoses:
                continue
            for diagnosis in patient.diagnoses[disease]:
                tuples.append((patient, diagnosis))
        else:
            for diagnosis in patient.diagnoses.iter_diagnoses():
                tuples.append((patient, diagnosis))

    return tuples


def moving_average(a, n=3):
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n


def plot_data(data, split_date=None):
    colors = ['C0', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9']
    legend = []

    fig = plt.figure()
    ax = fig.add_subplot(111)

    lines_correct = []
    lines_incorrect = []

    i = 0
    for practitioner, v in data.items():
        practitioner_correct = []
        practitioner_incorrect = []
        practitioner_dates = []

        for date, medication_rate in v.items():
            all_medic, all_total = medication_rate.get_count_threshold(0)
            correct_medic, correct_total = medication_rate.get_count_threshold(3)
            incorrect_medic, incorrect_total = all_medic - correct_medic, all_total - correct_total

            if all_total > 1:
                practitioner_correct.append(correct_medic / correct_total if correct_total > 0 else 0)
                practitioner_incorrect.append(incorrect_medic / incorrect_total if incorrect_total > 0 else 0)
                practitioner_dates.append(date)

        # plt.scatter(practitioner_dates, practitioner_data)
        if len(practitioner_dates) < 12:
            continue

        legend.append(practitioner)

        c = colors[i % len(colors)]
        i += 1

        l1 = plt.plot(practitioner_dates[:-4], moving_average(practitioner_correct, n=5), color=c)
        l2 = plt.plot(practitioner_dates[:-4], moving_average(practitioner_incorrect, n=5),
                      "--", color=c, label='_nolegend_')

        lines_correct.append(l1)
        lines_incorrect.append(l2)

    if split_date is not None:
        plt.plot([split_date, split_date], [0, 1], ":", color="black", label='_nolegend_')

    style_legend = ax.legend([lines_correct[0][0], lines_incorrect[0][0]], ["Correct", "Incorrect"], loc=1)
    ax.legend(legend)
    plt.gca().add_artist(style_legend)

    plt.show()


def analyze_practitioners(patients, start, end, bin_months=1, meds_start_with="B01", spec="CAR", diag="401", plot=True):
    practitioners = get_practitioners(patients, spec=spec)

    if spec is None or diag is None:
        disease = None
    else:
        disease = Disease(spec, diag)

    patient_diagnosis_tuples = get_diagnosis_tuples(patients, disease=disease)
    patient_diagnosis_tuples.sort(key=lambda tup: tup[1])

    date_bins = get_month_bins(start, end, bin_months)
    data = {k: {d: MedicationRate() for d in date_bins} for k in practitioners}
    i = 0
    for patient, diagnosis in patient_diagnosis_tuples:
        if diagnosis.practitioner not in practitioners:
            continue
        if diagnosis.start_date < start:
            continue
        if diagnosis.start_date > end:
            break

        while diagnosis.start_date > date_bins[i + 1]:
            i += 1

        score = patient.calculate_chads_vasc(diagnosis.start_date)
        has_medication = patient.has_medication_group(meds_start_with, diagnosis.start_date) \
                      or patient.has_medication_group(meds_start_with, diagnosis.start_date + relativedelta(days=+1))

        data[diagnosis.practitioner][date_bins[i]].update(score, has_medication)

    if plot:
        plot_data(data, datetime.date(2015, 7, 1))

    return data


class MedicationRate:
    def __init__(self):
        self.total = Counter()
        self.with_medication = Counter()

    def __repr__(self):
        return "MedicationRate.({}, {})".format(self.with_medication, self.total)

    def __eq__(self, other):
        return self.total == other.total and self.with_medication == other.with_medication

    def update(self, score, has_medication):
        self.total[score] += 1
        if has_medication:
            self.with_medication[score] += 1

    def get_rates(self):
        total = np.array([])
        with_medication = np.array([])
        for k in range(10):
            total = np.append(total, [self.total[k]])
            with_medication = np.append(with_medication, [self.with_medication[k]])

        with np.errstate(divide='ignore', invalid='ignore'):
            return np.divide(with_medication, total)

    def get_count_threshold(self, score):
        total = 0
        with_medication = 0
        for s in self.total:
            if s < score:
                continue
            total += self.total[s]
            with_medication += self.with_medication[s]

        return with_medication, total

    def get_rate_threshold(self, score):
        with_medication, total = self.get_count_threshold(score)

        with np.errstate(divide='ignore', invalid='ignore'):
            div = np.divide(with_medication, total)

        return 0 if np.isnan(div) else div
