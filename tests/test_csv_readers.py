from datetime import date as d
from unittest import TestCase, main

from csv_reader.diagnose_csv import *
from csv_reader.patients_csv import *
from patient import Patient
from diagnosis import Diagnosis
from disease import Disease


class TestCsvReaders(TestCase):
    patients = get_patients("test_data/test_patients.csv")
    diagnoses = get_diagnoses("test_data/test_diagnoses.csv")

    def test_get_patients(self):
        self.assertEqual(self.patients[5], Patient(5, "m", d(1931, 2, 3), d(datetime.MAXYEAR, 12, 31)))
        self.assertEqual(self.patients[123], Patient(123, "v", d(1999, 10, 11), d(2005, 1, 1)))
        self.assertEqual(self.patients, {
            5: Patient(5, "m", d(1931, 2, 3), d(datetime.MAXYEAR, 12, 31)),
            123: Patient(123, "v", d(1999, 10, 11), d(2005, 1, 1))
        })

    def test_get_diagnoses(self):
        disease_TE1_000 = Disease("TE1", "000", description="Test Disease 1")
        disease_TE1_001 = Disease("TE1", "001", description="Test Disease 2")
        disease_TE2_001 = Disease("TE2", "001", description="Test Disease 3")
        disease_TE3_001 = Disease("TE3", "001", description="Test Disease 4")

        self.assertEqual(self.diagnoses, {
            5: [Diagnosis(disease_TE1_000, d(2010, 1, 1), d(2010, 8, 6)),
                Diagnosis(disease_TE1_001, d(2010, 5, 1), d(2010, 6, 1)),
                Diagnosis(disease_TE2_001, d(2010, 6, 2), d(2012, 6, 2)),
                Diagnosis(disease_TE3_001, d(2010, 3, 18), d(2010, 4, 19))],
            123: [Diagnosis(disease_TE1_000, d(2010, 1, 1), d(2010, 1, 31)),
                  Diagnosis(disease_TE2_001, d(2011, 6, 3), d(2012, 6, 2))]
        })


if __name__ == "__main__":
    main()
