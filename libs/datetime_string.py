import datetime

def to_datetime(datetime_string):
    """Convert datetime string to object"""
    counter = 0
    first_slicing_index = 0
    dt_list = []
    datetime_object = None
    for letter in datetime_string:
        if letter in ['-', ' ', ':']:
            dt_list.append(int(datetime_string[first_slicing_index : counter]))
            first_slicing_index = counter + 1
        elif (counter + 1) == len(datetime_string):
            dt_list.append(int(datetime_string[first_slicing_index : counter + 1]))
            first_slicing_index = counter + 1
        counter += 1
    datetime_object = datetime.datetime(*dt_list)
    return datetime_object

def to_seconds(time_string):
    """Convert time string to seconds"""
    return to_timedelta(time_string).total_seconds()

def to_minutes(time_string):
    """Convert datetime string to minutes"""
    return round(to_timedelta(time_string).total_seconds() / 60, 0)

def to_hours(time_string):
    """Convert datetime string to hours"""
    return round(to_timedelta(time_string).total_seconds() / 3600, 0)

def dec_by_sec(datetime_string):
    """Decrement datetime string"""
    datetime_object = to_datetime(datetime_string)
    decrement = datetime.timedelta(seconds = 1)
    new_datetime = str(datetime_object - decrement)
    return new_datetime

def inc_by_sec(datetime_string):
    """Incremenet datetime string"""
    datetime_object = to_datetime(datetime_string)
    increment = datetime.timedelta(seconds = 1)
    new_datetime = str(datetime_object + increment)
    return new_datetime

def to_time(time_string):
    """Convert time string to object"""
    counter = 0
    first_slicing_index = 0
    dt_list = []
    time_object = None
    for letter in time_string:
        if letter in [':']:
            dt_list.append(int(time_string[first_slicing_index : counter]))
            first_slicing_index = counter + 1
        elif (counter + 1) == len(time_string):
            dt_list.append(int(time_string[first_slicing_index : counter + 1]))
            first_slicing_index = counter + 1
        counter += 1
    time_object = datetime.time(dt_list[0], dt_list[1], dt_list[2])
    return time_object

def to_timedelta(time_string):
    """Convert time string to timedelta object"""
    counter = 0
    first_slicing_index = 0
    dt_list = []
    timedelta = None
    for letter in time_string:
        if letter in [':']:
            dt_list.append(int(time_string[first_slicing_index : counter]))
            first_slicing_index = counter + 1
        elif (counter + 1) == len(time_string):
            dt_list.append(int(time_string[first_slicing_index : counter + 1]))
            first_slicing_index = counter + 1
        counter += 1
    timedelta = datetime.timedelta(hours=dt_list[0], minutes=dt_list[1], seconds=dt_list[2])
    return timedelta

def timedelta_to_time_string(timedelta):
    """Convert timedelta to time string"""
    time_object = (datetime.datetime.min + timedelta).time()
    return str(time_object)

def seconds_to_timedelta(seconds):
    '''Convert seconds (int or float) into timedelta object'''
    timedelta_object = datetime.timedelta(seconds=seconds)
    return timedelta_object

def subtract(first, second):
    """Return difference as a datetime string"""
    first_datetime = to_datetime(first)
    second_datetime = to_datetime(second)
    subtraction_result = str(first_datetime - second_datetime)
    return subtraction_result

def add(first, second):
    """Return sum as a datetime string"""
    first = to_datetime(first)
    second = to_datetime(second)
    return first + second

def compare(greater, lesser):
    """Return True if first is greater, False if not"""
    greater_datetime = to_datetime(greater)
    lesser_datetime = to_datetime(lesser)
    return greater_datetime > lesser_datetime


