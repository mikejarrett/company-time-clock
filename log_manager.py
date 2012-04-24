import sys
import pygtk
if not sys.platform == 'win32':
    pygtk.require('2.0')
import time, datetime
import calendar
from calendar import weekday, monthrange

class LogManager():
    def __init__(self):
        self.today = datetime.date.today()
        self.year = self.today.year
        self.first_day_of_period = self.first_day_of_pay_period()
        self.sundaylist = self.get_sunday_list(self.year)
        self.last_year_sunday_list = self.get_sunday_list(self.year - 1)
        
        self.ONE_WEEK_DELTA = datetime.timedelta(weeks=1)
        self.FILE_NAME = self.first_day_of_period.strftime("Time - %d-%b-%Y.txt")
        
        self.setup_log_file()
    
    def _get_today(self):
        return self.today
    
    def _get_year(self):
        return self.year
    
    def _get_first_day_of_period(self):
        return self.first_day_of_period
    
    def _get_sunday_list(self):
        return self.sundaylist
    
    def _get_last_year_sunday_list(self):
        return self.last_yuear_sunday_list
    
    def get_one_week_delta(self):
        return self.ONE_WEEK_DELTA
    
    def _get_file_name(self):
        return self.FILE_NAME
    
    def first_day_of_pay_period(self):
        '''Returns first day of pay period'''
        first_day_of_year = datetime.date(self.year,1,1) 
        first_day_of_pay_period_for_year = first_day_of_year - datetime.timedelta(first_day_of_year.weekday())
        if calendar.isleap(self.year):
            time_delta = datetime.timedelta(days = ((int(self.today.strftime("%W"))-1)*7)) 
        else:
            time_delta = datetime.timedelta(days = ((int(self.today.strftime("%W"))-1)*7) - 1)
        return first_day_of_year + time_delta 

    def get_sunday_list(self, year):
        '''Returns a list of every Sunday that starts a new pay period'''
        sundayList = []
        for month in xrange(1,13):
            sundayList1 = [sundayList.append('%d-%d-%d' % (year,month,day)) for day in xrange(1,1+monthrange(year,month)[1]) if weekday(year,month,day) == 6]
        return [sundayList[x] for x in xrange(0,len(sundayList),2)]   

    def setup_log_file(self):
        ##Determines the day and the week
        weeks = False
        if str(self.first_day_of_period) in self.sundaylist:
            try:
                self.punch_log_file = open(self.FILE_NAME, "a+r")
                for line in payDivide:
                    if line == "First Week:\n":
                        weeks = True
                        break 
                if weeks != True:
                    self.punch_log_file.writelines("First Week:\n")
                self.punch_log_file.close() 
            except IOError, e:
                self.punch_log_file = open(self.FILE_NAME, "a+r")
                self.punch_log_file.writelines("First Week:\n")
                self.punch_log_file.close()        

        elif str(self.first_day_of_period) not in self.sundaylist:
            self.first_day_of_period -= self.ONE_WEEK_DELTA
            try:
                self.punch_log_file = open(self.FILE_NAME, "a+r")
                for line in self.punch_log_file:
                    if line == "Second Week:\n":
                        weeks = True
                        break
                if not weeks:
                    self.punch_log_file.writelines("Second Week:\n")
                self.punch_log_file.close()
            except IOError, ioe:
                self.punch_log_file = open(self.FILE_NAME, "a+r")
                self.punch_log_file.writelines("Second Week:\n")
                self.punch_log_file.close()