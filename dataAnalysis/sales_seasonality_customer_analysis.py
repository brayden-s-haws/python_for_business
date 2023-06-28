'''
This was used to understand the purchase patterns and sales amounts of customers based on different categorical groupings
'''

from dataAnalysis import get_age_group
from importer.group_statistics import GroupStatistics
from importer import *
from importer.file_import import FileImporter

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

customer_default_headers = {
    'educationLevel': 'education_level',
    'customerKey': 'customer_key'
}

file_importer = FileImporter(f'{DATA_FILE_PATH}SalesData_HighArcticWool_2020.csv', default_data_types=default_data_types,default_headers=default_headers)
sales_data = file_importer.data
customer_data = FileImporter(f'{DATA_FILE_PATH}CustomerData_HighArcticWool_2020.csv', default_data_types={'age': int},default_headers=customer_default_headers).data
customer_data = {record['customer_key']: record for record in customer_data}

for sale in sales_data:
    customer = customer_data.get(sale['customer_key'], None)
    if not customer:
        raise ValueError('Customer does not exist')
    sale['age'] = customer['age']
    unit_discount_price = sale['unit_price'] * (1 - sale['discount_pct'])
    sale['unit_discount_price'] = unit_discount_price
    sale['unit_profit'] = unit_discount_price - sale['unit_cost']
    sale['total_price'] = unit_discount_price * sale['quantity']
    sale['total_profit'] = sale['unit_profit'] * sale['quantity']

age_group_sales_data = file_importer.get_group_data([(('age',get_age_group),)],data=sales_data,is_flat=True)

age_group_sales_statistics = {group_key: GroupStatistics(group) for group_key, group in age_group_sales_data[0].items()}


headers = ['age_group', 'total_profit', 'avg_profit']
records = []
for (age_group,),group_stats in age_group_sales_statistics.items():
    new_record = [age_group]
    new_record.append(group_stats.calculated_statistics['total_profit'][GroupStatistics.SUM])
    new_record.append(group_stats.calculated_statistics['total_profit'][GroupStatistics.MEAN])
    records.append(new_record)

sheets_config = [
    {'data': records, 'headers': headers, 'title': 'CustomerAgeGroupAnalysis'}
    ]

file_importer.write_excel_file('customer_age_group_analysis', sheets_config=sheets_config)


print('Finished')

