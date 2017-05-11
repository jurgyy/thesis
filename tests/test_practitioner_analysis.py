from datetime import date as d
import datetime
from unittest import TestCase, main
import numpy as np

from practitioner import *

from csv_reader.diagnose_csv import get_diagnoses
from csv_reader.medication_csv import get_medications
from csv_reader.patients_csv import get_patients

from main import add_diseases, add_medications

from diagnosis import Diagnosis
from medication import Medication
from patient import Patient
from disease import Disease


class TestPractitionerAnalysis(TestCase):
    patients = get_patients("test_data/test_patients.csv")
    diagnoses = get_diagnoses("test_data/test_diagnoses.csv", merge=False)
    medications = get_medications("test_data/test_meds.csv")

    add_diseases(patients, diagnoses)
    add_medications(patients, medications)

    def test_get_month_bins(self):
        start = d(2010, 1, 1)
        end = d(2012, 2, 1)
        bin_size = 3

        expected = [d(2010, 1, 1), d(2010, 4, 1), d(2010, 7, 1), d(2010, 10, 1),
                    d(2011, 1, 1), d(2011, 4, 1), d(2011, 7, 1), d(2011, 10, 1),
                    d(2012, 1, 1), d(2012, 4, 1)]

        self.assertEqual(expected, get_month_bins(start, end, bin_size=bin_size))

    def test_get_practitioners(self):
        practitioners = {"John Deer", "Jane Doe"}
        self.assertEqual(practitioners, get_practitioners(self.patients))
        self.assertEqual({"John Deer"}, get_practitioners(self.patients, spec="TE3"))
        self.assertEqual(practitioners, get_practitioners(self.patients, spec="TE1"))

    def test_get_diagnosis_tuples(self):
        disease_TE1_000 = Disease("TE1", "000", description="Test Disease 1")
        disease_TE1_001 = Disease("TE1", "001", description="Test Disease 2")
        disease_TE2_001 = Disease("TE2", "001", description="Test Disease 3")
        disease_TE3_001 = Disease("TE3", "001", description="Test Disease 4")

        p5 = Patient(5, "m", d(1931, 2, 3), d(datetime.MAXYEAR, 12, 31))
        p123 = Patient(123, "v", d(1999, 10, 11), d(2015, 1, 1))

        expected = [
            (p5, Diagnosis(disease_TE1_000, d(2010, 1, 1), d(2010, 1, 31), "John Deer")),
            (p5, Diagnosis(disease_TE1_000, d(2010, 2, 1), d(2010, 10, 31), "John Deer")),
            (p5, Diagnosis(disease_TE1_000, d(2010, 11, 1), d(2010, 12, 31), "Jane Doe")),
            (p5, Diagnosis(disease_TE1_000, d(2010, 4, 1), d(2010, 8, 6), "John Deer")),
            (p5, Diagnosis(disease_TE1_001, d(2010, 5, 1), d(2010, 6, 1), "John Deer")),
            (p5, Diagnosis(disease_TE2_001, d(2010, 6, 2), d(2011, 6, 2), "John Deer")),
            (p5, Diagnosis(disease_TE2_001, d(2010, 10, 1), d(2011, 10, 1), "John Deer")),
            (p5, Diagnosis(disease_TE3_001, d(2010, 3, 18), d(2010, 4, 19), "John Deer")),
            (p123, Diagnosis(disease_TE1_000, d(2010, 1, 1), d(2010, 1, 31), "John Deer")),
            (p123, Diagnosis(disease_TE2_001, d(2011, 6, 3), d(2012, 6, 2), "John Deer")),
            (p123, Diagnosis(disease_TE2_001, d(2015, 1, 1), d(2015, 5, 1), "John Deer"))
        ]

        result = get_diagnosis_tuples(self.patients)
        self.assertEqual(expected, result)

    def test_get_diagnosis_tuples_disease(self):
        disease_TE1_000 = Disease("TE1", "000", description="Test Disease 1")

        p5 = Patient(5, "m", d(1931, 2, 3), d(datetime.MAXYEAR, 12, 31))
        p123 = Patient(123, "v", d(1999, 10, 11), d(2015, 1, 1))

        expected = [
            (p5, Diagnosis(disease_TE1_000, d(2010, 1, 1), d(2010, 1, 31), "John Deer")),
            (p5, Diagnosis(disease_TE1_000, d(2010, 2, 1), d(2010, 10, 31), "John Deer")),
            (p5, Diagnosis(disease_TE1_000, d(2010, 11, 1), d(2010, 12, 31), "Jane Doe")),
            (p5, Diagnosis(disease_TE1_000, d(2010, 4, 1), d(2010, 8, 6), "John Deer")),
            (p123, Diagnosis(disease_TE1_000, d(2010, 1, 1), d(2010, 1, 31), "John Deer")),
        ]

        result = get_diagnosis_tuples(self.patients, disease=disease_TE1_000)
        self.assertEqual(expected, result)

    def test_analyze_practitioners(self):
        self.maxDiff = None
        bin_size = 3

        empty = MedicationRate()

        # The MedicationRate objects are manually filled according to the diagnosis and meds csv files.
        # CHADS-VASc scores don't change in this case, patient 123 always has a score of 1 and
        # patient 5 always a score of 2
        first = MedicationRate()
        first.total = Counter([1] + [2] * 4)

        second = MedicationRate()
        second.total = Counter([2] * 2)
        second.required = Counter([2])

        third = MedicationRate()
        third.total = Counter([2])
        third.required = Counter([2])

        fourth = MedicationRate()
        fourth.total = Counter([2])
        fourth.required = Counter([2])

        expected = {
            "John Deer": {d(2010, 1, 1): first,
                          d(2010, 4, 1): second,
                          d(2010, 7, 1): fourth,
                          d(2010, 10, 1): empty,
                          d(2011, 1, 1): empty,
                          d(2011, 4, 1): empty},
            "Jane Doe": {d(2010, 1, 1): empty,
                         d(2010, 4, 1): empty,
                         d(2010, 7, 1): empty,
                         d(2010, 10, 1): third,
                         d(2011, 1, 1): empty,
                         d(2011, 4, 1): empty}
        }

        start = d(2010, 1, 1)
        end = d(2011, 4, 1)
        outcome = analyze_practitioners(self.patients, start, end,
                                        bin_months=bin_size, meds_start_with="B", spec=None, diag=None, plot=False)
        self.assertEqual(expected, outcome)


if __name__ == "__main__":
    main()
