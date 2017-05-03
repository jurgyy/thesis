class ConfusionMatrix:
    def __init__(self, true, predict, name=None):
        if len(true) != len(predict):
            raise Exception("Data/Target length mismatch")

        self.true = true
        self.predict = predict
        self.name = name

        # TODO: Fix bug if any == 0
        self.t_p, self.f_n, self.f_p, self.t_n = self.calculate_matrix()
        self.basic = (self.t_p, self.f_n, self.f_p, self.t_n)

        self.population = self.t_p + self.f_n + self.f_p + self.t_n
        self.accuracy = (self.t_p + self.t_n) / self.population
        self.prevalence = (self.t_p + self.f_n) / self.population

        self.ppv = self.t_p / (self.t_p + self. f_p)
        self.fdr = self.f_p / (self.t_p + self. f_p)
        self.for_ = self.f_n / (self.t_n + self. f_n)
        self.npv = self.t_n / (self.t_n + self. f_n)

        self.tpr = self.t_p / (self.t_p + self.f_n)
        self.fnr = self.f_n / (self.t_p + self.f_n)
        self.fpr = self.f_p / (self.f_p + self.t_n)
        self.tnr = self.t_n / (self.f_p + self.t_n)

        self.plr = self.tpr / self.fpr
        self.nlr = self.fnr / self.tnr

        self.dor = self.plr / self.nlr

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
        print("True Positive:             {}".format(self.f_p))
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
