import numpy as np
from dateutil.relativedelta import relativedelta
import copy


def get_diagnoses_per_practitioner(patients):
    practitioners = {}
    for p in patients.values():
        for diagnoses in p.diagnoses.values():
            for d in diagnoses:
                if not d.practitioner:
                    continue

                if d.practitioner not in practitioners:
                    practitioners[d.practitioner] = []

                practitioners[d.practitioner].append((p, d))
    return practitioners


def get_practitioner_score_count(practitioners):
    score_count = {k: {k_: 0 for k_ in range(10)} for k in practitioners.keys()}
    medication_count = copy.deepcopy(score_count)

    for code, practitioner_diagnoses in practitioners.items():
        for (patient, diagnosis) in practitioner_diagnoses:
            score = patient.calculate_chads_vasc(diagnosis.start_date)

            score_count[code][score] += 1
            if patient.has_medication_group("B01", diagnosis.start_date) or \
                    patient.has_medication_group("B01", diagnosis.start_date + relativedelta(days=+1)):
                medication_count[code][score] += 1

    return score_count, medication_count


def analyze_practitioners(patients):
    """
    Goal: Find per practitioner the percentage of patients with AC meds prescriptions
          over time separated by CHADS-VASC score
    """
    # TODO: split per year or something

    practitioners = get_diagnoses_per_practitioner(patients)
    practitioner_score_count, practitioner_medication_count = get_practitioner_score_count(practitioners)

    practitioners_medication_rate = {key: dict(zip(practitioner_score_count[key].keys(),
                                                   np.divide(list(practitioner_medication_count[key].values()),
                                                             list(practitioner_score_count[key].values()))))
                                     for key in practitioner_score_count.keys()}

    print(practitioners_medication_rate)

