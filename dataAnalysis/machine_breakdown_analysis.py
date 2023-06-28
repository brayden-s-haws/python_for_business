'''
This was used to analyze the frequency and impact of different machines breaking down in a car manufacturing facility
'''

from datetime import date, timedelta

from dataAnalysis import get_date_time_diff
from importer import *
from importer.file_import import FileImporter


default_data_types = {
    'machine_id': int,
    'event_date_time': safe_date_time_parse
}

default_headers = {
    'machineId': 'machine_id',
    'machineType': 'machine_type',
    'eventDescription': 'event_description',
    'eventDateTime': 'event_date_time'
}

file_importer = FileImporter(f'{DATA_FILE_PATH}MachineBreakdownData_20201216_20201229.csv',default_data_types=default_data_types,default_headers=default_headers)
file_importer.print_rows(5)

# Group data by event description to determine unique event types (by looking at the unique keys in the grouped data)
event_description_groups = file_importer.get_group_data([('event_description',)])
# Filter out data with no eventDescription
filtered_events = [record for record in file_importer.data if record['event_description']]
# Sort data by eventDateTime (asc)
filtered_events.sort(key=lambda record: record['event_date_time'])

event_keys = {
    'Machine broke': 'broke_date_time',
    'Mechanic started repairing machine': 'mechanic_repairing_date_time',
    'Machine is fixed': 'fixed_date_time'
}

event_records_by_machine = {}
for record in filtered_events:
    machine_id = record['machine_id']
    event_key = event_keys[record['event_description']]
    new_event_record = {'machine_id': machine_id, 'machine_type': record['machine_type'],
                        event_key: record['event_date_time']}
    if machine_id not in event_records_by_machine:
        event_records_by_machine[machine_id] = [new_event_record]
    elif event_key in event_records_by_machine[machine_id][-1]:
        event_records_by_machine[machine_id].append(new_event_record)
    else:
        event_records_by_machine[machine_id][-1][event_key] = record['event_date_time']

event_records = []
for records in event_records_by_machine.values():
    event_records.extend(records)


def good_event_record_check (event_record):
    '''This checks that all needed fields for a record are populated
    :param dict event_record:a dictionary with event details for a particular machine and event
    :return: bool
    '''
    for event_key in ('broke_date_time','mechanic_repairing_date_time','fixed_date_time'):
        if event_key not in event_record:
            print(f'Missing an event_key for {event_record}')
            return False
    if event_record['broke_date_time'] > event_record['mechanic_repairing_date_time'] or event_record[
        'mechanic_repairing_date_time'] > event_record['fixed_date_time']:
        print(f'Timestamps out of order for {event_record}')
        return False
    return True

event_records = list(filter(good_event_record_check, event_records))

for record in event_records:
    broke_dt = record['broke_date_time']
    mechanic_repairing_dt = record['mechanic_repairing_date_time']
    fixed_dt = record['fixed_date_time']
    record['broken_date'] = broke_dt.date()
    record['broken_to_mechanic_time_minutes'] = get_date_time_diff(mechanic_repairing_dt,broke_dt)
    record['mechanic_to_fixed_time_minutes'] = get_date_time_diff(fixed_dt,mechanic_repairing_dt)
    record['broke_to_fixed_time_minutes'] = get_date_time_diff(fixed_dt,broke_dt)

raw_data = file_importer.data
file_importer.data = event_records


machine_type_grouped_events_by_date = file_importer.get_group_data([('machine_type', 'broken_date')])[(
    'machine_type','broken_date')]

date_headers = [None] + [date(2020, 12, 16) + timedelta(days=days_index) for days_index in range(14)]
machine_types = {
    'Car door machine': [],
    'Car window machine': [],
    'Car body machine': [],
    'Car engine machine': [],
    'Car machine': [],
    'Paint machine': []
}
rows = ['broken_to_mechanic_time_minutes', 'mechanic_to_fixed_time_minutes', 'broke_to_fixed_time_minutes']

for machine_type, values in machine_types.items():
    for row in rows:
        new_record = [row]
        for date in date_headers[1:]:
            machine_type_date_values = machine_type_grouped_events_by_date.get((machine_type, date), None)
            if machine_type_date_values is None:
                new_record.append(None)
            else:
                sum_minutes = sum([value[row] for value in machine_type_date_values])
                new_record.append(sum_minutes)
        values.append(new_record)

sheets_config = [
    {'data': records, 'headers': date_headers, 'title': machine_type}
    for machine_type, records in machine_types.items()
    ]

file_importer.write_excel_file('machine_breakdown_analysis', sheets_config=sheets_config)
print('Finished')