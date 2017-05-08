class Disease:
    def __init__(self, spec, diag, description=None):
        self.spec = spec
        self.diag = diag
        self.description = description

    def __repr__(self):
        if self.description:
            return self.description
        return "({}, {})".format(self.spec, self.diag)

    def __eq__(self, other):
        return self.spec == other.spec and self.diag == other.diag

    def __hash__(self):
        return hash((self.spec, self.diag))

    def dump(self):
        print(self.spec, self.diag, self.description)
