import numpy as np
import datetime
import json
import timeit
import random

import matplotlib.pyplot as plt

from dateutil.relativedelta import relativedelta

import anticoagulant_decision
from csv_reader.diagnose_csv import get_diagnoses
from csv_reader.patients_csv import get_patients
from disease import Disease
from disease_groups import stroke_diseases, atrial_fib
from learning.predictor import predict


def add_diseases(patients, diagnoses):
    for patient_nr, diagnoses in diagnoses.items():
        for diagnosis in diagnoses:
            patients[patient_nr].add_diagnosis(diagnosis)


def add_feature_slice(data, diseases, patient, sim_date):
    # TODO: Somehow not include strokes as actual features
    feature_vector = [1 if patient.has_disease(d, sim_date, chronic=True) else 0 for d in diseases]
    feature_vector += [patient.days_since_diagnosis(d, sim_date) if feature_vector[i] else 0
                       for i, d in enumerate(diseases)]

    feature_vector.append(1 if patient.is_female() else 0)
    feature_vector.append(patient.calculate_age(sim_date))

    data["Data"].append(feature_vector)
    data["Target"].append(patient.should_have_AC(sim_date, anticoagulant_decision.future_stroke,
                                                 {"months": 12}))

    # TODO: would be more efficient if adding labels could be done before the simulation
    if len(data["Data Labels"]) < len(feature_vector):
        data["Data Labels"] = [str(d) for d in diseases]
        data["Data Labels"] += ["days since {}".format(d) for d in diseases]
        data["Data Labels"] += ["Gender", "Age"]


def get_all_diseases(diagnoses):
    diseases = set()
    for patient_nr, diagnosis in diagnoses.items():
        for d in diagnosis:
            diseases.add(d.disease)

    return diseases


def get_disease_frequency(diseases, diagnoses):
    frequency = {d: 0 for d in diseases}

    for _, patient_diagnoses in diagnoses.items():
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


def get_random_subset(patients, test_rate=0.30):
    patient_nrs = list(patients.keys())
    test_size = round(len(patient_nrs) * test_rate)

    random.shuffle(patient_nrs)

    # Workaround for np.int64 to native int conversion; perhaps there's a better way
    return np.array(patient_nrs[0:test_size]).tolist()


def sim(patients, diseases, write_output=False):
    sim_date = datetime.date(2008, 1, 1)
    sim_end_date = datetime.date(2011, 7, 1)

    start = timeit.default_timer()

    for k, p in patients.items():
        p.find_strokes()
        p.find_chads_vasc_changes()

    learn_data = {"Data": [], "Target": [], "Data Labels": []}
    test_data = {"Data": [], "Target": [], "Data Labels": [], "Patients": get_random_subset(patients)}

    print("Simulating...\nStart Date: {}\nEnd Date: {}".format(sim_date, sim_end_date))
    while sim_date < sim_end_date:
        print(sim_date)
        for key, patient in patients.items():
            if (not patient.is_alive(sim_date)) or \
                    (not patient.has_disease_group(atrial_fib, sim_date, chronic=True)):
                continue

            if key in test_data["Patients"]:
                add_feature_slice(test_data, diseases, patient, sim_date)
            else:
                add_feature_slice(learn_data, diseases, patient, sim_date)

        sim_date += relativedelta(months=+1)

    stop = timeit.default_timer()
    print("Time elapsed: {}".format(stop - start))

    if write_output:
        print("Writing output file...")
        write("output/learn_data.json", learn_data)
        write("output/test_data.json", test_data)

    return learn_data, test_data


def main(cache=False):
    if cache:
        print("Reading...")
        learn = read("output/learn_data.json")
        test = read("output/test_data.json")
    else:
        print("Loading Data...")
        patients = get_patients("data/msc_test/patients_general.csv")
        diagnoses = get_diagnoses("data/msc_test/patients_diseases.csv")

        add_diseases(patients, diagnoses)

        diseases = get_all_diseases(diagnoses)
        diseases = reduce_feature_space(diseases, diagnoses, min_frequency=4)
        # plot_disease_frequency(diseases, diagnoses)

        learn, test = sim(patients, diseases, write_output=False)

    print("Predicting...")
    predict(learn, test)


if __name__ == "__main__":
    main(cache=False)
