import datetime

import pandas as pd

from diagnosis import Diagnosis
from disease import Disease
from csv_reader.reader import convert_to_date


def get_diagnoses(loc):
    dataframe = pd.read_csv(loc, sep=';')
    # Fields: PATIENTNR	SPECIALISM	HOOFDDIAG	OMSCHRIJV	BEGINDAT	EINDDAT

    dataframe['BEGINDAT'] = dataframe['BEGINDAT'].apply(convert_to_date)

    dataframe['EINDDAT'] = dataframe['EINDDAT'].fillna(dataframe['BEGINDAT'] + pd.Timedelta(days=365))
    dataframe['EINDDAT'] = dataframe['EINDDAT'].apply(convert_to_date)

    diagnoses = {}
    for d in dataframe.itertuples():
        if d.PATIENTNR not in diagnoses:
            diagnoses[d.PATIENTNR] = []
        diagnoses[d.PATIENTNR].append(Diagnosis(Disease(d.SPECIALISM, d.HOOFDDIAG),
                                                d.BEGINDAT, d.EINDDAT))

    return merge_overlapping_diagnoses(diagnoses)


def group_diagnoses(diseases):
    dct = {}
    for d in diseases:
        if d.disease not in dct:
            dct[d.disease] = []
        dct[d.disease].append(d)

    return list(dct.values())


def remove_overlap(diagnoses):
    result = []
    current_start = datetime.date(1, 1, 1)
    current_stop = datetime.date(1, 1, 1)

    for diag in sorted(diagnoses):
        start = diag.start_date
        stop = diag.end_date

        if start - datetime.timedelta(days=1) > current_stop:
            result.append(diag)
            current_start, current_stop = start, stop
        else:
            result[-1] = Diagnosis(diag.disease, current_start, stop)
            current_stop = max(current_stop, stop)

    return result


def merge_overlapping_diagnoses(diagnoses):
    for patient_nr, ds in diagnoses.items():
        continuous_diagnoses = []

        for diagnosis_group in group_diagnoses(ds):
            continuous_diagnoses += remove_overlap(diagnosis_group)
        diagnoses[patient_nr] = continuous_diagnoses

    return diagnoses
