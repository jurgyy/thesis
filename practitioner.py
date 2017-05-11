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
        for diagnoses in patient.diagnoses.values():
            for diagnosis in diagnoses:
                if not diagnosis.practitioner:
                    continue
                if spec is None:
                    practitioners.add(diagnosis.practitioner)
                    continue
                if spec == diagnosis.disease.spec:
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
            for diagnoses in patient.diagnoses.values():
                for diagnosis in diagnoses:
                    tuples.append((patient, diagnosis))

    return tuples


def plot_data(data, bins):
    hist_data = []
    annotations = []
    legend = []
    for practitioner, v in data.items():
        hist = []
        anos = []
        legend.append(practitioner)

        for date, medication_rate in v.items():
            hist.append(medication_rate.get_rate_threshold(3))
            a, b = medication_rate.get_count_threshold(3)
            anos.append("{}/{}".format(a, b))

        hist_data.append(hist)
        annotations.append(anos)

    fig = plt.figure()
    ax = fig.add_subplot(111)

    # Leave space equal to the width of an extra bar between different periods
    width = 1 / (len(data) + 1)
    for i, d in enumerate(hist_data):
        positions = np.array(range(len(bins))) + i * width + 0.5 * width
        ax.bar(positions, d, width)
        for j in range(len(d)):
            ax.text(positions[j], d[j], annotations[i][j], horizontalalignment='center')

    # TODO: fix bug; labels starting with the second element
    ax.set_xticklabels([""] + [d.strftime("%B %Y") for d in bins])
    ax.legend(legend)
    plt.show()


def analyze_practitioners(patients, start, end, bin_months=3, meds_start_with="B", spec="CAR", diag="401", plot=True):
    date_bins = get_month_bins(start, end, bin_months)

    practitioners = get_practitioners(patients, spec=spec)
    data = {k: {d: MedicationRate() for d in date_bins} for k in practitioners}

    if spec is None or diag is None:
        disease = None
    else:
        disease = Disease(spec, diag)

    patient_diagnosis_tuples = get_diagnosis_tuples(patients, disease=disease)
    patient_diagnosis_tuples.sort(key=lambda tup: tup[1])

    i = 0
    for p, d in patient_diagnosis_tuples:
        if d.practitioner not in practitioners:
            continue
        if d.start_date < start:
            continue
        if d.start_date > end:
            break

        while d.start_date > date_bins[i + 1]:
            i += 1

        score = p.calculate_chads_vasc(d.start_date)
        data[d.practitioner][date_bins[i]].update(score,
                                                  p.has_medication_group(meds_start_with, d.start_date) or
                                                  p.has_medication_group(meds_start_with, d.start_date + relativedelta(days=+1)))

    if plot:
        plot_data(data, date_bins)

    return data


class MedicationRate:
    def __init__(self):
        self.total = Counter()
        self.required = Counter()

    def __repr__(self):
        return "MedicationRate.({}, {})".format(self.required, self.total)

    def __eq__(self, other):
        return self.total == other.total and self.required == other.required

    def update(self, score, required):
        self.total[score] += 1
        if required:
            self.required[score] += 1

    def get_rates(self):
        total = np.array([])
        required = np.array([])
        for k in range(10):
            np.append(required, [self.required[k]])
            np.append(total, [self.total[k]])

        with np.errstate(divide='ignore', invalid='ignore'):
            return np.divide(required, total)

    def get_count_threshold(self, score):
        total = 0
        required = 0
        for s in self.total:
            if s < score:
                continue
            total += self.total[s]
            required += self.required[s]

        return required, total

    def get_rate_threshold(self, score):
        required, total = self.get_count_threshold(score)

        with np.errstate(divide='ignore', invalid='ignore'):
            div = np.divide(required, total)

        return 0 if np.isnan(div) else div
