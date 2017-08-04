from dateutil.relativedelta import relativedelta


def chads_vasc(patient, timestamp, max_value=2):
    return patient.calculate_chads_vasc(timestamp) >= max_value


def future_stroke(patient, timestamp, months=12):
    for s in patient.strokes:
        # "timestamp < s" because "<=" would mean strokes are predicting itself
        if timestamp < s <= timestamp + relativedelta(months=+months):
            return True
    return False
