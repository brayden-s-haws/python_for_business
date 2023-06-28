'''This is used to calculate a set of statistics for grouped data. Both at the record level and aggregated level'''
from copy import deepcopy
from datetime import datetime, date
from statistics import stdev

def string_group_and_key(grouping, group_key):
    """ Get a concatenated string of all pairs of grouping and groupKey variables
    :param tuple grouping: The names of the columns used for the grouping
    :param group_key: The values used in the grouping
    Example:
        grouping = ('hasNewBaby','educationLevel')
        group_key = (0, 'College')
        returns (string) = 'hasNewBaby: 0, educationLevel: College'
    """

    grouped_vals = []
    for group_name, group_val in zip(grouping, group_key):
        grouped_vals.append(f'{group_name}: {group_val}')
    return ', '.join(grouped_vals)


class GroupStatistics:

    #Aggregate level calculations
    MEAN = 'mean'
    PCT_UNIQUE = 'pct_unique'
    STD_DEV = 'std_deviation'

    # Record level calculations
    MAX = 'max'
    MIN = 'min'
    SUM = 'sum'
    COUNT = 'count'
    COUNT_NOT_NULL = 'count_not_null'
    COUNT_UNIQUE = 'count_unique'

    def __init__(self, group_data, headers=None):
        '''Class that allows you to run statistics on grouped data'''
        self.group_data = group_data if isinstance(group_data[0],dict) else {key: val for key, val in zip(headers, group_data)}
        self.set_starting_stats()

        for record in self.group_data:
            for column_key, value in record.items():
                self.calculate_record_stats(column_key, value)

        for stats in self.calculated_statistics.values():
            self.calculate_agg_stats(stats)

        for column_key, stats in self.calculated_statistics.items():
            if stats[self.MEAN]:
                column_data = [record[column_key]for record in self.group_data if record[column_key] is not None]
                stats[self.STD_DEV] = stdev(column_data)

    def set_starting_stats(self):
        '''Defines stats you wish to be able to run on grouped data'''
        stats_template_dict = {
            self.MEAN: None,
            self.PCT_UNIQUE: {},
            self.STD_DEV: None,
            self.MAX: None,
            self.MIN: None,
            self.SUM: None,
            self.COUNT: 0,
            self.COUNT_NOT_NULL: 0,
            self.COUNT_UNIQUE: {}
        }
        self.calculated_statistics = {}

        for column_key, value in self.group_data[0].items():
            self.calculated_statistics[column_key] = deepcopy(stats_template_dict)

    def calculate_record_stats(self, column_key, value):
        '''Calculates chose stats for grouped data at the record level'''
        stats = self.calculated_statistics[column_key]
        self.calculate_count(stats)
        self.calculate_count_not_null(stats, value)
        self.calculate_count_unique(stats,value)
        self.calculate_sum(stats,value)
        self.calculate_min(stats, value)
        self.calculate_max(stats, value)

    def calculate_agg_stats(self, stats):
        '''Calculates chose stats for grouped data at the aggregate level'''
        self.calculate_mean(stats)
        self.calculate_pct_unique(stats)

    def calculate_count(self, stats):
        stats[self.COUNT] += 1

    def calculate_count_not_null(self,stats,value):
        if value is not None:
            stats[self.COUNT_NOT_NULL] += 1

    def calculate_count_unique(self,stats,value):
        unique_items = stats[self.COUNT_UNIQUE]
        if value in unique_items:
            unique_items[value] += 1
        else:
            unique_items[value] = 1

    def calculate_sum(self, stats, value):
        if isinstance(value, (int, float)):
            if stats[self.SUM] is None:
                stats[self.SUM] = value
            else:
                stats[self.SUM] += value

    def calculate_min(self, stats, value):
        if isinstance(value, (int, float, date, datetime)):
            if stats[self.MIN] is None:
                stats[self.MIN] = value
            elif value < stats[self.MIN]:
                stats[self.MIN] = value

    def calculate_max(self, stats, value):
        if isinstance(value, (int, float, date, datetime)):
            if stats[self.MAX] is None:
                stats[self.MAX] = value
            elif value > stats[self.MAX]:
                stats[self.MAX] = value

    def calculate_mean(self, stats):
        try:
            if stats[self.SUM] is not None:
                stats[self.MEAN] = stats[self.SUM] / stats[self.COUNT_NOT_NULL]
        except ZeroDivisionError:
            pass

    def calculate_pct_unique(self,stats):
       for unique_val, count in stats[self.COUNT_UNIQUE].items():
            stats[self.PCT_UNIQUE][unique_val] = (count / stats[self.COUNT]) * 100