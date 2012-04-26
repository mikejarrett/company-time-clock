import pygtk
import sys
if not sys.platform == 'win32':
    pygtk.require('2.0')
import gtk
from timeclock import TimeClock
from datetime import datetime
import logging
import hashlib

SALTY_GOODNESS = "Sup3r-c0mplex s4lty g0On3sS"
logging.basicConfig(filename="errors.log",level=logging.ERROR)

class Setup(object):
    def __init__(self):
        sql_user, sql_password = self.get_sql_credentials()
        create_the_database = False
        create_user_table = False
        create_time_punches_table = False
        try: #Attempt to log into MySQL
            self.conn = MySQLdb.connect('localhost', sql_user, sql_password)
        except Exception, error:
            logging.error(" %s - %s" % (datetime.now(), error))
            print "Couldn't connect to MySQL server. Error: {}".format(str(error))
            sys.exit(-1)
            
        try: #Attempt to select timeclock database
            self.cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)
            self.cursor.execute("USE timeclock")
        except Exception, error:
            create_the_database = True
            logging.error(" %s - %s" % (datetime.now(), error))
        
        try: #Check user table is there
            self.cursor.execute("SELECT * FROM users")
        except Exception, error:
            create_user_table = True
            logging.error(" %s - %s" % (datetime.now(), error))
            
        try: #Check user table is there
            self.cursor.execute("SELECT * FROM time_punches")
        except Exception, error:
            create_time_punches_table = True
            logging.error(" %s - %s" % (datetime.now(), error))
        
        if create_the_database: self.create_database()
        if create_user_table: self.create_table_users()
        if create_time_punches_table: self.create_table_time_punches()
    
        print "Database setup successfully. Sign in with: 'admin' and your choosen password to add new accounts"
        
    def create_database(self):
        try:
            self.cursor.execute("CREATE DATABASE timeclock")
            self.cursor.execute("USE timeclock")
        except Exception, error:
            print "Couldn't created database timeclock"
            logging.error(" %s - %s" % (datetime.now(), error))
            sys.exit(-1)
    
    def create_table_users(self):
        pwd = getpass.getpass("Enter a password for the Time Clock admin: ")
        password = hashlib.sha512(pwd + SALTY_GOODNESS).hexdigest()        
        try:
            self.cursor.execute("CREATE TABLE users(id INT PRIMARY KEY AUTO_INCREMENT, username VARCHAR(25) UNIQUE, password VARCHAR(255), active BOOL, admin BOOL)")
            self.cursor.execute("INSERT INTO users(username, password, active, admin) VALUES('%s', '%s', '%s', '%s')" % ("admin", password, 1, 1))
        except Exception, error:
            print "Couldn't created table users"
            logging.error(" %s - %s" % (datetime.now(), error))
            sys.exit(-1)
    
    def create_table_time_punches(self):
        try:
            self.cursor.execute("CREATE TABLE time_punches(id INT PRIMARY KEY AUTO_INCREMENT, user_id INT, time_in DATETIME, time_out DATETIME, total FLOAT(2,2))")
        except Exception, error:
            print "Couldn't created table times_punches"
            logging.error(" %s - %s" % (datetime.now(), error))
            sys.exit(-1)
            
    def get_sql_credentials(self):
        username = raw_input("Enter SQL user: ")
        pwd = getpass.getpass("Enter SQL password: ")
        
        return username, pwd

def main():
    gtk.main()
    return 0       

if __name__ == "__main__":
    if "--setup" in sys.argv and "--help" not in sys.argv:
        import MySQLdb
        import getpass
        Setup()
    elif "--setup" in sys.argv and "--help" not in sys.argv:
        print "TODO --help"
    else:
        TimeClock()
        main()