'''
This was used to evaluate the change in stock amounts over a series of yeard
'''

from importer import *
from importer.file_import import FileImporter

default_headers = {
    'Marketing year1': 'Marketing_Start_Year',
    'Beginning stocks2': 'Beginning_Stocks',
    'Ending stocks': 'Ending_Stocks',
    7: 'Total2'
}

default_data_types = {
    'Marketing_Start_Year': string_extract_values_to_int,
    'Beginning_Stocks': parse_integer_string,
    'Production': parse_integer_string,
    'Imports': parse_integer_string,
    'Total': parse_integer_string,
    'Domestic': parse_integer_string,
    'Exports': parse_integer_string,
    'Total2': parse_integer_string,
    'Ending_Stocks': parse_integer_string
}

file_importer = FileImporter(f'{DATA_FILE_PATH}BiodieselDataChallenge.csv', default_headers=default_headers, default_data_types=default_data_types, row_data_type=ROW_TYPE_DICT,row_limit=18)
file_importer.print_rows(5)
file_importer.write_csv_file('biodiesel_processed')



