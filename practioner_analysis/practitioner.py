import datetime

from dateutil.relativedelta import relativedelta

from disease import Disease
from practioner_analysis.medication_rate import MedicationRate
from practioner_analysis.plot import plot_data


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


def analyze_practitioners(patients, start, end, bin_months=1, meds_start_with="B01", spec="CAR", diag="401", plot=True):
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
        has_medication = patient.has_medication_group(meds_start_with, diagnosis.start_date) \
                      or patient.has_medication_group(meds_start_with, diagnosis.start_date + relativedelta(days=+1))

        data[diagnosis.practitioner][date_bins[i]].update(score, has_medication)

    if plot:
        plot_data(data, datetime.date(2015, 7, 1), mva=3)

    return data

