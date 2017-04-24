class Disease:
    def __init__(self, spec, diag):
        self.spec = spec
        self.diag = diag

    def __repr__(self):
        return "({}, {})".format(self.spec, self.diag)

    def __eq__(self, other):
        return self.spec == other.spec and self.diag == other.diag

    def __hash__(self):
        return hash(self.spec) + hash(self.diag)
