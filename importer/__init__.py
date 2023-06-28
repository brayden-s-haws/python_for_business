'''
This contains global variables and functions that can be used in the File Importer
'''
from datetime import datetime
from dateutil.parser import parse
DATA_FILE_PATH = r'/Users/haws/Documents/Projects/Code/PycharmProjects/pythonForBusiness/dataFiles/'
DATA_FILE_OUTPUT_PATH = r'/Users/haws/Documents/Projects/Code/PycharmProjects/pythonForBusiness/outputFiles/'

ROW_TYPE_DICT = 'dict'
ROW_TYPE_LIST = 'list'
ROW_TYPE_TUPLE = 'tuple'

FILE_TYPE_CSV = 'csv'
FILE_TYPE_XLS = 'xls'

DEFAULT_NONE_STRINGS = ('null', 'na', 'n/a')

# parses dates into a datetime
def safe_date_time_parse(val):
    '''This evaluates a value to determine if it is a datetime and if note it parses it to a datetime
    :param datetime,str val: The datetime or value you wish to evaluate
    :return: datetime
    '''
    if isinstance(val, datetime):
        return val
    else:
        parsed_val = parse(val)
        #print(f'Parsed "{val}" into {parsed_val}')
        return parsed_val

# removes % from a string and returns the value as a float
def percent_string_to_float(val):
    '''This converts strings with a % to a float
    :param str val: The string you want to cast to a float
    :return: float
    '''
    return float(val.replace("%",''))

# extracts part of a string and returns it as an integer
def string_extract_values_to_int(val):
    '''This extracts values from a string and casts to an int
    :param str val: The string you want to cast to an int
    :return: int
    '''
    try:
        return int(val[0:4])
    except ValueError:
        print(val)

# removes commas from a string and replaces them with a blank
def parse_integer_string(val):
    '''Parses a string to an integer
    :param str val: The string you want to cast to an integer
    :return: int
    '''
    return int(val.replace(',', ''))
