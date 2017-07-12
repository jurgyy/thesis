import datetime
from collections import Counter

import numpy as np
import timeit
import random

from dateutil.relativedelta import relativedelta

from anticoagulant_decision import future_stroke, chads_vasc
from disease_groups import *
from learning.confusion_matrix import ConfusionMatrix
from learning.predictor import predict, plot_matrices


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

    test_set = get_patient_subset(patients)
    while sim_date < end:
        for patient_nr, patient in patients.items():
            # Excluded patients are either:
            #  - Not alive
            #  - Don't have atrial fib (yet)
            #  - Last diagnosis was more than a year ago
            if (not patient.is_alive(sim_date)) or \
                    (not patient.has_disease_group(atrial_fib, sim_date, chronic=True)) or \
                    (patient.days_since_last_diagnosis(sim_date) > 366):  # or \
                    # not (patient.care_range[0] <= sim_date <= patient.care_range[1]):
                continue

            yield patient, sim_date, patient_nr not in test_set

        sim_date += relativedelta(months=+step)


def simulate_predictor(patients, diseases, start, end, day_since=True, chads_vasc_features=False):
    x_learn, y_learn, x_test, y_test = [], [], [], []
    learn_groups = []

    if chads_vasc_features:
        labels = ["C", "H", "D", "S", "V", "Gender", "Age"]
    else:
        labels = get_feature_labels(diseases)

    print("Simulating Predictor...\nStart Date: {}\nEnd Date: {}".format(start, end))
    start_timer = timeit.default_timer()

    for patient, sim_date, in_test_set in patient_month_generator(patients, start, end):
        if chads_vasc_features:
            x, y = get_chads_vasc_feature(patient, sim_date)
        else:
            x, y = get_feature_slice(diseases, patient, sim_date, days_since=day_since)

        if in_test_set:
            x_test.append(x)
            y_test.append(y)
        else:
            x_learn.append(x)
            y_learn.append(y)
            learn_groups.append(patient.number)

    stop_timer = timeit.default_timer()
    print("Time elapsed: {}".format(stop_timer - start_timer))

    return x_learn, y_learn, x_test, y_test, labels, learn_groups


def simulate_chads_vasc(patients, start, end, only_test_set=False):
    x, y = [], []
    print("Simulating CHADS-Vasc...\nStart Date: {}\nEnd Date: {}".format(start, end))
    for patient, sim_date, in_test_set in patient_month_generator(patients, start, end):
        if only_test_set and not in_test_set:
            continue
        x.append(1 if patient.should_have_AC(sim_date, chads_vasc, {"max_value": 3}) else 0)
        y.append(1 if patient.should_have_AC(sim_date, future_stroke, {"months": 12}) else 0)
    return x, y


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


def export_chads_vasc_data(ypred, y):
    np.save("output/learning/ypred_chads_vasc", ypred)
    np.save("output/learning/y_chads_vasc", y)


def import_chads_vasc_data():
    ypred = np.load("output/learning/ypred_chads_vasc.npy")
    y = np.load("output/learning/y_chads_vasc.npy")

    return ypred, y


def export_predictor_data(x_learn, y_learn, x_test, y_test, labels, learn_groups):
    np.save("output/learning/x_learn", x_learn)
    np.save("output/learning/y_learn", y_learn)
    np.save("output/learning/x_test", x_test)
    np.save("output/learning/y_test", y_test)
    np.save("output/learning/labels", labels)
    np.save("output/learning/learn_groups", learn_groups)


def import_predictor_data():
    x_learn = np.load("output/learning/x_learn.npy").tolist()
    y_learn = np.load("output/learning/y_learn.npy").tolist()
    x_test = np.load("output/learning/x_test.npy").tolist()
    y_test = np.load("output/learning/y_test.npy").tolist()
    labels = np.load("output/learning/labels.npy").tolist()
    learn_groups = np.load("output/learning/learn_groups.npy").tolist()

    return x_learn, y_learn, x_test, y_test, labels, learn_groups


def compare_predictor_chads_vasc(patients, diseases, start, end, load_from_file=False):
    seed = random.randint(0, 1000000)

    if load_from_file:
        print("Loading learn and test data from npy files...")
        ypred_chads_vasc, y_chads_vasc = import_chads_vasc_data()
        x_learn, y_learn, x_test, y_test, labels, learn_groups = import_predictor_data()
    else:
        random.seed(seed)
        ypred_chads_vasc, y_chads_vasc = simulate_chads_vasc(patients, start, end, only_test_set=True)
        export_chads_vasc_data(ypred_chads_vasc, y_chads_vasc)

        random.seed(seed)
        x_learn, y_learn, x_test, y_test, labels, learn_groups = simulate_predictor(patients, diseases,
                                                                                    start, end, day_since=True)
        export_predictor_data(x_learn, y_learn, x_test, y_test, labels, learn_groups)

    cm_chads_vasc = ConfusionMatrix(y_chads_vasc, ypred_chads_vasc, name="CHA$_2$DS$_2$-VASc")

    print("Predicting...")
    cm_prediction = predict(x_learn, y_learn, learn_groups,
                            x_test, y_test, labels, plot=True, cutoff=0.075)

    print("Plotting Confusion Matrices...")
    plot_matrices([cm_chads_vasc, cm_prediction])

    cm_chads_vasc.dump()
    cm_prediction.dump()
