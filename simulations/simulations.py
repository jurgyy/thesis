import numpy as np
import timeit
import datetime
import random
from collections import Counter
from matplotlib.pyplot import cm

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

    y = patient.should_have_AC(sim_date, future_stroke, months=12)
    return x, y


def get_feature_slice(diseases, patient, sim_date, days_since=True):
    if days_since:
        x = [patient.days_since_diagnosis(d, sim_date) if patient.has_disease(d, sim_date, chronic=True)
             else 10000 for i, d in enumerate(diseases)]
    else:
        x = [1 if patient.has_disease(d, sim_date, chronic=True) else 0 for d in diseases]

    x.append(1 if patient.is_female() else 0)
    x.append(patient.calculate_age(sim_date))

    y = patient.should_have_AC(sim_date, future_stroke, months=12)

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


def patient_month_generator(patients, start, end, step=1, include_meds=False):
    sim_date = start
    # TODO: move split to other somewhere else

    test_set = get_patient_subset(patients)
    while sim_date < end:
        for patient_nr, patient in patients.items():
            # Excluded patients are either:
            #  - Not alive
            #  - Don't have atrial fib (yet)
            #  - Last diagnosis was more than a year ago
            #  - Receive Antithrombotics
            if patient.is_alive(sim_date) \
               and patient.has_disease_group(atrial_fib, sim_date, chronic=True) \
               and patient.days_since_last_diagnosis(sim_date) <= 365 \
               and (not patient.has_medication_group("B01", sim_date) or include_meds):  # Antithrombotic Agents start with B01
                yield patient, sim_date, patient_nr not in test_set

        sim_date += relativedelta(months=+step)


def simulate_predictor(patients, diseases, start, end, day_since=True, chads_vasc_features=False):
    x_learn, y_learn, x_test, y_test = [], [], [], []
    learn_groups, scores = [], []

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
            scores.append(patient.calculate_chads_vasc(sim_date))
        else:
            x_learn.append(x)
            y_learn.append(y)
            learn_groups.append(patient.number)

    stop_timer = timeit.default_timer()
    print("Time elapsed: {}".format(stop_timer - start_timer))

    return x_learn, y_learn, x_test, y_test, labels, learn_groups, scores


def simulate_chads_vasc(patients, start, end, only_test_set=False):
    x, y, scores = [], [], []
    print("Simulating CHADS-Vasc...\nStart Date: {}\nEnd Date: {}".format(start, end))
    for patient, sim_date, in_test_set in patient_month_generator(patients, start, end):
        if only_test_set and not in_test_set:
            continue
        x.append(1 if patient.should_have_AC(sim_date, chads_vasc, max_value=2) else 0)
        y.append(1 if patient.should_have_AC(sim_date, future_stroke, months=12) else 0)
        scores.append(patient.calculate_chads_vasc(sim_date))
    return x, y, scores


def get_group_dict(score_groups, y_true, y_pred, scores):
    print(score_groups)
    score_group_map = {}
    for i in range(10):
        index = -1
        for j, g in enumerate(score_groups):
            if i in g:
                index = j
                break

        score_group_map[i] = index if index >= 0 else len(score_groups)

    grouped = {k: ([], []) for k in range(len(score_groups) + 1)}
    print(grouped)
    print(score_group_map)
    for true, pred, score in zip(y_true, y_pred, scores):
        index = score_group_map[score]
        grouped[index][0].append(true)
        grouped[index][1].append(pred)

    return grouped


def get_grouped_matrices(models, score_groups, names):
    max_score = score_groups[-1][-1]
    score_labels = ["{} - {}".format(l[0], l[-1]) if len(l) > 1 else str(l[0]) for l in score_groups] + \
                   ["$\geq${}".format(max_score + 1)]

    grouped_data = []
    for true, pred, scores in models:
        grouped_data.append(get_group_dict(score_groups, true, pred, scores))

    cms = []
    for i, l in enumerate(score_labels):
        for j, g in enumerate(grouped_data):
            print("Group {}\t#Positive: {}\tTotal: {}".format(l, sum(g[i][0]), len(g[i][0])))
            cms.append(ConfusionMatrix(g[i][0], g[i][1], name="{} {}".format(l, names[j])))

    return cms


def export_chads_vasc_data(ypred, y, scores):
    np.save("output/learning/ypred_chads_vasc", ypred)
    np.save("output/learning/y_chads_vasc", y)
    np.save("output/learning/chads_vasc_scores", scores)


def import_chads_vasc_data():
    ypred = np.load("output/learning/ypred_chads_vasc.npy")
    y = np.load("output/learning/y_chads_vasc.npy")
    scores = np.load("output/learning/chads_vasc_scores.npy")

    return ypred, y, scores


def export_predictor_data(x_learn, y_learn, x_test, y_test, labels, learn_groups, test_scores):
    np.save("output/learning/x_learn", x_learn)
    np.save("output/learning/y_learn", y_learn)
    np.save("output/learning/x_test", x_test)
    np.save("output/learning/y_test", y_test)
    np.save("output/learning/labels", labels)
    np.save("output/learning/learn_groups", learn_groups)
    np.save("output/learning/test_scores", test_scores)


def import_predictor_data():
    x_learn = np.load("output/learning/x_learn.npy").tolist()
    y_learn = np.load("output/learning/y_learn.npy").tolist()
    x_test = np.load("output/learning/x_test.npy").tolist()
    y_test = np.load("output/learning/y_test.npy").tolist()
    labels = np.load("output/learning/labels.npy").tolist()
    learn_groups = np.load("output/learning/learn_groups.npy").tolist()
    test_scores = np.load("output/learning/test_scores.npy").tolist()

    return x_learn, y_learn, x_test, y_test, labels, learn_groups, test_scores


def compare_predictor_chads_vasc(patients, diseases, start, end, load_from_file=False):
    if load_from_file:
        print("Loading learn and test data from npy files...")
        ypred_chads_vasc, y_chads_vasc, chads_vasc_scores = import_chads_vasc_data()
        x_learn, y_learn, x_test, y_test, labels, learn_groups, test_scores = import_predictor_data()
    else:
        seed = random.randint(0, 1000000)
        print("Used seed: {}".format(seed))
        random.seed(seed)
        ypred_chads_vasc, y_chads_vasc, chads_vasc_scores = simulate_chads_vasc(patients, start, end, only_test_set=True)
        export_chads_vasc_data(ypred_chads_vasc, y_chads_vasc, chads_vasc_scores)

        random.seed(seed)
        x_learn, y_learn, x_test, y_test, labels, learn_groups, test_scores = simulate_predictor(
            patients, diseases, start, end, day_since=True
        )
        export_predictor_data(x_learn, y_learn, x_test, y_test, labels, learn_groups, test_scores)

    cm_chads_vasc = ConfusionMatrix(y_chads_vasc, ypred_chads_vasc, name="CHA$_2$DS$_2$-VASc")

    print("Predicting with unknown cutoff...")
    predictions_unknown = predict(x_learn, y_learn, learn_groups,
                                  x_test, y_test, labels, plot=True, s_beta=2, cutoff=0.05)
    cm_prediction_unknown = ConfusionMatrix(y_test, predictions_unknown, name=r'RF c=0.05')

    print("Predicting with fixed cutoff: 0.015...")
    predictions_fixed = predict(x_learn, y_learn, learn_groups,
                                x_test, y_test, labels, plot=False, cutoff=0.015)
    cm_prediction_fixed = ConfusionMatrix(y_test, predictions_fixed, name="RF c=0.015")

    # Hard to separate in functions
    print("Plotting Confusion Matrices...")

    def cm_plot_data(cm, **kwargs):
        s_beta = kwargs.get("s_beta", 2)
        data = [cm.tpr, cm.fpr, cm.fnr, cm.tnr, cm.s_beta(s_beta)]
        labels = ["True Positive\nRate", "False Positive\nRate", "False Negative\nRate", "True Negative\nRate",
                  r'$S_{}$ Score'.format(s_beta)]
        return data, labels

    plot_matrices([cm_prediction_unknown, cm_prediction_fixed, cm_chads_vasc], cm_plot_data, "performance", s_beta=2,
                  title="Performance comparison of Random Forests and CHA$_2$DS$_2$-VASc")

    def cm_plot_data(cm, **kwargs):
        data = [cm.tpr, cm.tnr]
        labels = ["True Positive\nRate", "True Negative\nRate"]
        return data, labels

    def cm_three_pair(n):
        return cm.tab20c(n + n // 3)

    score_groups = [[0, 1], [2, 3]]
    data = [
        [y_test, predictions_unknown, test_scores],
        [y_test, predictions_fixed, test_scores],
        [y_chads_vasc, ypred_chads_vasc, chads_vasc_scores]
    ]
    names = ["RF c=0.05", "RF c=0.015", "CHA$_2$DS$_2$-VASc"]
    cms = get_grouped_matrices(data, score_groups, names=names)
    plot_matrices(cms, cm_plot_data, "performance_scored", cm=cm_three_pair,
                  title="Performance comparison grouped by CHA$_2$DS$_2$-VASC score")

    cm_chads_vasc.dump()
    cm_prediction_unknown.dump()
    cm_prediction_fixed.dump()
