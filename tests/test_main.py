import datetime
from datetime import date as d
from unittest import TestCase, main

from main import add_diseases, add_medications, get_all_diseases, get_disease_frequency, reduce_feature_space
from diagnosis import Diagnosis
from medication import Medication
from patient import Patient
from disease import Disease
from simulations import get_random_subset


class TestMainFunctions(TestCase):
    patients = {2: Patient(2, 'm', d(1990, 1, 1), d(datetime.MAXYEAR, 12, 31)),
                5: Patient(5, 'm', d(1980, 2, 5), d(datetime.MAXYEAR, 12, 31)),
                7: Patient(7, 'v', d(1970, 3, 9), d(2006, 12, 31)),
                9: Patient(9, 'v', d(1960, 4, 11), d(2012, 12, 31))
                }

    diseases = [Disease("TEST", "1"), Disease("TEST", "2")]

    diagnoses = {2: [Diagnosis(Disease("TEST", "1"), d(2005, 1, 1), d(2005, 12, 31))],
                 5: [Diagnosis(Disease("TEST", "1"), d(2005, 1, 1), d(2005, 12, 31)),
                     Diagnosis(Disease("TEST", "1"), d(2006, 1, 1), d(2006, 12, 31))],
                 7: [Diagnosis(Disease("TEST", "1"), d(2005, 1, 1), d(2005, 6, 30)),
                     Diagnosis(Disease("TEST", "1"), d(2006, 1, 1), d(2006, 12, 31))],
                 9: [Diagnosis(Disease("TEST", "1"), d(2005, 1, 1), d(2005, 12, 31)),
                     Diagnosis(Disease("TEST", "2"), d(2006, 1, 1), d(2006, 12, 31))]
                 }

    medications = {2: [Medication("A00AA00", d(2004, 3, 1), d(2005, 3, 1)),
                       Medication("A00AA00", d(2005, 3, 2), d(2006, 3, 3))],
                   5: [Medication("A00AA00", d(2005, 3, 1), d(2005, 6, 1)),
                       Medication("A00AA00", d(2006, 1, 1), d(2006, 3, 1))],
                   7: [Medication("A00AA00", d(2005, 1, 1), d(2005, 3, 1)),
                       Medication("B99BB99", d(2006, 1, 1), d(2006, 3, 1))],
                   9: [Medication("A00AA00", d(2005, 1, 2), d(2006, 1, 1))]
                   }

    def test_add_diseases(self):
        add_diseases(self.patients, self.diagnoses)
        self.assertEqual(self.patients[2].diagnoses,
                         {Disease("TEST", "1"): [Diagnosis(Disease("TEST", "1"), d(2005, 1, 1), d(2005, 12, 31))]})
        self.assertEqual(self.patients[5].diagnoses,
                         {Disease("TEST", "1"): [Diagnosis(Disease("TEST", "1"), d(2005, 1, 1), d(2005, 12, 31)),
                                                 Diagnosis(Disease("TEST", "1"), d(2006, 1, 1), d(2006, 12, 31))]})
        self.assertEqual(self.patients[7].diagnoses,
                         {Disease("TEST", "1"): [Diagnosis(Disease("TEST", "1"), d(2005, 1, 1), d(2005, 6, 30)),
                                                 Diagnosis(Disease("TEST", "1"), d(2006, 1, 1), d(2006, 12, 31))]})
        self.assertEqual(self.patients[9].diagnoses,
                         {Disease("TEST", "1"): [Diagnosis(Disease("TEST", "1"), d(2005, 1, 1), d(2005, 12, 31))],
                          Disease("TEST", "2"): [Diagnosis(Disease("TEST", "2"), d(2006, 1, 1), d(2006, 12, 31))]})

    def test_get_all_diseases(self):
        self.assertEqual(get_all_diseases(self.diagnoses), set(self.diseases))

    def test_get_disease_frequency(self):
        self.assertEqual(get_disease_frequency(self.diseases, self.diagnoses),
                         {Disease("TEST", "1"): 6, Disease("TEST", "2"): 1})

    def test_reduce_feature_space(self):
        self.assertEqual(reduce_feature_space(self.diseases, self.diagnoses, 3), {Disease("TEST", "1")})

    def test_get_random_subset(self):
        subset = get_random_subset(self.patients, 0.5)
        self.assertEqual(len(subset), 2)
        for s in subset:
            self.assertTrue(s in self.patients)

    def test_add_medication(self):
        add_medications(self.patients, self.medications)
        self.assertEqual(self.patients[2].medications,
                         {"A00AA00": [Medication("A00AA00", d(2004, 3, 1), d(2005, 3, 1)),
                                      Medication("A00AA00", d(2005, 3, 2), d(2006, 3, 3))]})
        self.assertEqual(self.patients[5].medications,
                         {"A00AA00": [Medication("A00AA00", d(2005, 3, 1), d(2005, 6, 1)),
                                      Medication("A00AA00", d(2006, 1, 1), d(2006, 3, 1))]})
        self.assertEqual(self.patients[7].medications,
                         {"A00AA00": [Medication("A00AA00", d(2005, 1, 1), d(2005, 3, 1))],
                          "B99BB99": [Medication("B99BB99", d(2006, 1, 1), d(2006, 3, 1))]})
        self.assertEqual(self.patients[9].medications,
                         {"A00AA00": [Medication("A00AA00", d(2005, 1, 2), d(2006, 1, 1))]})


if __name__ == "__main__":
    main()
