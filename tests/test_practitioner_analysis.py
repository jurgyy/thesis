import datetime
from collections import Counter
from datetime import date as d
from unittest import TestCase, main

import numpy as np

from csv_reader.diagnose_csv import get_diagnoses
from csv_reader.medication_csv import get_medications
from csv_reader.patients_csv import get_patients
from diagnosis import Diagnosis
from disease import Disease
from main import add_diseases, add_medications
from patient import Patient
from practioner_analysis.medication_rate import MedicationRate
from practioner_analysis.practitioner import get_month_bins, get_practitioners, get_diagnosis_tuples, \
    analyze_practitioners


class TestMedicationRate(TestCase):
    rate = MedicationRate()
    for i in range(10):
        for j in range(i):
            rate.update(i, j % 2 == 0)

    def test_update(self):
        self.assertEqual(self.rate.total,
                         Counter({1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9}))

        self.assertEqual(self.rate.with_medication,
                         Counter({1: 1, 2: 1, 3: 2, 4: 2, 5: 3, 6: 3, 7: 4, 8: 4, 9: 5}))

    def test_get_rates(self):
        self.assertTrue(np.allclose(self.rate.get_rates(),
                                    np.array([float('nan'), 1, 0.5, 2/3, 0.5, 0.6, 0.5, 4/7, 0.5, 5/9]),
                                    rtol=1e-05, atol=1e-08, equal_nan=True))

    def test_get_count_threshold(self):
        self.assertEqual(self.rate.get_count_threshold(0),
                         (sum(self.rate.with_medication.values()), sum(self.rate.total.values())))

        self.assertEqual(self.rate.get_count_threshold(5), (19, 35))

    def test_get_rate_threshold(self):
        self.assertEqual(self.rate.get_rate_threshold(0),
                         sum(self.rate.with_medication.values()) / sum(self.rate.total.values()))

        self.assertEqual(self.rate.get_rate_threshold(5), 19 / 35)

    def test_add_medication_rates(self):
        def get_numbers(mr):
            with_meds = []
            total = []
            for i in range(10):
                with_meds.append(mr.with_medication[i])
                total.append(mr.total[i])
            return with_meds, total

        a = MedicationRate()
        b = MedicationRate()

        self.assertEqual(a + b, MedicationRate())

        a.update(0, False)
        a.update(1, False)
        a.update(1, True)
        a.update(3, True)

        self.assertEqual(get_numbers(a + b), ([0, 1, 0, 1, 0, 0, 0, 0, 0, 0], [1, 2, 0, 1, 0, 0, 0, 0, 0, 0]))

        b.update(1, True)
        b.update(2, False)
        b.update(2, True)
        b.update(4, False)
        b.update(6, True)

        self.assertEqual(get_numbers(a + b), ([0, 2, 1, 1, 0, 0, 1, 0, 0, 0], [1, 3, 2, 1, 1, 0, 1, 0, 0, 0]))


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

        p5 = Patient(5, "m", d(1931, 1, 1), d(datetime.MAXYEAR, 12, 31))
        p123 = Patient(123, "v", d(1999, 1, 1), d(2015, 1, 1))

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

        p5 = Patient(5, "m", d(1931, 1, 1), d(datetime.MAXYEAR, 12, 31))
        p123 = Patient(123, "v", d(1999, 1, 1), d(2015, 1, 1))

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
        second.with_medication = Counter([2])

        third = MedicationRate()
        third.total = Counter([2])
        third.with_medication = Counter([2])

        fourth = MedicationRate()
        fourth.total = Counter([2])
        fourth.with_medication = Counter([2])

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
        outcome = analyze_practitioners(self.patients, start, end, bin_months=bin_size, meds_start_with="B",
                                        spec=None, diag=None, plot=False)
        self.assertEqual(expected, outcome)


if __name__ == "__main__":
    main()
