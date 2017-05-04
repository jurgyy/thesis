import numpy as np


class ConfusionMatrix:
    def __init__(self, true, predict, name=None):
        if len(true) != len(predict):
            raise Exception("Data/Target length mismatch")

        self.true = true
        self.predict = predict
        self.name = name

        self.t_p, self.f_n, self.f_p, self.t_n = self.calculate_matrix()
        self.matrix = (self.t_p, self.f_n, self.f_p, self.t_n)

        # Division by zero now returns inf
        with np.errstate(divide='ignore', invalid='ignore'):
            self.population = self.t_p + self.f_n + self.f_p + self.t_n
            self.accuracy = np.divide(self.t_p + self.t_n, self.population)
            self.prevalence = np.divide(self.t_p + self.f_n, self.population)

            self.ppv = np.divide(self.t_p, (self.t_p + self.f_p))
            self.fdr = np.divide(self.f_p, (self.t_p + self.f_p))
            self.for_ = np.divide(self.f_n, (self.t_n + self.f_n))
            self.npv = np.divide(self.t_n, (self.t_n + self.f_n))

            self.tpr = np.divide(self.t_p, (self.t_p + self.f_n))
            self.fnr = np.divide(self.f_n, (self.t_p + self.f_n))
            self.fpr = np.divide(self.f_p, (self.f_p + self.t_n))
            self.tnr = np.divide(self.t_n, (self.f_p + self.t_n))

            self.plr = np.divide(self.tpr, self.fpr)
            self.nlr = np.divide(self.fnr, self.tnr)

            self.dor = np.divide(self.plr, self.nlr)

    def calculate_matrix(self):
        t_p = f_n = f_p = t_n = 0
        for i in range(len(self.true)):
            t = self.true[i]
            p = self.predict[i]
            if t == p == 1:
                t_p += 1
            elif t == p == 0:
                t_n += 1
            elif t == 1 and p == 0:
                f_n += 1
            else:
                f_p += 1

        return t_p, f_n, f_p, t_n

    def dump(self):
        if self.name:
            print(self.name)
        print("Population Size:           {}".format(self.population))
        print("")
        print("True Positive:             {}".format(self.t_p))
        print("False Negative:            {}".format(self.f_n))
        print("False Positive:            {}".format(self.f_p))
        print("True Negative:             {}".format(self.t_n))
        print("")
        print("Accuracy:                  {}".format(self.accuracy))
        print("Prevalence:                {}".format(self.prevalence))
        print("")
        print("Positive Predictive Value: {}".format(self.ppv))
        print("Negative Predictive Value: {}".format(self.npv))
        print("False Omission Rate:       {}".format(self.for_))
        print("False Discovery Rate:      {}".format(self.fdr))
        print("")
        print("True Positive Rate:        {}".format(self.tpr))
        print("False Negative Rate:       {}".format(self.fnr))
        print("False Positive Rate        {}".format(self.fpr))
        print("True Negative Rate:        {}".format(self.tnr))
        print("")
        print("Positive Likelihood Ratio: {}".format(self.plr))
        print("Negative Likelihood Ratio: {}".format(self.nlr))
        print("")
        print("Diagnostic Odds Ratio:     {}".format(self.dor))
        print("")
