'''
This was used to evaluate the effects of seasonality on the sales of a winter clothing company
'''

from dataAnalysis import get_date_agg, DATE_AGG_QUARTERS, DATE_AGG_MONTHS
from importer import *
from importer.file_import import FileImporter
from importer.group_statistics import GroupStatistics


default_data_types = {
    'purchase_date_time': safe_date_time_parse,
    'quantity': int,
    'unit_price': float,
    'unit_cost': float,
    'discount_pct': float

}

default_headers = {
    'purchaseDateTime': 'purchase_date_time',
    'customerKey': 'customer_key',
    'productName': 'product_name',
    'unitPrice': 'unit_price',
    'unitCost': 'unit_cost',
    'discountPct': 'discount_pct'
}

file_importer = FileImporter(f'{DATA_FILE_PATH}SalesData_HighArcticWool_2020.csv',
                             default_data_types=default_data_types,default_headers=default_headers,row_limit=1000)
file_importer.print_rows(5)


processed_data = file_importer.data
for record in processed_data:
    unit_discount_price = record['unit_price'] * (1 - record['discount_pct'])
    record['unit_discount_price'] = unit_discount_price
    record['unit_profit'] = unit_discount_price - record['unit_cost']
    record['total_price'] = unit_discount_price * record['quantity']
    record['total_profit'] = record['unit_profit'] * record['quantity']

purchase_date_group = file_importer.get_group_data([(('purchase_date_time',get_date_agg),'product_name')],data=processed_data,is_flat=True)

get_month = lambda record: get_date_agg(record, date_agg=DATE_AGG_MONTHS)
get_quarter = lambda record: get_date_agg(record, date_agg=DATE_AGG_QUARTERS)
purchase_month_group = file_importer.get_group_data([(('purchase_date_time', get_month), 'product_name')], data=processed_data,is_flat=True)
purchase_quarter_group = file_importer.get_group_data([(('purchase_date_time', get_quarter), 'product_name')], data=processed_data, is_flat=True)


seasonality_group_statistics = {
    'date': {group_key: GroupStatistics(group) for group_key, group in purchase_date_group[0].items()},
    'month': {group_key: GroupStatistics(group) for group_key, group in purchase_month_group[0].items()},
    'quarter': {group_key: GroupStatistics(group) for group_key, group in purchase_quarter_group[0].items()}
}
metrics = ['total_price', 'total_profit', 'quantity']
product_lines = ['Mountain socks', 'Storm surge jacket', 'Aspen long sleeve shirt', 'Pine short sleeve shirt']
headers = ['date_category'] + metrics
seasonality_product_groups = {(product, seasonality_group): [] for product in product_lines for seasonality_group in seasonality_group_statistics}


for (product, seasonality_group), records in seasonality_product_groups.items():
    group_statistics = seasonality_group_statistics[seasonality_group]
    for (date_agg, product_item), statistics in group_statistics.items():
        if product == product_item:
            new_record = [date_agg]
            calculated_stats = statistics.calculated_statistics
            for metric in metrics:
                new_record.append(calculated_stats[metric]['sum'])
            records.append(new_record)

sheets_config = [
    {'data': records, 'headers': headers, 'title': f'{product}-{seasonality_group}'}
    for (product,seasonality_group), records in seasonality_product_groups.items()
    ]

file_importer.write_excel_file('product_seasonality_analysis', sheets_config=sheets_config)


