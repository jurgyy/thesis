import datetime

import pandas as pd

from diagnosis import Diagnosis
from disease import Disease
from csv_reader.reader import convert_to_date


def get_diagnoses(loc):
    converters = {'HOOFDDIAG': lambda x: str(x),
                  'UITVOERDER': lambda x: str(x),
                  'BEGINDAT': lambda x: convert_to_date(x)}
    dataframe = pd.read_csv(loc, sep='\t', converters=converters)
    # Fields: PATIENTNR	SPECIALISM	HOOFDDIAG	OMSCHRIJV	UITVOERDER	BEGINDAT	EINDDAT

    dataframe['EINDDAT'] = dataframe['EINDDAT'].fillna(dataframe['BEGINDAT'] + pd.Timedelta(days=365))
    # TODO: 365 vs 120 days when EINDAT is null
    dataframe['EINDDAT'] = dataframe['EINDDAT'].apply(convert_to_date)

    diagnoses = {}
    for d in dataframe.itertuples():
        if d.PATIENTNR not in diagnoses:
            diagnoses[d.PATIENTNR] = []
        diagnoses[d.PATIENTNR].append(Diagnosis(Disease(str(d.SPECIALISM), str(d.HOOFDDIAG),
                                                        description=str(d.OMSCHRIJV)),
                                                d.BEGINDAT, d.EINDDAT, practitioner=d.UITVOERDER))

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
    prev = None

    for diag in sorted(diagnoses):
        start = diag.start_date
        stop = diag.end_date

        if (prev and prev.practitioner != diag.practitioner) or start - datetime.timedelta(days=1) > current_stop:
            result.append(diag)
            current_start, current_stop = start, stop
        else:
            current_stop = max(current_stop, stop)
            result[-1] = Diagnosis(diag.disease, current_start, current_stop, practitioner=diag.practitioner)

        prev = diag
    return result


def merge_overlapping_diagnoses(diagnoses):
    for patient_nr, ds in diagnoses.items():
        continuous_diagnoses = []

        for diagnosis_group in group_diagnoses(ds):
            continuous_diagnoses += remove_overlap(diagnosis_group)
        diagnoses[patient_nr] = continuous_diagnoses

    return diagnoses
