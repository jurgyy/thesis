from datetime import date as d
from unittest import TestCase, main

from diagnosis import Diagnosis
from disease import Disease


class TestDiagnosisInequalityOperators(TestCase):
    disease_TE1_000 = Disease("TE1", "000", description="Test Disease 1")
    disease_TE1_000_no_description = Disease("TE1", "000")
    disease_TE1_000_other_description = Disease("TE1", "000", description="Test Other Description")

    disease_TE2_001 = Disease("TE2", "001", description="Test Disease 3")

    diagnosis_TE1_000 = Diagnosis(disease_TE1_000, d(2010, 1, 1), d(2011, 1, 1))
    diagnosis_TE1_000_no_description = Diagnosis(disease_TE1_000_no_description, d(2010, 1, 1), d(2011, 1, 1))
    diagnosis_TE1_000_other_description = Diagnosis(disease_TE1_000_other_description, d(2010, 1, 1), d(2011, 1, 1))

    diagnosis_TE2_001 = Diagnosis(disease_TE2_001, d(2010, 1, 1), d(2011, 1, 1))
    diagnosis_TE1_000_half_duration = Diagnosis(disease_TE1_000, d(2010, 3, 1), d(2010, 9, 1))
    diagnosis_TE1_000_later = Diagnosis(disease_TE1_000, d(2011, 1, 1), d(2012, 1, 1))

    def test_lt(self):
        self.assertLess(self.diagnosis_TE1_000, self.diagnosis_TE1_000_half_duration)
        self.assertLess(self.diagnosis_TE2_001, self.diagnosis_TE1_000_half_duration)

        self.assertLess(self.diagnosis_TE1_000, self.diagnosis_TE1_000_later)

    def test_gt(self):
        self.assertGreater(self.diagnosis_TE1_000_half_duration, self.diagnosis_TE1_000)
        self.assertGreater(self.diagnosis_TE1_000_half_duration, self.diagnosis_TE2_001)

        self.assertGreater(self.diagnosis_TE1_000_later, self.diagnosis_TE1_000)

    def test_eq(self):
        self.assertEqual(self.diagnosis_TE1_000, self.diagnosis_TE1_000_no_description)
        self.assertEqual(self.diagnosis_TE1_000, self.diagnosis_TE1_000_other_description)
        self.assertEqual(self.diagnosis_TE1_000_no_description, self.diagnosis_TE1_000_other_description)

        self.assertNotEqual(self.diagnosis_TE1_000, self.diagnosis_TE1_000_half_duration)
        self.assertNotEqual(self.diagnosis_TE1_000, self.diagnosis_TE1_000_later)
        self.assertNotEqual(self.diagnosis_TE1_000, self.diagnosis_TE2_001)


if __name__ == "__main__":
    main()
