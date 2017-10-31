import datetime


def _round_publication_date(date: datetime.datetime):
    minutes = date.minute
    if minutes > 30:
        return date + datetime.timedelta(minutes=minutes + (60 - minutes))
    if minutes < 30:
        return date + datetime.timedelta(minutes=minutes + (30 - minutes))
