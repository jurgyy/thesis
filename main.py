import numpy as np
import datetime
import json

import matplotlib.pyplot as plt

from csv_reader.diagnose_csv import get_diagnoses
from csv_reader.medication_csv import get_medications
from csv_reader.patients_csv import get_patients
from practitioner import analyze_practitioners
from simulations import compare_predictor_chads_vasc, find_adjusted_stroke_rate


def add_diseases(patients, diagnoses):
    for patient_nr, diagnoses in diagnoses.items():
        for diagnosis in diagnoses:
            patients[patient_nr].add_diagnosis(diagnosis)


def add_medications(patients, medications):
    for patient_nr, medication in medications.items():
        for m in medication:
            patients[patient_nr].add_medication(m)


def get_all_diseases(diagnoses):
    diseases = set()
    for patient_nr, diagnosis in diagnoses.items():
        for d in diagnosis:
            diseases.add(d.disease)

    return diseases


def get_disease_frequency(diseases, diagnoses):
    frequency = {d: 0 for d in diseases}

    for patient_diagnoses in diagnoses.values():
        for diagnosis in patient_diagnoses:
            if diagnosis.disease not in frequency:
                continue
            frequency[diagnosis.disease] += 1

    return frequency


def reduce_feature_space(diseases, diagnoses, min_frequency):
    frequency = get_disease_frequency(diseases, diagnoses)

    diseases = [d for d, f in frequency.items() if f >= min_frequency]
    return set(diseases)


def plot_disease_frequency(diseases, diagnoses):
    frequency = get_disease_frequency(diseases, diagnoses)

    labels, y = map(list, zip(*frequency.items()))
    labels = map(str, labels)

    y, labels = zip(*sorted(zip(y, labels)))

    x = range(len(labels))
    plt.barh(x, y, log=True)
    plt.yticks(x, labels)
    plt.show()


def read(loc):
    with open(loc, 'r') as f:
        try:
            data = json.load(f)
        except ValueError:
            data = {}

    return data


def write(loc, data):
    with open(loc, 'w') as f:
        json.dump(data, f)


def prepare_data():
    print("Reading CSV files...")
    patients = get_patients("data/msc_test/patients_general.csv")
    diagnoses = get_diagnoses("data/msc_test/patients_diseases.csv")
    medications = get_medications("data/msc_test/patient_meds.csv")

    add_diseases(patients, diagnoses)
    add_medications(patients, medications)

    diseases = get_all_diseases(diagnoses)
    diseases = reduce_feature_space(diseases, diagnoses, min_frequency=10)

    # plot_disease_frequency(diseases, diagnoses)
    for k, p in patients.items():
        p.find_strokes()
        p.find_chads_vasc_changes()

    return patients, diagnoses, diseases


def main():
    patients, diagnoses, diseases = prepare_data()

    start = datetime.date(2005, 1, 1)
    end = datetime.date(2015, 6, 1)
    # end = datetime.date(2007, 7, 1)

    # compare_predictor_chads_vasc(patients, diseases, start, end)
    # analyze_practitioners(patients, start, end)
    asr = find_adjusted_stroke_rate(patients, start, end)
    print(asr)

if __name__ == "__main__":
    main()
