from dateutil.relativedelta import relativedelta

from disease_groups import *


class Patient:
    def __init__(self, number, sex, birth_date, death_date=None):
        self.number = number
        self.sex = sex
        self.birth_date = birth_date
        self.death_date = death_date

        self.diagnoses = {}
        self.chads_vasc_changes = []
        self.strokes = []

    def __repr__(self):
        return "({}, {}, {}, {}\nDiseases: {})".format(self.number, self.sex, self.birth_date, self.death_date,
                                                       self.diagnoses)

    def add_diagnosis(self, diagnosis):
        if diagnosis.disease not in self.diagnoses:
            self.diagnoses[diagnosis.disease] = []

        self.diagnoses[diagnosis.disease].append(diagnosis)

    def get_current_diseases(self, timestamp):
        current_diseases = []
        for disease, diagnose in self.diagnoses.items():
            if diagnose.start_date <= timestamp <= diagnose.end_date:
                current_diseases.append(diagnose)

        return current_diseases

    def has_disease(self, disease, timestamp, chronic=False):
        if disease not in self.diagnoses:
            return False

        for d in self.diagnoses[disease]:
            if (chronic and d.start_date <= timestamp) or d.start_date <= timestamp <= d.end_date:
                return True
        return False

    def days_since_disease(self, disease, timestamp):
        if disease not in self.diagnoses:
            return 0

        days = [(timestamp - d.start_date).days for d in self.diagnoses[disease]
                if (timestamp - d.start_date).days >= 0]

        if not days:
            return 0

        return min(days)

    def calculate_age(self, timestamp):
        age = timestamp.year - self.birth_date.year

        if timestamp.month < self.birth_date.month:
            age -= 1
        elif timestamp.month == self.birth_date.month and self.birth_date.day > timestamp.day:
            age -= 1

        return age

    def is_female(self):
        return self.sex.lower() == "v" or self.sex.lower() == "f"

    def calculate_chads_vasc(self, timestamp):
        score = sum([
            1 if any(map(lambda d: self.has_disease(d, timestamp, chronic=True), chads_vasc_c)) else 0,
            1 if any(map(lambda d: self.has_disease(d, timestamp, chronic=True), chads_vasc_h)) else 0,
            1 if any(map(lambda d: self.has_disease(d, timestamp, chronic=True), chads_vasc_d)) else 0,
            2 if any(map(lambda d: self.has_disease(d, timestamp, chronic=True), chads_vasc_s)) else 0,
            1 if any(map(lambda d: self.has_disease(d, timestamp, chronic=True), chads_vasc_v)) else 0,
        ])

        age = self.calculate_age(timestamp)

        if age >= 75:
            score += 2
        elif age >= 65:
            score += 1

        if self.is_female():
            score += 1

        return score

    def should_have_AC(self, timestamp, method, kwargs):
        return method(self, timestamp, **kwargs)

    def is_dead(self, timestamp):
        if self.death_date <= timestamp:
            return True
        return False

    def find_chads_vasc_changes(self):
        """"
        It's more efficient to pre-calculate the CHADS-VASc score based on all data,
        than to calculate it while simulating. This method does assume that all diagnoses
        are in effect indefinitely (chronic).
        """

        changes = [ChadsVascChangeEvent(self.birth_date, 0)]
        for _, ds in self.diagnoses.items():
            for diagnosis in ds:
                date = diagnosis.start_date
                changes.append(ChadsVascChangeEvent(date, self.calculate_chads_vasc(date)))

        date = self.birth_date + relativedelta(years=65)
        changes.append(ChadsVascChangeEvent(date, self.calculate_chads_vasc(date)))

        date = self.birth_date + relativedelta(years=75)
        changes.append(ChadsVascChangeEvent(date, self.calculate_chads_vasc(date)))

        self.chads_vasc_changes = sorted(changes)

    def find_strokes(self):

        timestamps = []
        for s in stroke_diseases:
            if s not in self.diagnoses:
                continue

            for d in self.diagnoses[s]:
                timestamps.append(d.start_date)

        self.strokes = timestamps


class ChadsVascChangeEvent:
    def __init__(self, date, score):
        self.date = date
        self.score = score

    def __lt__(self, other):
        return self.date < other.date

    def __repr__(self):
        return "{} {}".format(self.date, self.score)
