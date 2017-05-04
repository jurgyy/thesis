import datetime


def convert_to_date(datetime_string):
    if isinstance(datetime_string, datetime.date):
        return datetime_string

    if datetime_string != datetime_string or datetime_string == 'NULL':
        return datetime.date(datetime.MAXYEAR, 12, 31)

    return datetime.datetime.strptime(datetime_string, '%Y-%m-%d %H:%M:%S.%f').date()
