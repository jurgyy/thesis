from datetime import date as d
from unittest import TestCase, main

from anticoagulant_decision import chads_vasc, event_based, future_stroke
from diagnosis import Diagnosis
from disease_groups import *

from patient import Patient
from patient import ChadsVascChangeEvent as CVCE
from disease import Disease
from medication import Medication


class TestPatient(TestCase):
    patient = Patient(1, 'm', d(1970, 6, 6), d(2008, 10, 5))

    def test_calculate_age(self):
        self.assertEqual(self.patient.calculate_age(d(1980, 5, 5)), 9)
        self.assertEqual(self.patient.calculate_age(d(1980, 5, 6)), 9)
        self.assertEqual(self.patient.calculate_age(d(1980, 5, 7)), 9)
        self.assertEqual(self.patient.calculate_age(d(1980, 6, 5)), 9)
        self.assertEqual(self.patient.calculate_age(d(1980, 6, 6)), 10)
        self.assertEqual(self.patient.calculate_age(d(1980, 6, 7)), 10)
        self.assertEqual(self.patient.calculate_age(d(1980, 7, 5)), 10)
        self.assertEqual(self.patient.calculate_age(d(1980, 7, 6)), 10)
        self.assertEqual(self.patient.calculate_age(d(1980, 7, 7)), 10)

    def test_is_alive(self):
        self.assertFalse(self.patient.is_alive(d(1970, 6, 5)))
        self.assertTrue(self.patient.is_alive(d(1970, 6, 6)))
        self.assertTrue(self.patient.is_alive(d(2008, 10, 4)))
        self.assertFalse(self.patient.is_alive(d(2008, 10, 5)))

    def test_is_female(self):
        self.assertFalse(Patient(1, 'm', d(1970, 6, 6), d(2008, 10, 5)).is_female())
        self.assertTrue(Patient(1, 'v', d(1970, 6, 6), d(2008, 10, 5)).is_female())


class TestPatientDiseases(TestCase):
    patient = Patient(1, 'm', d(1970, 6, 6), d(2008, 10, 5))

    diagnoses = [Diagnosis(Disease("TEST", "1"), d(2005, 1, 1), d(2005, 12, 31)),
                 Diagnosis(Disease("TEST", "2"), d(2005, 6, 1), d(2006, 5, 31)),
                 Diagnosis(Disease("TEST", "1"), d(2006, 1, 1), d(2006, 12, 31))]

    def test_add_diagnosis(self):
        self.patient.add_diagnosis(self.diagnoses[0])
        self.patient.add_diagnosis(self.diagnoses[1])
        self.patient.add_diagnosis(self.diagnoses[2])

        self.assertEqual(len(self.patient.diagnoses[Disease("TEST", "1")]), 2)
        self.assertEqual(len(self.patient.diagnoses[Disease("TEST", "2")]), 1)

    def test_get_current_diseases(self):
        self.assertEqual(self.patient.get_current_diseases(d(2005, 1, 1)),
                         set(diagnosis.disease for diagnosis in self.diagnoses[0:1]))
        self.assertEqual(self.patient.get_current_diseases(d(2006, 1, 1)),
                         set(diagnosis.disease for diagnosis in self.diagnoses[1:3]))

    def test_has_disease(self):
        self.assertFalse(self.patient.has_disease(Disease("TEST", "1"), d(2004, 12, 31)))
        self.assertTrue(self.patient.has_disease(Disease("TEST", "1"), d(2005, 1, 1)))
        self.assertTrue(self.patient.has_disease(Disease("TEST", "1"), d(2006, 12, 31)))
        self.assertFalse(self.patient.has_disease(Disease("TEST", "1"), d(2007, 1, 1)))
        self.assertTrue(self.patient.has_disease(Disease("TEST", "1"), d(2007, 1, 1), chronic=True))

        self.assertFalse(self.patient.has_disease(Disease("TEST", "3"), d(2006, 7, 1)))

    def test_days_since_diagnosis(self):
        self.assertEqual(self.patient.days_since_diagnosis(Disease("TEST", "1"), d(2004, 1, 1)), 0)
        self.assertEqual(self.patient.days_since_diagnosis(Disease("TEST", "1"), d(2005, 1, 2)), 1)
        self.assertEqual(self.patient.days_since_diagnosis(Disease("TEST", "1"), d(2005, 2, 1)), 31)
        self.assertEqual(self.patient.days_since_diagnosis(Disease("TEST", "1"), d(2005, 12, 31)), 364)
        self.assertEqual(self.patient.days_since_diagnosis(Disease("TEST", "1"), d(2006, 1, 1)), 0)
        self.assertEqual(self.patient.days_since_diagnosis(Disease("TEST", "1"), d(2007, 2, 1)), 396)

    def test_days_since_last_diagnosis(self):
        self.assertEqual(self.patient.days_since_last_diagnosis(d(2006, 1, 1)), 0)
        self.assertEqual(self.patient.days_since_last_diagnosis(d(2006, 2, 1)), 31)
        self.assertEqual(self.patient.days_since_last_diagnosis(d(2005, 12, 31)), -1)
        self.assertEqual(self.patient.days_since_last_diagnosis(d(2007, 2, 1)), 396)


class TestChadsVasc(TestCase):
    patient_male = Patient(1, 'm', d(1930, 1, 1), d(2015, 12, 31))
    patient_female = Patient(1, 'v', d(1930, 1, 1), d(2015, 12, 31))

    diagnoses = [Diagnosis(Disease("TEST", "1"), d(1960, 1, 1), d(1960, 12, 31)),
                 Diagnosis(Disease("TEST", "2"), d(1961, 1, 1), d(1961, 12, 31)),
                 Diagnosis(chads_vasc_c[0], d(1962, 1, 1), d(1963, 12, 31)),
                 Diagnosis(chads_vasc_s[0], d(1963, 1, 1), d(1963, 12, 31)),
                 Diagnosis(Disease("TEST", "3"), d(1964, 1, 1), d(1964, 12, 31)),
                 Diagnosis(chads_vasc_h[0], d(1965, 1, 1), d(1965, 12, 31)),
                 Diagnosis(Disease("TEST", "1"), d(1966, 1, 1), d(1966, 12, 31)),
                 Diagnosis(Disease("TEST", "2"), d(1966, 1, 1), d(1966, 12, 31)),
                 Diagnosis(chads_vasc_c[0], d(1967, 1, 1), d(1967, 12, 31)),
                 Diagnosis(chads_vasc_v[0], d(1968, 1, 1), d(1968, 12, 31)),
                 Diagnosis(chads_vasc_s[0], d(1969, 1, 1), d(1969, 12, 31)),
                 Diagnosis(Disease("TEST", "4"), d(1970, 1, 1), d(1970, 12, 31)),
                 ]

    for diagnosis in diagnoses:
        patient_male.add_diagnosis(diagnosis)
        patient_female.add_diagnosis(diagnosis)

    patient_male.find_chads_vasc_changes()
    patient_female.find_chads_vasc_changes()

    patient_male.find_strokes()
    patient_female.find_strokes()

    def test_find_chads_vasc_changes(self):
        male_changes = self.patient_male.chads_vasc_changes
        female_changes = self.patient_female.chads_vasc_changes

        expected_male_changes = sorted([CVCE(self.patient_male.birth_date, 0),
                                        CVCE(d(1962, 1, 1), 1),
                                        CVCE(d(1963, 1, 1), 3),
                                        CVCE(d(1965, 1, 1), 4),
                                        CVCE(d(1967, 1, 1), 4),
                                        CVCE(d(1968, 1, 1), 5),
                                        CVCE(d(1969, 1, 1), 5),
                                        CVCE(d(1995, 1, 1), 6),
                                        CVCE(d(2005, 1, 1), 7)])

        expected_female_changes = sorted([CVCE(self.patient_female.birth_date, 1),
                                          CVCE(d(1962, 1, 1), 2),
                                          CVCE(d(1963, 1, 1), 4),
                                          CVCE(d(1965, 1, 1), 5),
                                          CVCE(d(1967, 1, 1), 5),
                                          CVCE(d(1968, 1, 1), 6),
                                          CVCE(d(1969, 1, 1), 6),
                                          CVCE(d(1995, 1, 1), 7),
                                          CVCE(d(2005, 1, 1), 8)])

        self.assertEqual(male_changes, expected_male_changes)
        self.assertEqual(female_changes, expected_female_changes)

    def test_find_strokes(self):
        expected_strokes = [d(1963, 1, 1), d(1969, 1, 1)]

        self.assertEqual(self.patient_male.strokes, expected_strokes)
        self.assertEqual(self.patient_female.strokes, expected_strokes)


class TestPatientMedication(TestCase):
    patient = Patient(1, 'm', d(1970, 6, 6), d(2016, 10, 5))

    medications = [Medication("A00AA00", d(2010, 1, 1), d(2010, 1, 1)),
                   Medication("B00BB01", d(2010, 6, 1), d(2010, 6, 7)),
                   Medication("B00BB01", d(2010, 8, 1), d(2010, 8, 7)),
                   Medication("B00BB02", d(2010, 7, 1), d(2010, 8, 1))]

    for m in medications:
        patient.add_medication(m)

    def test_add_medications(self):
        self.assertEqual(self.patient.medications,
                         {m.code: [n for n in self.medications if n.code is m.code] for m in self.medications})

    def test_has_medication(self):
        self.assertTrue(self.patient.has_medication("A00AA00", d(2010, 1, 1)))
        self.assertTrue(self.patient.has_medication("B00BB01", d(2010, 6, 3)))
        self.assertFalse(self.patient.has_medication("B00BB01", d(2010, 1, 1)))

    def test_has_medication_group(self):
        self.assertFalse(self.patient.has_medication_group("A0", d(2009, 12, 31)))
        self.assertTrue(self.patient.has_medication_group("A0", d(2010, 1, 1)))
        self.assertFalse(self.patient.has_medication_group("A0", d(2010, 1, 2)))

        self.assertFalse(self.patient.has_medication_group("A0", d(2009, 12, 31), which=True))
        self.assertEqual("A00AA00", self.patient.has_medication_group("A0", d(2010, 1, 1), which=True))
        self.assertEqual("B00BB01", self.patient.has_medication_group("B0", d(2010, 8, 3), which=True))


class TestPatientShouldHaveAC(TestCase):
    patient = Patient(1, 'm', d(1937, 5, 14), d(2017, 12, 31))

    diagnoses = [                                                    # Score | Disease
        Diagnosis(chads_vasc_c[0], d(1980, 1, 1), d(1980, 12, 31)),  # 1     | Congestive heart failure
        Diagnosis(chads_vasc_h[0], d(1985, 1, 1), d(1985, 12, 31)),  # 2     | Hypertension
        Diagnosis(chads_vasc_s[0], d(1990, 1, 1), d(1990, 12, 31)),  # 4     | Stroke
        Diagnosis(chads_vasc_c[0], d(1995, 1, 1), d(1995, 12, 31)),  # 4     | Congestive heart failure
        Diagnosis(chads_vasc_v[0], d(2000, 1, 1), d(2000, 12, 31)),  # 5     | Vascular Disease
        Diagnosis(chads_vasc_s[0], d(2005, 1, 1), d(2005, 12, 31)),  # 6     | Stroke & 65 >= age >= 75
    ]

    for diagnosis in diagnoses:
        patient.add_diagnosis(diagnosis)
    patient.find_chads_vasc_changes()
    patient.find_strokes()

    def test_method_chads_vasc(self):
        self.assertFalse(self.patient.should_have_AC(d(1980, 1, 1), chads_vasc, {"max_value": 3}))
        self.assertFalse(self.patient.should_have_AC(d(1985, 1, 1), chads_vasc, {"max_value": 3}))
        self.assertTrue(self.patient.should_have_AC(d(1990, 1, 1), chads_vasc, {"max_value": 3}))
        self.assertTrue(self.patient.should_have_AC(d(1995, 1, 1), chads_vasc, {"max_value": 3}))
        self.assertTrue(self.patient.should_have_AC(d(2000, 1, 1), chads_vasc, {"max_value": 3}))
        self.assertTrue(self.patient.should_have_AC(d(2005, 1, 1), chads_vasc, {"max_value": 3}))

    def test_method_event_based(self):
        self.assertFalse(self.patient.should_have_AC(d(1980, 1, 1), event_based, {"max_value": 3}))
        self.assertFalse(self.patient.should_have_AC(d(1985, 1, 1), event_based, {"max_value": 3}))
        self.assertTrue(self.patient.should_have_AC(d(1990, 1, 1), event_based, {"max_value": 3}))
        self.assertTrue(self.patient.should_have_AC(d(1995, 1, 1), event_based, {"max_value": 3}))
        self.assertTrue(self.patient.should_have_AC(d(2000, 1, 1), event_based, {"max_value": 3}))
        self.assertTrue(self.patient.should_have_AC(d(2005, 1, 1), event_based, {"max_value": 3}))

    def test_method_future_stroke(self):
        self.assertFalse(self.patient.should_have_AC(d(1980, 1, 1), future_stroke, {"months": 12}))
        self.assertFalse(self.patient.should_have_AC(d(1985, 1, 1), future_stroke, {"months": 12}))
        self.assertTrue(self.patient.should_have_AC(d(1989, 12, 31), future_stroke, {"months": 12}))
        self.assertFalse(self.patient.should_have_AC(d(1990, 1, 1), future_stroke, {"months": 12}))
        self.assertFalse(self.patient.should_have_AC(d(1995, 1, 1), future_stroke, {"months": 12}))
        self.assertFalse(self.patient.should_have_AC(d(2000, 1, 1), future_stroke, {"months": 12}))
        self.assertFalse(self.patient.should_have_AC(d(2003, 12, 31), future_stroke, {"months": 12}))
        self.assertTrue(self.patient.should_have_AC(d(2004, 1, 1), future_stroke, {"months": 12}))
        self.assertTrue(self.patient.should_have_AC(d(2004, 12, 31), future_stroke, {"months": 12}))
        self.assertFalse(self.patient.should_have_AC(d(2005, 1, 1), future_stroke, {"months": 12}))


class TestPatientCareRange(TestCase):
    diagnoses = [Diagnosis(Disease("TEST", "1"), d(2005, 1, 1), d(2005, 12, 31)),
                 Diagnosis(Disease("TEST", "2"), d(2005, 6, 1), d(2006, 5, 31)),
                 Diagnosis(Disease("TEST", "1"), d(2006, 1, 1), d(2006, 12, 31))]

    medications = [Medication("A00AA00", d(2010, 1, 1), d(2010, 1, 1)),
                   Medication("B00BB01", d(2010, 6, 1), d(2010, 6, 7)),
                   Medication("B00BB01", d(2010, 8, 1), d(2010, 8, 7)),
                   Medication("B00BB02", d(2010, 7, 1), d(2010, 8, 1))]

    def test_none(self):
        patient = Patient(1, 'm', d(1970, 6, 6), d(2016, 10, 5))
        self.assertRaises(ValueError, patient.set_care_range)

    def test_diagnoses(self):
        patient = Patient(1, 'm', d(1970, 6, 6), d(2016, 10, 5))
        for diagnosis in self.diagnoses:
            patient.add_diagnosis(diagnosis)

        patient.set_care_range(extra_months=12)
        self.assertEqual(patient.care_range, (d(2005, 1, 1), d(2007, 12, 31)))

    def test_medication(self):
        patient = Patient(1, 'm', d(1970, 6, 6), d(2016, 10, 5))
        for m in self.medications:
            patient.add_medication(m)

        patient.set_care_range(extra_months=6)
        self.assertEqual(patient.care_range, (d(2010, 1, 1), d(2011, 2, 7)))

    def test_combined(self):
        patient = Patient(1, 'm', d(1970, 6, 6), d(2016, 10, 5))
        for diagnosis in self.diagnoses:
            patient.add_diagnosis(diagnosis)
        for m in self.medications:
            patient.add_medication(m)

        patient.set_care_range()
        self.assertEqual(patient.care_range, (d(2005, 1, 1), d(2010, 8, 7)))


if __name__ == "__main__":
    main()
