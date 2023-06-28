from dataAnalysis.sun_food_customer_segmentation import  get_sun_food_file_importer, get_baby_segment_data, original_data_file

# 6 month advertising campaign
# 12 months purchasing baby items
# Is the cost of the advertising campaign worth it based on expected customer value?

# Advertising campaign assumptions
# Rates by month - assumes that we continue acquiring customers one month after campaign ends
BABY_CUSTOMER_ACQUISITION_RATES = [0.4, 0.5, 0.5, 0.6, 0.8, 0.8, 0.5]
# Assumes that after 12 months customers will no longer purchase baby items
BABY_CUSTOMER_ATTRITION_RATES = [0, 0.08, 0.08, 0.08, 0.04, 0.04, 0.04, 0.04, 0.02, 0.02, 0.02, 0.02]
BABY_CUSTOMER_SPEND_MONTHS = 12
BABY_CUSTOMER_AD_COST = 10000

"""
Marketing campaign example

Month | New customers | Lost customers | Total customers |
1     | 3             | 0              | 15              |
2     | 5             | 1              | 19              |
3     | 5             | 2              | 22              |
4     | 7             | 2              | 27              |
5     | 8             | 3              | 32              |
6     | 9             | 4              | 37              |
"""
def has_baby(record):
    '''Eveluates if a customer has a baby based on data in their customer record
    :param record: A customer record that you want to evalaute
    :return: bool
    '''
    return record['hasNewBaby']
def get_customers_and_spend(file_name, row_filter):
    '''This gets customer details and their purchase spend
    :param str file_name: name of the data file for which you want to analyze data
    :param func row_filter: Allows you to filter data at time of import, limits imported data to records that fit filter parameters
    :return: tuple
    '''
    file_importer = get_sun_food_file_importer(file_name,row_filter=row_filter)
    customers_with_baby = file_importer.data
    customer_spend = sum(customer['avgPurchaseAmount'] for customer in customers_with_baby)
    return customers_with_baby, customer_spend, file_importer

pre_promo_baby_customers, pre_promo_total_spend, file_importer = get_customers_and_spend(original_data_file, has_baby)
pre_promo_customer_keys = [customer['customerKey'] for customer in pre_promo_baby_customers]

def is_new_customer_promo(record):
    return record['hasNewBaby'] and record['customerKey'] not in pre_promo_customer_keys

check_in_customers, check_in_total_spend, _ = get_customers_and_spend('SunFoodShop_MarketingPromo_2021_Apr.csv',is_new_customer_promo)
def get_marketing_stats(base_customer_count,expected_monthly_spend):
    '''Get specific marketing stats for customers
    :param list base_customer_count:This is the count of customers each month
    :param list expected_monthly_spend: This is the expected spend by month
    :return:
    '''
    total_monthly_revenue = []
    total_monthly_customers = []
    for month_offset, customer_acq_rate in enumerate(BABY_CUSTOMER_ACQUISITION_RATES):
        new_customers = round(base_customer_count * customer_acq_rate)
        for month in range(BABY_CUSTOMER_SPEND_MONTHS):
            current_month = month_offset + month
            monthly_rev = new_customers * expected_monthly_spend
            try:
                total_monthly_revenue[current_month] += monthly_rev
            except IndexError:
                total_monthly_revenue.append(monthly_rev)

            attrition_rate = BABY_CUSTOMER_ATTRITION_RATES[month]
            new_customers = round(new_customers * (1 - attrition_rate))
            try:
                total_monthly_customers[current_month] += new_customers
            except IndexError:
                total_monthly_customers.append(new_customers)

    return (total_monthly_revenue, total_monthly_customers)

total_monthly_baby_rev, total_monthly_baby_customers = get_marketing_stats(len(pre_promo_baby_customers),(pre_promo_total_spend/len(pre_promo_baby_customers)))
roi_headers = ['metric'] + [f'Month {idx + 1}' for idx in range(len(total_monthly_baby_rev))] + ['Total']
roi_data = []
for metric_name, metric_values in (('Revenue',total_monthly_baby_rev), ('New Customers',total_monthly_baby_customers)):
    roi_data.append([metric_name] + metric_values + [sum(metric_values)])

roi_data.append([])
roi_data.append([])
roi_data.append(['Market Promo Cost', 'Total Revenue', 'ROI (nominal)', 'ROI (pct)'])
expected_total_rev = sum(total_monthly_baby_rev)
nom_roi = expected_total_rev - BABY_CUSTOMER_AD_COST
roi_data.append([BABY_CUSTOMER_AD_COST, expected_total_rev, nom_roi, (nom_roi/BABY_CUSTOMER_AD_COST) * 100])


actuals_headers = ['metric','actual','expected','diff']
actuals_data = []

actuals_data.append(['customers', len(check_in_customers), total_monthly_baby_customers[3], len(check_in_customers) - total_monthly_baby_customers[3]])
actuals_data.append(['revenue', check_in_total_spend, total_monthly_baby_rev[3], check_in_total_spend - total_monthly_baby_rev[3]])
sheets_config = [
    {'data': roi_data, 'headers': roi_headers, 'title': 'marketing_baby_roi'},
    {'data': actuals_data, 'headers': actuals_headers, 'title': 'month_4 _check_in'}
]
file_importer.write_excel_file('sun_food_marketing_roi', sheets_config=sheets_config)
print('Finished')







