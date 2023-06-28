'''
This was used to analyze shopping patterns and sales amounts of different customer segments
'''

from importer import *
from importer.file_import import FileImporter
from importer.group_statistics import GroupStatistics, string_group_and_key
from dataAnalysis import get_age_group

original_data_file = 'SunFoodShop_customers.csv'

def get_sun_food_file_importer(file_name, row_filter=None):
    ''' This imports data from files related to the Sun Food Shop
    :param str file_name: The name of the file you want to process
    :param func row_filter: Allows you to filter data at time of import, limits imported data to records that fit filter parameters
    :return: dict
    '''
    default_data_types = {
        'isMarried': int,
        'isEmployed': int,
        'hasNewBaby': int,
        'age': int,
        'annualIncome': float,
        'childrenNum': int,
        'avgPurchaseAmount': float
    }

    return FileImporter(f'{DATA_FILE_PATH}{file_name}',default_data_types = default_data_types,row_filter=row_filter)

file_importer = get_sun_food_file_importer(original_data_file)

def get_baby_segment_data(file_importer):
    '''This imports data for customers who have babies
    :param func file_importer: imports data based on parameters passed into argument of function
    :return: dict
    '''
    grouped_data = file_importer.get_group_data([('hasNewBaby',),])

    has_new_baby_segments = grouped_data[('hasNewBaby',)]
    baby_segments_stats = {group_key: GroupStatistics(group) for group_key, group in has_new_baby_segments.items()}
    analyzed_data = []

    for group_key, group_stats in baby_segments_stats.items():
        stats = group_stats.calculated_statistics
        new_record = []
        new_record.append(group_key[0])
        new_record.append((stats['customerKey'][group_stats.COUNT] / len(file_importer.data)) * 100)
        new_record.append(stats['customerKey'][group_stats.COUNT])
        new_record.append(round(stats['avgPurchaseAmount'][group_stats.MEAN],2))
        new_record.append(round(stats['avgPurchaseAmount'][group_stats.MAX],2))
        new_record.append(round(stats['avgPurchaseAmount'][group_stats.MIN],2))
        new_record.append(stats['isEmployed'][group_stats.MEAN] * 100)
        new_record.append(round(stats['age'][group_stats.MEAN],2))
        new_record.append(round(stats['annualIncome'][group_stats.MEAN],2))
        analyzed_data.append(new_record)

    return analyzed_data

baby_analysis_data = get_baby_segment_data(file_importer)

grouped_data = file_importer.get_group_data([
    ('hasNewBaby',),
    ('educationLevel', 'isMarried'),
    ('sex', 'isMarried'),
    ('educationLevel',),
    ('sex', ('age', get_age_group))
])

grouped_segment_stats = {}
for grouped_data_key, grouped_segments in grouped_data.items():
        grouped_segment_stats[grouped_data_key] = {group_key: GroupStatistics(group) for group_key, group in grouped_segments.items()}

segmentation_headers = ['group', 'customerCount', 'avgPurchasePrice']
segmentation_analysis_data = []

for grouped_data_key, segment_stats in grouped_segment_stats.items():
    for group_key, group_stats in segment_stats.items():
        new_record = []
        stats = group_stats.calculated_statistics
        new_record.append(string_group_and_key(grouped_data_key, group_key))
        new_record.append(stats['customerKey'][group_stats.COUNT])
        new_record.append(round(stats['avgPurchaseAmount'][group_stats.MEAN],2))
        segmentation_analysis_data.append(new_record)

headers = ['has_new_baby', 'group_pct', 'count', 'avg_purchase_price', 'max_purchase_price', 'min_purchase_price', 'pct_employed', 'avg_age', 'avg_annual_income']

sheets_config = [
    {'data': baby_analysis_data, 'headers': headers, 'title': 'baby_analysis'},
    {'data': segmentation_analysis_data, 'headers': segmentation_headers, 'title': 'segmentation_analysis'},
    {'title': 'raw_data'}
]
file_importer.write_excel_file('sun_food_segments_analysis', sheets_config=sheets_config)
print('Finished')