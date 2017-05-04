from unittest import TestCase, main

from disease import Disease


class TestDisease(TestCase):
    no_description = Disease("TEST1", "000")
    with_description = Disease("TEST1", "000", description="Test 1")

    other_spec = Disease("TEST2", "000")
    other_diag = Disease("TEST1", "001")
    other_both = Disease("TEST2", "001")

    def test_repr(self):
        self.assertEqual(str(self.no_description), "(TEST1, 000)")
        self.assertEqual(str(self.with_description), "Test 1")

    def test_equality(self):
        self.assertEqual(self.no_description, self.with_description)
        self.assertNotEqual(self.no_description, self.other_spec)
        self.assertNotEqual(self.no_description, self.other_diag)
        self.assertNotEqual(self.no_description, self.other_both)

    def test_hash(self):
        self.assertEqual(hash(self.no_description), hash(self.with_description))
        self.assertNotEqual(hash(self.no_description), hash(self.other_spec))
        self.assertNotEqual(hash(self.no_description), hash(self.other_diag))
        self.assertNotEqual(hash(self.no_description), hash(self.other_both))


if __name__ == "__main__":
    main()
