import datetime
import pandas as pd
import numpy as np
import statsmodels.api as sm

from dateutil.relativedelta import relativedelta

from disease import Disease
from practioner_analysis.cdss_practitioners import cdss_practitioners
from practioner_analysis.medication_rate import MedicationRate
from practioner_analysis.plot import plot_data, group_data, plot_difference, plot_medication_breakdown


def get_month_bins(start, end, bin_size):
    date_bins = []
    cur_bin = start
    while cur_bin < end:
        date_bins.append(cur_bin)
        cur_bin += relativedelta(months=bin_size)

    date_bins.append(cur_bin)

    return date_bins


def get_practitioners(patients, spec=None):
    practitioners = set()

    for patient in patients.values():
        for diagnosis in patient.diagnoses.iter_diagnoses():
            if not diagnosis.practitioner:
                continue
            if diagnosis.disease.spec == spec or spec is None:
                practitioners.add(diagnosis.practitioner)

    return practitioners


def get_diagnosis_tuples(patients, disease=None):
    tuples = []
    for patient in patients.values():
        if disease:
            if disease not in patient.diagnoses:
                continue
            for diagnosis in patient.diagnoses[disease]:
                tuples.append((patient, diagnosis))
        else:
            for diagnosis in patient.diagnoses.iter_diagnoses():
                tuples.append((patient, diagnosis))

    return tuples


def regression_analysis(df):
    dummy_practitioners = pd.get_dummies(df["practitioner"], prefix='p')
    cols = ['CDSS', 'correct', 'score']
    print(dummy_practitioners.head())
    dummy_practitioners.drop(dummy_practitioners.columns[0], axis=1, inplace=True)
    print(dummy_practitioners.head())
    data = df[cols].join(dummy_practitioners)

    predict_col = 'correct'
    train_cols = list(data.columns)
    train_cols.remove(predict_col)

    data.info()
    logit = sm.Logit(data[predict_col], data[train_cols].astype(np.uint8))
    result = logit.fit()
    print(result.summary())
    print()
    print(result.conf_int())


def analyze_practitioners(patients, start, end, meds_start_with, bin_months=1, **kwargs):
    print("analyzing practitioners...")

    spec, diag = kwargs.get("spec"), kwargs.get("diag")
    practitioners = get_practitioners(patients, spec=spec)

    if spec is None or diag is None:
        disease = None
    else:
        disease = Disease(spec, diag)

    patient_diagnosis_tuples = get_diagnosis_tuples(patients, disease=disease)
    patient_diagnosis_tuples.sort(key=lambda tup: tup[1])

    date_bins = get_month_bins(start, end, bin_months)
    data = {k: {d: MedicationRate() for d in date_bins} for k in practitioners}
    i = 0

    regression_data = {"datum": [], "practitioner": [], "CDSS": [], "score": [], "correct": []}

    for patient, diagnosis in patient_diagnosis_tuples:
        if diagnosis.practitioner not in practitioners:
            continue
        if diagnosis.start_date < start:
            continue
        if diagnosis.start_date > end:
            break

        while diagnosis.start_date > date_bins[i + 1]:
            i += 1

        score = patient.calculate_chads_vasc(diagnosis.start_date)
        medication = patient.has_medication_group(meds_start_with, diagnosis.start_date, which=True) \
                     or patient.has_medication_group(meds_start_with, diagnosis.start_date + relativedelta(days=+1),
                                                     which=True)

        regression_data["datum"].append(diagnosis.start_date)
        regression_data["practitioner"].append(diagnosis.practitioner)
        regression_data["CDSS"].append(True
                                       if diagnosis.practitioner in cdss_practitioners and diagnosis.start_date >=
                                                                                           datetime.date(2015, 7, 1)
                                       else False)
        regression_data["correct"].append(1 if (score >= 2 and medication) or (score < 2 and not medication) else 0)
        regression_data["score"].append(score)

        data[diagnosis.practitioner][date_bins[i]].update(score, medication)

    df = pd.DataFrame(regression_data)
    df.to_csv("output/practitioner/{}regression_data.csv".format(kwargs.get("fname_prefix")), sep=";")

    if kwargs.get("plot"):
        print("plotting...")
        mva = 3
        split_date = datetime.date(2015, 7, 1)
        prefix = kwargs.get("fname_prefix")
        prefix = prefix if prefix is not None else ""

        fname = prefix + "Medication Rate All"
        title = "Medication rate per cardiologist over time"
        plot_data(data, split_date=split_date, mva=mva, fname=fname, title=title, legend=None)

        grouped_data = group_data(data, cdss_practitioners, "CDSS", "No CDSS")

        fname = prefix + "Medication Rate Grouped"
        title = "Medication rate over time grouped by use of CDSS"
        plot_data(grouped_data, split_date=split_date, mva=mva, fname=fname, title=title, legend=grouped_data.keys())
        fname = prefix + "Medication Rate Grouped Complete"
        plot_medication_breakdown(grouped_data, split_date=split_date, mva=mva, fname=fname, title=title,
                                  legend=grouped_data.keys())

        fname = prefix + "Medication Rate Difference"
        title = "Difference in medication rate over time grouped by score"
        plot_difference(grouped_data, split_date=split_date, mva=mva, fname=fname, title=title)

    regression_analysis(df)

    return data
