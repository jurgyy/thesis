import datetime
from datetime import date as d
from unittest import TestCase, main

from csv_reader.diagnose_csv import get_diagnoses
from csv_reader.medication_csv import get_medications
from csv_reader.patients_csv import get_patients
from medication import Medication
from patient import Patient
from diagnosis import Diagnosis
from disease import Disease


class TestCsvReaders(TestCase):
    patients = get_patients("test_data/test_patients.csv")
    diagnoses = get_diagnoses("test_data/test_diagnoses.csv")
    medications = get_medications("test_data/test_meds.csv")

    def test_get_patients(self):
        self.assertEqual(self.patients[5], Patient(5, "m", d(1931, 2, 3), d(datetime.MAXYEAR, 12, 31)))
        self.assertEqual(self.patients[123], Patient(123, "v", d(1999, 10, 11), d(2015, 1, 1)))
        self.assertEqual(self.patients, {
            5: Patient(5, "m", d(1931, 2, 3), d(datetime.MAXYEAR, 12, 31)),
            123: Patient(123, "v", d(1999, 10, 11), d(2015, 1, 1))
        })

    def test_get_diagnoses(self):
        disease_TE1_000 = Disease("TE1", "000", description="Test Disease 1")
        disease_TE1_001 = Disease("TE1", "001", description="Test Disease 2")
        disease_TE2_001 = Disease("TE2", "001", description="Test Disease 3")
        disease_TE3_001 = Disease("TE3", "001", description="Test Disease 4")

        self.assertEqual(self.diagnoses, {
            5: [Diagnosis(disease_TE1_000, d(2010, 1, 1), d(2010, 10, 31), "John Deer"),
                Diagnosis(disease_TE1_000, d(2010, 11, 1), d(2010, 12, 31), "Jane Doe"),
                Diagnosis(disease_TE1_001, d(2010, 5, 1), d(2010, 6, 1), "John Deer"),
                Diagnosis(disease_TE2_001, d(2010, 6, 2), d(2012, 6, 2), "John Deer"),
                Diagnosis(disease_TE3_001, d(2010, 3, 18), d(2010, 4, 19), "John Deer")],
            123: [Diagnosis(disease_TE1_000, d(2010, 1, 1), d(2010, 1, 31), "John Deer"),
                  Diagnosis(disease_TE2_001, d(2011, 6, 3), d(2012, 6, 2), "John Deer")]
        })

    def test_get_medications(self):
        self.assertEqual(self.medications, {5: [Medication("A00AA00", d(2010, 1, 1), d(datetime.MAXYEAR, 12, 31)),
                                                Medication("B00BB01", d(2010, 6, 1), d(2010, 6, 7)),
                                                Medication("B00BB02", d(2010, 7, 1), d(2010, 8, 1)),
                                                Medication("B00BB01", d(2010, 8, 1), d(2011, 8, 1)),
                                                Medication("A00AA04", d(2010, 10, 31), d(2010, 11, 21)),
                                                Medication("A00AA10", d(2010, 12, 31), d(datetime.MAXYEAR, 12, 31))],
                                            123: [Medication("A00AA00", d(2010, 1, 1), d(2011, 1, 1)),
                                                  Medication("B00BB02", d(2010, 6, 16), d(2010, 7, 16))]})


if __name__ == "__main__":
    main()
