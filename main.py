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
    def __init__(self, create_user):
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
        if create_user:
            try:
                self.cursor.execute("grant CREATE,INSERT,DELETE,UPDATE,SELECT on timeclock.* to timeclock@localhost")
                self.cursor.execute("set password for timeclock = password('platypus')")
                self.cursor.execute("flush privileges")
                print "Added, and granted all rights to timeclock user into the databse"
            except Exception, error:
                logging.error(" %s - %s" % (datetime.now(), error))
        print "Database setup successfully. Sign in with: 'admin' and your choosen password to add new accounts"
    
    def __del__(self):
        self.conn.close()
        
    def create_database(self):
        try:
            self.cursor.execute("CREATE DATABASE timeclock")
            print "Database created successfully"
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
            print "Created users table successfully"
            self.cursor.execute("INSERT INTO users(username, password, active, admin) VALUES('%s', '%s', '%s', '%s')" % ("admin", password, 1, 1))
            print "Added admin user to timeclock.users successfully"
        except Exception, error:
            print "Couldn't created table users"
            logging.error(" %s - %s" % (datetime.now(), error))
            sys.exit(-1)
    
    def create_table_time_punches(self):
        try:
            self.cursor.execute("CREATE TABLE time_punches(id INT PRIMARY KEY AUTO_INCREMENT, user_id INT, time_in DATETIME, time_out DATETIME, total FLOAT(2,2))")
            print "Created time_punches table successfully"
        except Exception, error:
            print "Couldn't created table times_punches"
            logging.error(" %s - %s" % (datetime.now(), error))
            sys.exit(-1)
            
    def get_sql_credentials(self):
        username = raw_input("Enter SQL user: ")
        pwd = getpass.getpass("Enter SQL password: ")
        return username, pwd


def help():
    print "Usage: main.py [OPTIONS]"
    print "--setup \t Creates database `timeclock` and tables `users` and `time_punches`"
    print "--create-user \t Creates user 'timeclock' with password 'platypus'."
    print "--setup --create-user \t performs both of the above operations at once.\n"
    print "Report any bugs to jarrettm@msu.edu"
    print "This software is freely distributed in accordance with"
    print "the GNU Lesser General Public (LGPL) license, version 3 or later"
    print "as published by the Free Software Foundation."
    print "For details see LGPL: http://www.gnu.org/licenses/lgpl.html"
    print "and GPL: http://www.gnu.org/licenses/gpl-3.0.html\n"
    print 'This software is provided by the copyright holders and contributors "as is"'
    print "and any express or implied warranties, including, but not limited to, the"
    print "implied warranties of merchantability and fitness for a particular purpose"
    print "are disclaimed. In no event shall the copyright owner or contributors be"
    print "liable for any direct, indirect, incidental, special, exemplary, or"
    print "consequential damages (including, but not limited to, procurement of"
    print "substitute goods or services; loss of use, data, or profits; or business"
    print "interruption) however caused and on any theory of liability, whether in"
    print "contract, strict liability, or tort (including negligence or otherwise)"
    print "arising in any way out of the use of this software, even if advised of the"
    print "possibility of such damage. "    
    
def main():
    gtk.main()
    return 0       

if __name__ == "__main__":
    if "--setup" in sys.argv and "--help" not in sys.argv and "-h" not in sys.argv:
        import MySQLdb
        import getpass
        if "--create-user" in sys.argv:
            Setup(True)
        else:
            Setup(False)
    elif "--help" in sys.argv or "-h" in sys.argv:
        help()

    else:
        TimeClock()
        main()