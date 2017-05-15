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


def get_random_subset(patients, test_rate=0.30):
    patient_nrs = list(patients.keys())
    test_size = round(len(patient_nrs) * test_rate)

    random.shuffle(patient_nrs)

    # Workaround for np.int64 to native int conversion; perhaps there's a better way
    return np.array(patient_nrs[0:test_size]).tolist()


def patient_month_generator(start, end, patients):
    sim_date = start
    while sim_date < end:
        for key, patient in patients.items():
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

            yield key, patient, sim_date

        sim_date += relativedelta(months=+1)


def simulate_predictor(patients, diseases, start, end):
    learn_data = {"Data": [], "Target": [], "Data Labels": []}
    test_data = {"Data": [], "Target": [], "Data Labels": [], "Patients": get_random_subset(patients, test_rate=.70)}

    start_timer = timeit.default_timer()
    print("Simulating...\nStart Date: {}\nEnd Date: {}".format(start, end))
    for key, patient, sim_date in patient_month_generator(start, end, patients):
        if key in test_data["Patients"]:
            add_feature_slice(test_data, diseases, patient, sim_date)
        else:
            add_feature_slice(learn_data, diseases, patient, sim_date)

    stop_timer = timeit.default_timer()
    print("Time elapsed: {}".format(stop_timer - start_timer))

    return learn_data, test_data


def simulate_chads_vasc(patients, start, end):
    print("Simulating...\nStart Date: {}\nEnd Date: {}".format(start, end))
    data = {"Data": [], "Target": []}
    for key, patient, sim_date in patient_month_generator(start, end, patients):
        data["Data"].append(1 if patient.should_have_AC(sim_date, chads_vasc, {"max_value": 3}) else 0)
        data["Target"].append(1 if patient.should_have_AC(sim_date, future_stroke, {"months": 12}) else 0)
    return data


def compare_predictor_chads_vasc(patients, diseases, start, end):
    for k, p in patients.items():
        p.find_strokes()
        p.find_chads_vasc_changes()

    chads_vasc_data = simulate_chads_vasc(patients, start, end)
    # TODO: Find the true adjusted stroke rate
    learn, test = simulate_predictor(patients, diseases, start, end)

    print("CHADS-VASc...")
    cf_chads_vasc = analyze_chads_vasc(chads_vasc_data)

    print("Predicting...")
    cf_prediction = predict(learn, test, plot=True)

    cf_chads_vasc.dump()
    cf_prediction.dump()
