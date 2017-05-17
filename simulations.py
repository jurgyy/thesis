from collections import Counter

import numpy as np
import timeit
import random

from dateutil.relativedelta import relativedelta

from anticoagulant_decision import future_stroke, chads_vasc
from disease_groups import atrial_fib
from learning.predictor import predict, analyze_chads_vasc


def add_feature_slice(data, diseases, patient, sim_date):
    feature_vector = [1 if patient.has_disease(d, sim_date, chronic=True) else 0 for d in diseases]
    feature_vector += [patient.days_since_diagnosis(d, sim_date) if feature_vector[i] else 0
                       for i, d in enumerate(diseases)]

    feature_vector.append(1 if patient.is_female() else 0)
    feature_vector.append(patient.calculate_age(sim_date))

    data["Data"].append(feature_vector)
    data["Target"].append(patient.should_have_AC(sim_date, future_stroke, {"months": 12}))

    # TODO: would be more efficient if adding labels could be done before the simulation
    if len(data["Data Labels"]) < len(feature_vector):
        data["Data Labels"] = [str(d) for d in diseases]
        data["Data Labels"] += ["days since {}".format(d) for d in diseases]
        data["Data Labels"] += ["Gender", "Age"]


def get_random_subset(patients, test_rate=0.30, seed=None):
    patient_nrs = list(patients.keys())
    test_size = round(len(patient_nrs) * test_rate)

    if seed:
        random.seed(seed)
    random.shuffle(patient_nrs)

    # Workaround for np.int64 to native int conversion; perhaps there's a better way
    return np.array(patient_nrs[0:test_size]).tolist()


def patient_month_generator(start, end, patients, step=1, test_rate=.20):
    sim_date = start
    test_set = get_random_subset(patients, test_rate=test_rate)
    while sim_date < end:
        for patient_nr, patient in patients.items():
            # Excluded patients are either:
            #  - Not alive
            #  - Don't have atrial fib (yet)
            #  - Last diagnosis was more than a year ago
            #  - Are receiving antithrombotic agents (this skews the results)
            if (not patient.is_alive(sim_date)) or \
                    (not patient.has_disease_group(atrial_fib, sim_date, chronic=True)) or \
                    (patient.days_since_last_diagnosis(sim_date) > 366) or \
                    patient.has_medication_group("B01", sim_date):  # Antithrombotic Agents start with B01
                continue

            yield patient, sim_date, patient_nr in test_set

        sim_date += relativedelta(months=+step)


def simulate_predictor(patients, diseases, start, end):
    learn_data = {"Data": [], "Target": [], "Data Labels": []}
    test_data = {"Data": [], "Target": [], "Data Labels": []}

    start_timer = timeit.default_timer()
    print("Simulating...\nStart Date: {}\nEnd Date: {}".format(start, end))
    for patient, sim_date, in_test_set in patient_month_generator(start, end, patients):
        if in_test_set:
            add_feature_slice(test_data, diseases, patient, sim_date)
        else:
            add_feature_slice(learn_data, diseases, patient, sim_date)

    stop_timer = timeit.default_timer()
    print("Time elapsed: {}".format(stop_timer - start_timer))

    return learn_data, test_data


def simulate_chads_vasc(patients, start, end, only_test_set=False):
    print("Simulating...\nStart Date: {}\nEnd Date: {}".format(start, end))
    data = {"Data": [], "Target": []}
    for patient, sim_date, in_test_set in patient_month_generator(start, end, patients):
        if only_test_set and not in_test_set:
            continue
        data["Data"].append(1 if patient.should_have_AC(sim_date, chads_vasc, {"max_value": 3}) else 0)
        data["Target"].append(1 if patient.should_have_AC(sim_date, future_stroke, {"months": 12}) else 0)
    return data


def find_adjusted_stroke_rate(patients, start, end):
    score_counter = Counter()
    stroke_counter = Counter()
    for patient, sim_date, _ in patient_month_generator(start, end, patients, step=12):
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


def compare_predictor_chads_vasc(patients, diseases, start, end):
    seed = random.randint(0, 1000)

    random.seed(seed)
    chads_vasc_data = simulate_chads_vasc(patients, start, end, only_test_set=True)

    random.seed(seed)
    learn, test = simulate_predictor(patients, diseases, start, end)

    print("CHADS-VASc...")
    cf_chads_vasc = analyze_chads_vasc(chads_vasc_data)

    print("Predicting...")
    cf_prediction = predict(learn, test, plot=True)

    cf_chads_vasc.dump()
    cf_prediction.dump()
