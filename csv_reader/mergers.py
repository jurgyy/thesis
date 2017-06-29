import copy


def merge_data(a, b):
    merger = copy.deepcopy(a)

    for key, value in b.items():
        if key in merger:
            raise NotImplementedError

        merger[key] = value

    return merger
