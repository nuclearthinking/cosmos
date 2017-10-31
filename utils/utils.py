import datetime


def _round_publication_date(date: datetime.datetime):
    if date.minute > 30:
        return date + datetime.timedelta(minutes=60 - date.minute) - datetime.timedelta(seconds=date.second)
    if date.minute < 30:
        return date + datetime.timedelta(minutes=30 - date.minute) - datetime.timedelta(seconds=date.second)
