import pandas as pd

from patient import Patient
from csv_reader.reader import convert_to_date


def get_patients(loc):
    converters = {'GEBDAT': lambda x: convert_to_date(x),
                  'OVERLDAT': lambda x: convert_to_date(x)}
    dataframe = pd.read_csv(loc, sep='\t', converters=converters)
    # Fields: PATIENTNR	VOORLETTER	ACHTERNAAM	GESLACHT	GEBDAT	OVERLEDEN	OVERLDAT	hasAC

    patients = {}

    for p in dataframe.itertuples():
        patients[p.PATIENTNR] = (Patient(p.PATIENTNR, p.GESLACHT, p.GEBDAT, p.OVERLDAT))

    return patients
