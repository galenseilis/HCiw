'''Server schedules or factories of schedules.'''

# TODO: Remove holidays as days where service is given.
def server_schedule_from_date_range(start_date, end_date):
    dates = pd.date_range(start_date, end_date)
    idx = list(range(1,dates.size+1))
    is_weekday = (dates.weekday <= 4) * 1
    # Check which dates are weekdays
    return list(zip(is_weekday, idx))
