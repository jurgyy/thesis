from unittest import TestCase, main

from learning.confusion_matrix import ConfusionMatrix


class TestConfusionMatrix(TestCase):
    true = [0, 0, 0, 1, 1, 1, 1, 1, 1, 1]
    pred = [0, 1, 1, 1, 1, 1, 0, 0, 0, 0]
    cf = ConfusionMatrix(true, pred)

    def test_basic_values(self):
        t_p = f_n = f_p = t_n = 0
        for i in range(len(self.true)):
            if self.true[i] == self.pred[i] == 1:
                t_p += 1
            elif self.true[i] == self.pred[i] == 0:
                t_n += 1
            elif self.true[i] == 1 and self.pred[i] == 0:
                f_n += 1
            else:
                f_p += 1
        self.assertEqual((self.cf.t_p, self.cf.f_n, self.cf.f_p, self.cf.t_n), (t_p, f_n, f_p, t_n))

        matrix = self.cf.matrix
        self.assertEqual(matrix, (t_p, f_n, f_p, t_n))

    def test_population(self):
        self.assertEqual(self.cf.population, len(self.true))

    def test_accuracy(self):
        total = 0
        for i in range(len(self.true)):
            if self.true[i] == self.pred[i]:
                total += 1
        self.assertEqual(self.cf.accuracy, total/self.cf.population)

    def test_prevalence(self):
        total = 0
        for i in range(len(self.true)):
            if self.true[i] == 1:
                total += 1
        self.assertEqual(self.cf.prevalence, total/self.cf.population)


if __name__ == "__main__":
    main()
