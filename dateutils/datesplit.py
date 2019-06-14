# -*- coding: utf-8 -*-
"""
Created on Fri Jun 14 19:41:27 2019

@author: eoghan keegan, 36379
"""

import pandas
import datetime
import calendar
import dateutil

class DateTimeSplit:
    """
    split two dates into a dictionary of start and end dates with the start 
    dates being the keys and the end dates being the values.
    """
    
    def __init__(self, start, end, split=1):
        """
        initialise the class
        
        :param *str* start the start date of the range
        :param *str* end the end date of the range
        :param *str* or *int* split the division into which to split the dates
        can be one of 'monthly', 'quarterly' or integer (default=1)
        """
        
        self.start = start
        self.end = end
        self.split = split
        self.start_dt = dateutil.parser.parse(start)
        self.end_dt = dateutil.parser.parse(end)
        self.fmt = '%Y-%m-%d'
        self.delta = self.end_dt - self.start_dt
        self.dates = self.__split_dates_into_range()
        
    def __split_dates_into_range(self):
        """
        split two dates into a dictionary of start and end dates either monthly
        or quarterly or into n equal divisions
        """
        
        _dates = dict()
        
        if self.split == 'monthly':
            
            _month_end = calendar.monthrange(self.start_dt.year, self.start_dt.month)[1]
            _next_end = datetime.datetime(self.start_dt.year, self.start_dt.month, _month_end)
            _next_start = _next_end + datetime.timedelta(days=1)
            _dates[self.start] = datetime.datetime.strftime(_next_end, self.fmt)
                        
            while _next_end < self.end_dt:
                _next_start = _next_end + datetime.timedelta(days=1)
                _month_end = calendar.monthrange(_next_start.year, _next_start.month)[1]
                _next_end = datetime.datetime(_next_start.year, _next_start.month, _month_end)
                _dates[datetime.datetime.strftime(_next_start, self.fmt)] = datetime.datetime.strftime(_next_end, self.fmt)
            
            _dates[datetime.datetime.strftime(_next_start, self.fmt)] = self.end
            
        elif self.split == 'quarterly':
            
            _quarter_ends = [3, 6, 9, 12]
            _quarter = pandas.Timestamp(self.start_dt).quarter
            _month = _quarter_ends[_quarter - 1]
            _month_end = calendar.monthrange(self.start_dt.year, _month)[1]
            _next_end = datetime.datetime(self.start_dt.year, _month, _month_end)
            _dates[self.start] = datetime.datetime.strftime(_next_end, self.fmt)
                        
            while _next_end < self.end_dt:
                _next_start = _next_end + datetime.timedelta(days=1)
                _quarter = pandas.Timestamp(_next_start).quarter
                _month = _quarter_ends[_quarter - 1]
                _month_end = calendar.monthrange(_next_start.year, _month)[1]
                _next_end = datetime.datetime(_next_start.year, _month, _month_end)
                _dates[datetime.datetime.strftime(_next_start, self.fmt)] = datetime.datetime.strftime(_next_end, self.fmt)
            
            _dates[datetime.datetime.strftime(_next_start, self.fmt)] = self.end
                        
        elif isinstance(self.split, int):
            
            _delta = self.delta / self.split
            _next_end = self.start_dt + _delta
            _dates[self.start] = datetime.datetime.strftime(_next_end, self.fmt)
            
            while _next_end < self.end_dt:
                _next_start = _next_end + datetime.timedelta(days=1)
                _next_end = _next_start + _delta
                _dates[datetime.datetime.strftime(_next_start, self.fmt)] = datetime.datetime.strftime(_next_end, self.fmt)
            
            _dates[datetime.datetime.strftime(_next_start, self.fmt)] = self.end
            
        else:
            raise ValueError(str(self.split)+' is an unsupported split criteria')
        
        return _dates