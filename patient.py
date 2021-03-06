import datetime

from dateutil.relativedelta import relativedelta

from diagnosis import Diagnosis
from disease_groups import *


class Patient:
    def __init__(self, number, sex, birth_date, death_date=None):
        self.number = number
        self.sex = sex
        self.birth_date = birth_date
        self.death_date = death_date

        self.diagnoses = DiagnosesDict({})
        self.strokes = []
        self.care_range = (datetime.date(datetime.MAXYEAR, 12, 31), datetime.date(datetime.MINYEAR, 1, 1))  # TODO Unused

        self.medications = {}

    def __repr__(self):
        return "({}, {}, {}, {}\nDiseases: {})".format(self.number, self.sex, self.birth_date, self.death_date,
                                                       len(self.diagnoses.keys()))

    def __eq__(self, other):
        return (self.number == other.number and self.sex == other.sex and
                self.birth_date == other.birth_date and self.death_date == other.death_date)

    def add_diagnosis(self, diagnosis):
        self.diagnoses.add(diagnosis)

        if self.death_date is not None and self.death_date is not datetime.date(datetime.MAXYEAR, 12, 31):
            if diagnosis.start_date > self.death_date:
                self.death_date = diagnosis.start_date

    def get_current_diseases(self, timestamp):  # Unused
        current_diseases = set()
        for diagnosis in self.diagnoses.iter_diagnoses():
            if diagnosis.start_date <= timestamp <= diagnosis.end_date:
                current_diseases.add(diagnosis.disease)

        return current_diseases

    def has_disease(self, disease, timestamp, chronic=False):
        if disease not in self.diagnoses:
            return False

        for d in self.diagnoses[disease]:
            if (chronic and d.start_date <= timestamp) or d.start_date <= timestamp <= d.end_date:
                return True
        return False

    def has_disease_group(self, group, timestamp, chronic=False):
        return any(map(lambda d: self.has_disease(d, timestamp, chronic=chronic), group))

    def days_since_diagnosis(self, disease, timestamp):
        if disease not in self.diagnoses:
            return 0

        days = [(timestamp - d.start_date).days for d in self.diagnoses[disease]
                if (timestamp - d.start_date).days >= 0]

        if not days:
            return 0

        return min(days)

    def days_since_last_diagnosis(self, timestamp):
        last_diagnosis = self.diagnoses.last_diagnosis
        if last_diagnosis is None:
            raise Exception("No Diagnoses")
        return (timestamp - last_diagnosis.start_date).days

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
            1 if self.has_disease_group(chads_vasc_c, timestamp, chronic=True) else 0,
            1 if self.has_disease_group(chads_vasc_h, timestamp, chronic=True) else 0,
            1 if self.has_disease_group(chads_vasc_d, timestamp, chronic=True) else 0,
            2 if self.has_disease_group(chads_vasc_s, timestamp, chronic=True) else 0,
            1 if self.has_disease_group(chads_vasc_v, timestamp, chronic=True) else 0
        ])

        age = self.calculate_age(timestamp)

        if age >= 75:
            score += 2
        elif age >= 65:
            score += 1

        if self.is_female():
            score += 1

        return score

    def should_have_AC(self, timestamp, method, **kwargs):
        return method(self, timestamp, **kwargs)

    def is_alive(self, timestamp):
        if self.birth_date <= timestamp < self.death_date:
            return True
        return False

    def find_strokes(self):

        timestamps = []
        for s in stroke_diseases:
            if s not in self.diagnoses:
                continue

            for d in self.diagnoses[s]:
                timestamps.append(d.start_date)

        self.strokes = timestamps

    def add_medication(self, medication):
        if medication.code not in self.medications:
            self.medications[medication.code] = []
        self.medications[medication.code].append(medication)

    def has_medication(self, medication_code, sim_date):
        for m in self.medications[medication_code]:
            if m.start_date <= sim_date <= m.end_date:
                return True
        return False

    def has_medication_group(self, starts_with, sim_date, which=False):
        last = None
        last_date = datetime.date(datetime.MINYEAR, 1, 1)
        for code, medications in self.medications.items():
            if not code.startswith(starts_with):
                continue

            for m in medications:
                if m.start_date <= sim_date <= m.end_date:
                    if not which:
                        return True
                    elif m.start_date > last_date:
                        last_date = m.start_date
                        last = code
        if which and last is not None:
            return last
        return False

    def set_care_range(self, extra_months=0):
        first_date, last_date = self.care_range

        for diagnosis in self.diagnoses.iter_diagnoses():
            if diagnosis.start_date < first_date:
                first_date = diagnosis.start_date
            if diagnosis.end_date > last_date:
                last_date = diagnosis.end_date

        for atc_group in self.medications.values():
            for m in atc_group:
                if m.start_date < first_date:
                    first_date = m.start_date
                if m.end_date != datetime.date(datetime.MAXYEAR, 12, 31) and \
                   m.end_date > last_date:
                    last_date = m.end_date

        if first_date == datetime.date(datetime.MAXYEAR, 1, 1) or last_date == datetime.date(datetime.MINYEAR, 1, 1):
            raise ValueError("No patient information")

        self.care_range = (first_date, last_date + relativedelta(months=extra_months))


class DiagnosesDict(dict):
    def __init__(self, *args, **kw):
        super(DiagnosesDict, self).__init__(*args, **kw)
        self.last_diagnosis = None

    def add(self, diagnosis):
        if not type(diagnosis) is Diagnosis:
            raise(TypeError, "Type is not a Diagnosis")

        disease = diagnosis.disease
        if disease not in self.keys():
            super(DiagnosesDict, self).__setitem__(disease, [])
        self[disease].append(diagnosis)
        if self.last_diagnosis is None or self.last_diagnosis < diagnosis:
            self.last_diagnosis = diagnosis

    def iter_diagnoses(self):
        for diagnoses in self.values():
            for diagnosis in diagnoses:
                yield diagnosis

