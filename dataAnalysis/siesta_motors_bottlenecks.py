'''
This was used to analyze where there were bottlenecks in a car production facility
'''

from dataAnalysis import get_date_time_diff, TIME_AGG_MINUTES
from importer import *
from importer.file_import import FileImporter
from importer.group_statistics import GroupStatistics


default_data_types = {
    'partId': int,
    'machineId': int,
    'processingStartTime': safe_date_time_parse,
    'processingEndTime': safe_date_time_parse,
    'inputPartId': int,
    'inputPartReadyTime': safe_date_time_parse
}

default_headers = {
    7: 'inputPartName',
    8: 'inputPartReadyTime'
}

file_importer = FileImporter(f'{DATA_FILE_PATH}CarProcessingData_20201216_20201229.csv', default_headers=default_headers ,default_data_types=default_data_types)


new_data_headers = ['partId', 'partName', 'machineId', 'machineType', 'processingStartTime', 'processingEndTime']

aggregated_car_data = {}
for record in file_importer.data:
    new_record = aggregated_car_data.get(record['partId'], None)
    if not new_record:
        new_record = {header: record[header] for header in new_data_headers}
        new_record['processing_minutes'] = get_date_time_diff(record['processingEndTime'], record['processingStartTime'])
        new_record['processing_start_date'] = record['processingStartTime'].date()
        new_record['input_part_ids'] = []
        new_record['ready_processing_start_time'] = None
        if record['inputPartId']:
            new_record['input_part_ids'].append(record['inputPartId'])
            new_record['ready_processing_start_time'] = record['inputPartReadyTime']
        aggregated_car_data[record['partId']] = new_record
    else:
        if record['inputPartId']:
            new_record['input_part_ids'].append(record['inputPartId'])
            if record['inputPartReadyTime'] > new_record['ready_processing_start_time']:
                new_record['ready_processing_start_time'] = record['inputPartReadyTime']

for record in aggregated_car_data.values():
    record['wait_time_minutes'] = get_date_time_diff(record['processingStartTime'],record['ready_processing_start_time'])
    record['input_part_ids'] = tuple(record['input_part_ids'])

file_importer.data = list(aggregated_car_data.values())
car_part_data_groups = file_importer.get_group_data([('partName', 'processing_start_date')])['partName', 'processing_start_date']

car_part_date_groups = {group_key: GroupStatistics(group) for group_key, group in car_part_data_groups.items()}

headers = ['partName', 'processingStartDate', 'processingTimeMin', 'processingTimeMax', 'processingTimeAvg',
           'processingTimeStdDev', 'waitTimeMin', 'waitTimeMax', 'waitTimeAvg', 'waitTimeStdDev']

car_part_date_output_data = []
for group_key, group_stats in car_part_date_groups.items():
    new_record = []
    new_record.append(group_key[0])
    new_record.append(group_key[1])

    stats = group_stats.calculated_statistics
    processing_time_stats = stats['processing_minutes']
    wait_time_stats = stats['wait_time_minutes']
    for time_stats in (processing_time_stats, wait_time_stats):
        for metric in (group_stats.MIN, group_stats.MAX, group_stats.MEAN, group_stats.STD_DEV,):
            new_record.append(time_stats[metric])

    car_part_date_output_data.append(new_record)

def is_part_in_process(record):
    '''This evaluates if a part is in process
    :param dict record: a dictionary with processing details for a particular part
    :return: bool or datetime
    '''
    if not record['processingStartTime'] or not record['processingEndTime']:
        return False
    target_date_time = record['processingStartTime'].replace(hour=23, minute=0, second=0, microsecond=0)
    return record['processingStartTime'] <= target_date_time and record['processingEndTime'] >= target_date_time

machine_data_groups = file_importer.get_group_data([('machineId', 'machineType', 'processing_start_date')], filter_fn=is_part_in_process)[('machineId', 'machineType', 'processing_start_date')]
parts_processing_headers = ['machine_name', 'date', 'parts_in_process']
parts_in_process_records = []
for group_key, parts_list in machine_data_groups.items():
    new_record = []
    new_record.append(f'{group_key[1]} ({group_key[0]})')
    new_record.append(group_key[2])
    new_record.append(len(parts_list))
    parts_in_process_records.append(new_record)


sheets_config = [
    {'data': car_part_date_output_data, 'headers': headers, 'title': 'car_part_analysis'},
    {'data': parts_in_process_records, 'headers': parts_processing_headers, 'title': 'machine_throughput_analysis'},
]
file_importer.write_excel_file('siesta_motors_bottlenecks_analysis', sheets_config=sheets_config)
print('Finished')