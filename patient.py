from dateutil.relativedelta import relativedelta

from chads_vasc_diseases import *


class Patient:
    def __init__(self, number, sex, birth_date, death_date=None):
        self.number = number
        self.sex = sex
        self.birth_date = birth_date
        self.death_date = death_date

        self.diagnoses = {}
        self.chadsvasc_changes = []

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

    def has_disease(self, disease, timestamp, chronic=True):
        if disease not in self.diagnoses:
            return False

        for d in self.diagnoses[disease]:
            if(d.start_date <= timestamp and chronic) or d.start_date <= timestamp <= d.end_date:
                return True
        return False

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
            1 if any(map(lambda d: self.has_disease(d, timestamp, chronic=True), heart_failure)) else 0,
            1 if any(map(lambda d: self.has_disease(d, timestamp, chronic=True), hypertension)) else 0,
            1 if any(map(lambda d: self.has_disease(d, timestamp, chronic=True), diabetes)) else 0,
            2 if any(map(lambda d: self.has_disease(d, timestamp, chronic=True), stroke)) else 0,
            1 if any(map(lambda d: self.has_disease(d, timestamp, chronic=True), vascular)) else 0,
        ])

        age = self.calculate_age(timestamp)

        if age >= 75:
            score += 2
        elif age >= 65:
            score += 1

        if self.is_female():
            score += 1

        return score

    def should_have_AC(self, timestamp, method="event"):
        if method == "event":
            if len(self.chadsvasc_changes) == 0:
                return False

            tmp = self.chadsvasc_changes[0]
            for e in self.chadsvasc_changes:
                if e.date > timestamp:
                    break

                tmp = e

            return tmp.score >= 3
        else:
            if self.calculate_chads_vasc(timestamp) >= 3:
                return True
            return False

    def is_dead(self, timestamp):
        if self.death_date <= timestamp:
            return True
        return False

    def find_chadsvasc_changes(self):
        """"
        It's more efficient to pre-calculate the CHADS-VASc score based on all data,
        than to calculate it while simulating. This method does assume that all diagnoses
        are in effect indefinitely (chronic).
        """

        changes = [ChadsvascChangeEvent(self.birth_date, 0)]
        for _, ds in self.diagnoses.items():
            for diagnosis in ds:
                date = diagnosis.start_date
                changes.append(ChadsvascChangeEvent(date, self.calculate_chads_vasc(date)))

        date = self.birth_date + relativedelta(years=65)
        changes.append(ChadsvascChangeEvent(date, self.calculate_chads_vasc(date)))

        date = self.birth_date + relativedelta(years=75)
        changes.append(ChadsvascChangeEvent(date, self.calculate_chads_vasc(date)))

        self.chadsvasc_changes = sorted(changes)


class ChadsvascChangeEvent:
    def __init__(self, date, score):
        self.date = date
        self.score = score

    def __lt__(self, other):
        return self.date < other.date

    def __repr__(self):
        return "{} {}".format(self.date, self.score)
