class Diagnosis:
    def __init__(self, disease, start_date, end_date, practitioner=None):
        self.disease = disease
        self.start_date = start_date
        self.end_date = end_date
        self.practitioner = practitioner

    def __repr__(self):
        if self.practitioner:
            return "{} {}~{} (by {})".format(self.disease, self.start_date, self.end_date, self.practitioner)
        return "{} {}~{}".format(self.disease, self.start_date, self.end_date)

    def __lt__(self, other):
        return self.start_date < other.start_date

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def dump(self):
        print(self.disease.spec)
        print(self.disease.diag)
        print(self.disease.description)
        print(self.start_date)
        print(self.end_date)
        if self.practitioner:
            print(self.practitioner)
