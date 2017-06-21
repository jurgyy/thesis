import pandas as pd
import datetime

from patient import Patient


def get_patients(loc):
    dataframe = pd.read_csv(loc, sep='\t')
    # Fields: PATIENTNR GESLACHT LEEFTIJD OVERLEDEN OVRLLEEFTIJD

    patients = {}

    for p in dataframe.itertuples():
        birth_date = datetime.date(2018 - int(p.LEEFTIJD), 1, 1)
        death_date = datetime.date(birth_date.year + int(p.OVRLLEEFTIJD), 1, 1)\
            if not pd.isnull(p.OVRLLEEFTIJD) else datetime.date(datetime.MAXYEAR, 12, 31)

        patients[p.PATIENTNR] = Patient(p.PATIENTNR, p.GESLACHT.lower(), birth_date, death_date)

    return patients
