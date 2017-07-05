from collections import Counter

import numpy as np


class MedicationRate:
    def __init__(self):
        self.total = Counter()
        self.with_medication = Counter()
        self.which_medication = Counter()

    def __repr__(self):
        return "MedicationRate.({}, {})".format(self.with_medication, self.total)

    def __eq__(self, other):
        return self.total == other.total and self.with_medication == other.with_medication

    def __add__(self, other):
        summed_rate = MedicationRate()
        summed_rate.total = self.total + other.total
        summed_rate.with_medication = self.with_medication + other.with_medication
        summed_rate.which_medication = self.which_medication + other.which_medication
        return summed_rate

    def update(self, score, medication):
        self.total[score] += 1
        if medication:
            self.with_medication[score] += 1
            self.which_medication[medication] += 1

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