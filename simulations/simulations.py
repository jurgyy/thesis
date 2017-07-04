import datetime
from collections import Counter

import numpy as np
import timeit
import random

from dateutil.relativedelta import relativedelta

from anticoagulant_decision import future_stroke, chads_vasc
from disease_groups import *
from learning.predictor import predict, analyze_chads_vasc


def get_chads_vasc_feature(patient, sim_date):
    groups = [chads_vasc_c, chads_vasc_h, chads_vasc_d, chads_vasc_s, chads_vasc_v]

    x = [1 if patient.has_disease_group(g, sim_date, chronic=True) else 0 for g in groups]
    x.append(1 if patient.is_female() else 0)
    x.append(patient.calculate_age(sim_date))

    y = patient.should_have_AC(sim_date, future_stroke, {"months": 12})
    return x, y


def get_feature_slice(diseases, patient, sim_date, days_since=True):
    if days_since:
        x = [patient.days_since_diagnosis(d, sim_date) if patient.has_disease(d, sim_date, chronic=True)
             else 10000 for i, d in enumerate(diseases)]
    else:
        x = [1 if patient.has_disease(d, sim_date, chronic=True) else 0 for d in diseases]

    x.append(1 if patient.is_female() else 0)
    x.append(patient.calculate_age(sim_date))

    y = patient.should_have_AC(sim_date, future_stroke, {"months": 12})

    return x, y


def get_feature_labels(diseases):
    """ Make sure that this function is in line with get_feature_slice() """
    labels = [str(d) for d in diseases]
    labels += ["Gender", "Age"]

    return labels


def get_random_subset(patients, test_rate=0.30, seed=None):
    patient_nrs = list(patients.keys())
    test_size = round(len(patient_nrs) * test_rate)

    if seed:
        random.seed(seed)
    random.shuffle(patient_nrs)

    # Workaround for np.int64 to native int conversion; perhaps there's a better way
    return np.array(patient_nrs[0:test_size]).tolist()


def get_patient_subset(patients, stroke_patient_rate=0.5, seed=None):
    positive_patients = []
    negative_patients = []

    for patient_nr, patient in patients.items():
        if patient.has_disease_group(stroke_diseases, datetime.date(2050, 1, 1), chronic=True):
            positive_patients.append(patient_nr)
        else:
            negative_patients.append(patient_nr)

    half_learn_size = int(len(positive_patients) * stroke_patient_rate)

    if seed:
        random.seed(seed)
    random.shuffle(positive_patients)
    random.shuffle(negative_patients)

    learn_set = positive_patients[:half_learn_size] + negative_patients[0:half_learn_size]
    return learn_set


def patient_month_generator(patients, start, end, step=1, test_rate=.20):
    sim_date = start
    # TODO: move split to other somewhere else
    # test_set = get_random_subset(patients, test_rate=test_rate)
    test_set = get_patient_subset(patients)
    while sim_date < end:
        for patient_nr, patient in patients.items():
            # Excluded patients are either:
            #  - Not alive
            #  - Don't have atrial fib (yet)
            #  - Last diagnosis was more than a year ago
            #  - Are receiving antithrombotic agents (this skews the results), temporarily turned off
            if (not patient.is_alive(sim_date)) or \
                    (not patient.has_disease_group(atrial_fib, sim_date, chronic=True)) or \
                    (patient.days_since_last_diagnosis(sim_date) > 366):  # or \
                    # patient.has_medication_group("B01", sim_date):  # Antithrombotic Agents start with B01
                continue

            yield patient, sim_date, patient_nr not in test_set

        sim_date += relativedelta(months=+step)


def simulate_predictor(patients, diseases, start, end, day_since=True):
    learn_data = {"Data": [], "Target": []}
    test_data = {"Data": [], "Target": []}

    start_timer = timeit.default_timer()
    print("Simulating Predictor...\nStart Date: {}\nEnd Date: {}".format(start, end))

    learn_data["Data Labels"] = get_feature_labels(diseases)
    # learn_data["Data Labels"] = ["C", "H", "D", "S", "V", "Gender", "Age"]
    test_data["Data Labels"] = learn_data["Data Labels"]

    for patient, sim_date, in_test_set in patient_month_generator(patients, start, end):
        features, target = get_feature_slice(diseases, patient, sim_date, days_since=day_since)
        # features, target = get_chads_vasc_feature(patient, sim_date)
        if in_test_set:
            test_data["Data"].append(features)
            test_data["Target"].append(target)
        else:
            learn_data["Data"].append(features)
            learn_data["Target"].append(target)

    stop_timer = timeit.default_timer()
    print("Time elapsed: {}".format(stop_timer - start_timer))

    return learn_data, test_data


def simulate_chads_vasc(patients, start, end, only_test_set=False):
    print("Simulating CHADS-Vasc...\nStart Date: {}\nEnd Date: {}".format(start, end))
    data = {"Data": [], "Target": []}
    for patient, sim_date, in_test_set in patient_month_generator(patients, start, end):
        if only_test_set and not in_test_set:
            continue
        data["Data"].append(1 if patient.should_have_AC(sim_date, chads_vasc, {"max_value": 3}) else 0)
        data["Target"].append(1 if patient.should_have_AC(sim_date, future_stroke, {"months": 12}) else 0)
    return data


def find_adjusted_stroke_rate(patients, start, end):
    score_counter = Counter()
    stroke_counter = Counter()
    for patient, sim_date, _ in patient_month_generator(patients, start, end, step=12):
        score = patient.calculate_chads_vasc(sim_date)
        score_counter[score] += 1

        if patient.should_have_AC(sim_date, future_stroke, {"months": 12}):
            stroke_counter[score] += 1

    asr = {}
    with np.errstate(divide='ignore', invalid='ignore'):
        baseline_rate = np.divide(stroke_counter[0], score_counter[0])
        print("baseline rate: {}".format(baseline_rate))
        for i in range(10):
            print("{}) {}    {}".format(i, stroke_counter[i], score_counter[i]))
            asr[i] = np.divide(stroke_counter[i], score_counter[i]) - baseline_rate

    return asr


def export_data(learn, test):
    np.save("output/data", learn["Data"] + test["Data"])
    np.save("output/target", learn["Target"] + test["Target"])
    np.save("output/labels", learn["Data Labels"])


def import_data(test_rate=0.2):
    data = np.load("output/data.npy")
    target = np.load("output/target.npy")
    labels = np.load("output/labels.npy")
    
    split = 1 - round(len(data) * test_rate)

    learn = {"Data": data[0:split].tolist(),
             "Target": target[0:split].tolist(),
             "Data Labels": labels}
    test = {"Data": data[split:].tolist(),
            "Target": target[split:].tolist(),
            "Data Labels": labels}

    return learn, test


def compare_predictor_chads_vasc(patients, diseases, start, end, load_from_file=False):
    seed = random.randint(0, 1000000)

    random.seed(seed)
    chads_vasc_data = simulate_chads_vasc(patients, start, end, only_test_set=True)

    if load_from_file:
        learn, test = import_data()
    else:
        random.seed(seed)
        learn, test = simulate_predictor(patients, diseases, start, end)
        export_data(learn, test)

    print("CHADS-VASc...")
    cf_chads_vasc = analyze_chads_vasc(chads_vasc_data)

    print("Predicting...")
    cf_prediction = predict(learn["Data"], learn["Target"],
                            test["Data"], test["Target"],
                            learn["Data Labels"], plot=True)

    cf_chads_vasc.dump()
    cf_prediction.dump()
