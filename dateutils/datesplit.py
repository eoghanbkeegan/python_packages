# -*- coding: utf-8 -*-
"""
Created on Tue Jun 11 21:39:25 2019

@author: eoghan keegan, 36379, strategic insights
"""

import calendar
import datetime
import itertools

class DateTimeSplit:
    """
    class for splitting dates into a given range for queries against databases to avoid spool issues
    """

    def __init__(self, start, end):
        """
        initialize datetime split class with start and end date

        :param str start the date from which to start the range
        :param str end the date from which to end the range
        """

        fmts = ['{0}'.format(a)+join+'{0}'.format(b)+join+'{0}'.format(c) for a, b, c in [(x, y, z) for x, y, z in list(itertools.permutations(['%d', '%m', '%y'])) + list(itertools.permutations(['%d', '%m', '%Y']))] for join in ['-', '/', '.', ' ', '', ]]

        fmts = fmts + ['1'+fmt for fmt in fmts]

        if start is None or end is None:
            raise ValueError('start and end must not be None')
        else:
            for fmt in fmts:
                try:
                    start_dt = datetime.datetime.strptime(start, '{0}'.format(fmt))
                    end_dt = datetime.datetime.strptime(end, '{0}'.format(fmt))
                    self.start_dt = start_dt
                    self.end_dt = end_dt
                    self.fmt = fmt
                except Exception as e:
                    if 'day is out of range for month' in str(e):
                        raise ValueError(e)
                    else:
                        pass
        
        self.start = start
        self.end = end
        self.date_fmt = '%Y-%m-%d'
        
    def get_quarter(self, date, prev=False):
        """
        get quarter of date

        :param datetime date the date from which to extract the quarter
        :param boolean prev whether to return the previous quarter default(False)
        """

        quarters = [(4, -1), (1, 0), (2, 0), (3, 0), (4, 0)]

        if prev:
            add = 0
        else:
            add = 1

        quarter, year_diff = (quarters[((date.month - 1) // 3) + add])

        return (date.year + year_diff, quarter)
    
    def split_dates_into_range(self, start, end, split, delta, fmt):
        """
        split two dates into a given range. the range can be monthly, quarterly or defined by an integer division

        :param datetime start the date from which to start the range
        :param datetime end the date from which to end the range
        :param str/int split the split in which to divide the dates
        :param delta the delta between the start and end dates
        :param str fmt the format of the given dates
        """
        
        date_dict = dict()
        
        if split == 'monthly':
            
            last_date = datetime.datetime(start.year, start.month, calendar.monthrange(start.year, start.month)[1])
            date_dict = {datetime.datetime.strftime(start, fmt): datetime.datetime.strftime(last_date, fmt)}
            
            while end >= last_date:
                next_start = last_date + datetime.timedelta(days=1)
                last_date = datetime.datetime(next_start.year, next_start.month, calendar.monthrange(next_start.year, next_start.month)[1])
                if next_start < end:
                    next_dict = {datetime.datetime.strftime(next_start, fmt):datetime.datetime.strftime(last_date, fmt)}
                    date_dict = {**date_dict, **next_dict}
            
            date_dict[list(date_dict.keys())[-1]] = datetime.datetime.strftime(end, fmt)
            self.date_dict = date_dict

        elif split == 'quarterly':
            
            end_months = [3, 6, 9, 12]
            quarter = self.get_quarter(start)[1] - 1
            
            last_date = datetime.datetime(start.year, end_months[quarter], calendar.monthrange(start.year, end_months[quarter])[1])
            date_dict = {datetime.datetime.strftime(start, fmt): datetime.datetime.strftime(last_date, fmt)}
            
            while end >= last_date:
                next_start = last_date + datetime.timedelta(days=1)
                quarter = self.get_quarter(next_start)[1] - 1
                last_date = datetime.datetime(next_start.year, end_months[quarter], calendar.monthrange(next_start.year, end_months[quarter])[1])
                if next_start < end:
                    next_dict = {datetime.datetime.strftime(next_start, fmt):datetime.datetime.strftime(last_date, fmt)}
                    date_dict = {**date_dict, **next_dict}
            
            date_dict[list(date_dict.keys())[-1]] = datetime.datetime.strftime(end, fmt)
            self.date_dict = date_dict

        else:

            last_date = start + delta
            date_dict = {datetime.datetime.strftime(start, fmt): datetime.datetime.strftime(last_date, fmt)}

            while end >= last_date:
                next_start = last_date + datetime.timedelta(days=1)
                last_date = next_start + delta
                if next_start < end:
                    next_dict = {datetime.datetime.strftime(next_start, fmt):datetime.datetime.strftime(last_date, fmt)}
                    date_dict = {**date_dict, **next_dict}
                    
            date_dict[list(date_dict.keys())[-1]] = datetime.datetime.strftime(end, fmt)
            self.date_dict = date_dict
        
        return self.date_dict

    def split_dates(self, split):
        """
        define split in which to split dates

        :param str/int split the split in which to divide the dates 
        """
        
        self.delta = self.end_dt - self.start_dt
        
        if split is None:
            raise ValueError(type(split) + ' is not a supported split criteria')
        elif split in ['monthly', 'quarterly']:
            self.split = split
            self.split_dates_into_range(self.start_dt, self.end_dt, self.split, self.delta, self.date_fmt)
        elif isinstance(split, int):
            self.split = split
            self.delta = self.delta / split
            self.split_dates_into_range(self.start_dt, self.end_dt, self.split, self.delta, self.date_fmt)
        else:
            raise ValueError(str(split) + ' is not a supported split criteria')
        
        return self.date_dict