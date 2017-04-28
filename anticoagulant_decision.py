from dateutil.relativedelta import relativedelta


def chads_vasc(patient, timestamp, max_value):
    if patient.calculate_chads_vasc(timestamp) >= 3:
        return True
    return False


def event_based(patient, timestamp):
    if len(patient.chads_vasc_changes) == 0:
        return False

    tmp = patient.chads_vasc_changes[0]
    for e in patient.chads_vasc_changes:
        if e.date > timestamp:
            break

        tmp = e

    return tmp.score >= 3


def future_stroke(patient, timestamp, months=6):
    for s in patient.strokes:
        if s <= timestamp <= s + relativedelta(months=+6):
            return True
    return False