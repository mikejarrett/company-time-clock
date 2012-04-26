import sys
import pygtk
if not sys.platform == 'win32':
    pygtk.require('2.0')
import time, datetime
from datetime import timedelta
import calendar
from calendar import weekday, monthrange
import hashlib
import MySQLdb
import logging

logging.basicConfig(filename="errors.log",level=logging.ERROR)

class SQLConnection(object):
    def __init__(self):
        self.time_format = '%Y-%m-%d %H:%M:%S'
        try:
            self.conn = MySQLdb.connect('localhost', 'timeclock', 'platypus')
            self.cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)
            self.cursor.execute("USE timeclock")
        except Exception, error:
            logging.error(" %s - %s" % (datetime.datetime.now(), error))
    
    def refresh_user(self, username):
        query = "SELECT `id`, `username`, `active`, `admin` FROM users WHERE `username`='%s'" % (username)
        self.cursor.execute(query)
        return self.cursor.fetchone()

    def get_user(self, username, password):
        if username and password:
            query = "SELECT `id`, `username`, `active`, `admin` FROM users WHERE `username`='%s' AND `password`='%s'" % (username, password)
        else:
            query = "SELECT `id`, `username`, `active`, `admin` FROM users WHERE `username`='%s'" % (username)
        self.cursor.execute(query)
        results = self.cursor.fetchone()
        if results:
            user = User(id=results['id'], username=results['username'], active=results['active'], admin=results['admin'])
            return user
        else:
            return False
  
    def clock_in(self, user_id):
        query = "SELECT * FROM time_punches WHERE `user_id`=%s AND `time_in` IS NOT NULL AND `time_out` IS NULL" % user_id
        results = self.cursor.execute(query)
        results = self.cursor.fetchall()
        if len(results) >= 1:
            return "You have already clocked in. \nYour last punch in was at: {}".format("TODO")
        else:
            now = datetime.datetime.now()
            punch_in_str = now.strftime(self.time_format)            
            query = "INSERT INTO time_punches(user_id, time_in) VALUES(%s, '%s')" % (user_id, punch_in_str)
            results = self.cursor.execute(query)
            return "Clocked in successfully a: {}".format(punch_in_str)
            
    def clock_out(self, user_id):
        float_time = 0.0
        query = "SELECT * FROM time_punches WHERE `user_id`=%s AND `time_in` IS NOT NULL AND `time_out` IS NULL LIMIT 1" % user_id
        self.cursor.execute(query)
        results = self.cursor.fetchone()
        if results:
            time_in = results['time_in']
            time_out = datetime.datetime.now()
            difference = time_out - time_in
            if difference.days:
                float_time += float(difference.days * 24)
            if difference.seconds:
                float_time += float((difference.seconds / 60.0) / 60.0)
            time_out_str = time_out.strftime(self.time_format)
            query = "UPDATE time_punches SET time_out='%s', total=%2.2f WHERE id=%s" % (time_out_str, float_time, results['id'])
            self.cursor.execute(query)
            return "You have clocked out successfully at: {}".format(time_out_str)
        else:
            return "You have already clocked out. \nYour last clock out was at: {}".format("TODO")

    def get_punches_for_period(self, user_id, first_day, end_day):
        query = "SELECT * FROM time_punches WHERE `user_id`='%s' AND `time_in` IS NOT NULL AND `time_out` IS NOT NULL \
                AND `time_in` BETWEEN '%s' AND '%s'" % (user_id, first_day, end_day)
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def get_all_punches(self, user_id):
        query = "SELECT * FROM time_punches WHERE `user_id`=%s AND `time_in` IS NOT NULL AND `time_out` IS NOT NULL" % user_id
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def get_total_time(self, user_id, first_day, end_day):
        query = "SELECT * FROM time_punches WHERE `user_id`='%s' AND `time_in` IS NOT NULL AND `time_out` IS NOT NULL \
                AND `time_in` BETWEEN '%s' AND '%s'" % (user_id, first_day, end_day)
        result = self.cursor.execute(query)
        if result: 
            results = self.cursor.fetchall()
            return sum([row['total'] for row in results])
        
    def run_query(self, query):
        result = self.cursor.execute(query)
        return result

class User(object):
    def __init__(self, id=None, username="", password="", active="", admin=""):
        self.SQL = SQLConnection()
        self.id = id
        self.username = username
        self.password = password
        self.active = active
        self.admin = admin

    def __repr__(self):
        return "id: {} username: {} active: {} admin: {}".format(self.id, self.username, self.active, self.admin)
        
    def save(self):
        if self.password:
            query = "INSERT INTO users(username, password, active, admin) VALUES('%s', '%s', %s, %s)" % (self.username, self.password, self.active, self.admin)
            result = self.SQL.run_query(query)
        self.refresh_info()            
        return result
        
    def set_password(self):
        if self.password and self.id:
            query = "UPDATE users SET `password`='%s' WHERE id=%s" % (self.password, self.id)
            self.SQL.run_query(query)
        self.refresh_info()            
            
    def set_active(self):
        if self.id:
            query = "UPDATE users SET `active`=%s WHERE id=%s" % (True, self.id)
            self.SQL.run_query(query)
        self.refresh_info()
    
    def set_inactive(self):
        if self.id:
            query = "UPDATE users SET `active`=%s WHERE id=%s" % (False, self.id)
            self.SQL.run_query(query)            
        self.refresh_info()            
        
    def set_as_admin(self):
        if self.id:
            query = "UPDATE users SET `admin`=%s WHERE id=%s" % (True, self.id)
            self.SQL.run_query(query)            
        self.refresh_info()       
        
    def revoke_admin(self):
        if self.id:
            query = "UPDATE users SET `admin`=%s WHERE id=%s" % (False, self.id)
            self.SQL.run_query(query)    
        self.refresh_info()
        
    def refresh_info(self):
        results = self.SQL.refresh_user(self.username)
        self.active = results['active']
        self.admin = results['admin']
        
class DateManager(object):
    def __init__(self):
        self.today = datetime.date.today()
        self.year = self.today.year
        self.first_day_of_period = self.first_day_of_pay_period()
        self.last_day_of_period = self.first_day_of_period + timedelta(days=14)
        self.sundaylist = self.get_sunday_list(self.year)
        self.last_year_sunday_list = self.get_sunday_list(self.year - 1)
        self.ONE_WEEK_DELTA = datetime.timedelta(weeks=1)
    
    def get_today(self):
        return self.today
    
    def get_year(self):
        return self.year
    
    def get_first_day_of_period(self):
        return self.first_day_of_period
    
    def get_last_day_of_period(self):
        return self.last_day_of_period
    
    def get_sunday_list(self):
        return self.sundaylist
    
    def get_last_year_sunday_list(self):
        return self.last_yuear_sunday_list
    
    def get_one_week_delta(self):
        return self.ONE_WEEK_DELTA
    
    def first_day_of_pay_period(self):
        '''Returns first day of pay period'''
        first_day_of_year = datetime.date(self.year,1,1) 
        first_day_of_pay_period_for_year = first_day_of_year - datetime.timedelta(first_day_of_year.weekday())
        if calendar.isleap(self.year):
            time_delta = datetime.timedelta(days = ((int(self.today.strftime("%W")) - 1) * 7)) 
        else:
            time_delta = datetime.timedelta(days = ((int(self.today.strftime("%W")) - 1) * 7) - 1)
        return first_day_of_year + time_delta 

    def get_sunday_list(self, year):
        '''Returns a list of every Sunday that starts a new pay period'''
        sundayList = []
        for month in xrange(1,13):
            sundayList1 = [sundayList.append('%d-%d-%d' % (year,month,day)) for day in xrange(1,1+monthrange(year,month)[1]) if weekday(year,month,day) == 6]
        return [sundayList[x] for x in xrange(0,len(sundayList),2)]   
