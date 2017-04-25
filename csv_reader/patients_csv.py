import pandas as pd

from patient import Patient
from csv_reader.reader import  convert_to_date


def get_patients(loc):
    dataframe = pd.read_csv(loc, sep='\t')
    # Fields: PATIENTNR	VOORLETTER	ACHTERNAAM	GESLACHT	GEBDAT	OVERLEDEN	OVERLDAT	hasAC

    dataframe['GEBDAT'] = dataframe['GEBDAT'].apply(convert_to_date)
    dataframe['OVERLDAT'] = dataframe['OVERLDAT'].apply(convert_to_date)

    patients = {}

    for p in dataframe.itertuples():
        patients[p.PATIENTNR] = (Patient(p.PATIENTNR, p.GESLACHT, p.GEBDAT, p.OVERLDAT))

    return patients
