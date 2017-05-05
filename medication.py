class Medication:
    def __init__(self, code, start_date, end_date):
        self.code = code
        self.start_date = start_date
        self.end_date = end_date

    def __repr__(self):
        return "{} {}~{}".format(self.code, self.start_date, self.end_date)

    def __lt__(self, other):
        return self.start_date < other.start_date

    def __eq__(self, other):
        return self.__dict__ == other.__dict__
