import pandas as pd

from csv_reader.reader import convert_to_date
from medication import Medication


def get_medications(loc, sep):
    converters = {'VRSCHRDAT': lambda x: convert_to_date(x)}
    dataframe = pd.read_csv(loc, sep=sep, converters=converters)
    
    dataframe['ACTSTOPDT'] = dataframe['ACTSTOPDT'].apply(convert_to_date)
    dataframe['ATCCODE'] = dataframe['ATCCODE'].fillna('0000000')

    medications = {}
    for m in dataframe.itertuples():
        if m.PATIENTNR not in medications:
            medications[m.PATIENTNR] = []
        medications[m.PATIENTNR].append(Medication(m.ATCCODE, m.VRSCHRDAT, m.ACTSTOPDT))

    return medications
    # TODO: remove duplicates like diagnoses
