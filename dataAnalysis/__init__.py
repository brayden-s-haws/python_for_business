from datetime import datetime, date

TIME_AGG_SECONDS = 'seconds'
TIME_AGG_MINUTES = 'minutes'
TIME_AGG_HOURS = 'hours'
TIME_AGG_DAYS = 'days'

DATE_AGG_DAYS = 'days'
DATE_AGG_MONTHS = 'months'
DATE_AGG_QUARTERS = 'quarters'


def get_age_group(age, age_group_increment=10,age_limit=80):
    '''Takes an age value and groups it into buckets that are determined by the arguments of the function
    :param int age: the age value that you want to categorize
    :param int age_group_increment: this defines the increment between age groups
    :param int age_limit: this is the maximum age that an age value can be grouped into
    :return: str
    '''
    starting_age=0
    if age is None:
        return None
    while starting_age < age_limit:
        ending_age = starting_age + age_group_increment
        if age >= starting_age and age < ending_age:
            return f'{starting_age}-{ending_age}'
        starting_age = ending_age

    return f'{age_limit}+'


def get_date_agg(dt_value, date_agg=DATE_AGG_DAYS):
    '''Takes a date value and aggregates it based on the chosen aggregation method
    :param date dt_value: this is the date value that you want to aggregate
    :param str date_agg: this is the type of aggregation you want to preform: months, quarters, etc.
    :return:date or str
    '''
    if not isinstance(dt_value, (datetime, date)):
        return None
    if date_agg == DATE_AGG_DAYS:
        if isinstance(dt_value, datetime):
            return dt_value.date()
        return dt_value
    if date_agg == DATE_AGG_MONTHS:
        return dt_value.month
    if date_agg == DATE_AGG_QUARTERS:
        month = dt_value.month
        if month < 4:
            return 'Q1'
        if month < 7:
            return 'Q2'
        if month < 10:
            return 'Q3'
        return 'Q4'
    raise ValueError(f'Unsupported dateAgg: {date_agg}')


def get_date_time_diff(end_date_time,start_date_time, time_agg=TIME_AGG_MINUTES):
    '''Takes two date values and calculates the chosen aggregate value between them
    :param datetime end_date_time: this is the end date for the calculation
    :param datetime start_date_time: this is the start date for the calculation
    :param str time_agg: this is the type of aggregation you want to preform: minutes, days, etc.
    :return:int
    '''
    if not end_date_time or not start_date_time:
        return None

    try:
        date_time_diff = end_date_time - start_date_time
    except TypeError:
        print('Error')
    diff_seconds = round(date_time_diff.total_seconds())
    if time_agg == TIME_AGG_SECONDS:
        return diff_seconds
    if time_agg == TIME_AGG_MINUTES:
        return round(diff_seconds / 60)
    if time_agg == TIME_AGG_HOURS:
        return round(diff_seconds / 60 / 60)
    if time_agg == TIME_AGG_DAYS:
        return round(diff_seconds / 60 / 60 /24)

