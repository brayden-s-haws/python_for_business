'''
This was used to analyze demograohic information for a given population
'''
from importer import *
from importer.file_import import FileImporter

default_headers = {
    0: 'Name',
    'Height (Inches)': 'Height_inches',
    'Marital status': 'Marital_status',
    'Height %': 'Height_percentile'
}

default_data_types = {
    'Age': int,
    'Height_inches': int,
    'Employment_date': safe_date_time_parse,
    'Height_percentile': percent_string_to_float
}

file_importer = FileImporter(f'{DATA_FILE_PATH}DemographicSampleMoreData.xlsx', default_headers=default_headers, default_data_types=default_data_types, row_data_type=ROW_TYPE_LIST)
file_importer.print_rows(5)
file_importer.write_excel_file(FILE_TYPE_XLS, 'demographic_processed')

