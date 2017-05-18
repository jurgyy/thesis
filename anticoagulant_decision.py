from dateutil.relativedelta import relativedelta


def chads_vasc(patient, timestamp, max_value=3):
    return patient.calculate_chads_vasc(timestamp) >= max_value


def event_based(patient, timestamp, max_value=3):
    if len(patient.chads_vasc_changes) == 0:
        return False

    tmp = patient.chads_vasc_changes[0]
    for e in patient.chads_vasc_changes:
        if e.date > timestamp:
            break

        tmp = e

    return tmp.score >= max_value


def future_stroke(patient, timestamp, months=12):
    for s in patient.strokes:
        # "timestamp < s" because "<=" would mean strokes are predicting itself
        if timestamp < s <= timestamp + relativedelta(months=+months):
            return True
    return False
