from datetime import date as d
from unittest import TestCase, main

from diagnosis import Diagnosis
from main import *
from patient import Patient
from disease import Disease


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


if __name__ == '__main__':
    main()
