import sys
import pygtk
if not sys.platform == 'win32':
    pygtk.require('2.0')
import gtk
import time, datetime
from calendar import weekday, monthrange
from log_manager import DateManager, SQLConnection
import hashlib

SALTY_GOODNESS = "Sup3r-c0mplex s4lty g0On3sS"

class TimeClock:
    def process_login(self, login_box):
        username = self.username_entry.get_text()
        password = hashlib.sha512(self.password_entry.get_text() + SALTY_GOODNESS).hexdigest()
        self.user = self.SQL.get_user(username, password)
        if self.user:
            self.login_box.remove(self.username_entry)
            self.login_box.remove(self.password_entry)
            self.login_box.remove(self.login_button)
            self.login_box.hide()
            self.window.set_size_request(400,500)
            self.build_menu_bar()
            self.build_scroll_window()
            self.build_bottom_buttons()
        else:
            self.login_box.remove(self.username_entry)
            self.login_box.remove(self.password_entry)
            self.login_box.remove(self.login_button)
            self.login_box.hide()
            self.build_login_box()
            
        
    def __init__(self):
        self.date_manager = DateManager()
        self.SQL = SQLConnection()
        self.user = None
        self.VERSION = "v1.3.1"
        self.ABOUT = "Company, Inc. Time Clock {}\n\nCreated by Mike Jarrett for internal Company use.\n\nReport all errors to jarrettm@msu.edu or xXXXX\n(c)2007".format(self.VERSION)
        
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_resizable(False)  
        self.window.connect("destroy", self.close_application)
        self.window.set_title("Company Time Clock {}".format(self.VERSION))
        self.window.set_border_width(0)
        self.window.set_size_request(400,150)
    
        self.vertical_box_main = gtk.VBox(False, 0)
        self.window.add(self.vertical_box_main)
        self.vertical_box_main.show()

        ##Create Login Panel
        self.login_box = gtk.VBox(False, 10)
        self.login_box.set_border_width(10)
        self.vertical_box_main.pack_start(self.login_box, True, True, 0)        
        self.build_login_box()
        
        ##Create everything else - but hidden
        self.main_interface = gtk.VBox(False, 10)
        self.main_interface.set_border_width(10)
        self.vertical_box_main.pack_start(self.main_interface, True, True, 0)
        self.main_interface.show()
        self.window.show()

    def build_login_box(self):
        self.username_entry = gtk.Entry(max=0)  
        self.password_entry = gtk.Entry(max=0) 
        self.password_entry.set_visibility(False)
        self.login_button = gtk.Button("Login")
        self.login_button.connect_object("clicked", self.process_login, self.login_box)        
        self.login_box.pack_start(self.username_entry, False, True, 0)
        self.login_box.pack_start(self.password_entry, False, True, 0)
        self.login_box.pack_start(self.login_button, False, True, 0)
        self.username_entry.show()
        self.password_entry.show()
        self.login_button.show()
        self.login_box.show()
    
    def build_menu_bar(self):
        if self.user.admin:
            self.menu_items = (("/_File", None, None, 0, "<Branch>"),
                                ("/File/E_xit", None, gtk.main_quit, 0, None),
                                ("/A_dmin", None, None, 0, "<Branch>"),
                                ("/Admin/Add a user", None, None, 0, None),
                                ("/Admin/Activate a user", None, None, 0, None),
                                ("/Admin/Deactivate a user", None, None, 0, None),
                                ("/Admin/Promote user to admin", None, None, 0, None),
                                ("/_Options", None, None, 0, "<Branch>"),
                                ("/Options/Punch _In", "<control>I", self.clock_in, 0, None),
                                ("/Options/Punch _Out", "<control>O", self.clock_out, 0, None),
                                ("/Options/sep1", None, None, 0, "<Separator>" ),
                                ("/Options/_Show Punches", "<control>S", self.show_punches, 0, None),
                                ("/Options/sep2", None, None, 0, "<Separator>"),
                                ("/Options/Calc _Time", "<control>T", self.calculate_time, 0, None),
                                ("/_Help", None, None, 0, "<LastBranch>"),
                                ("/_Help/About", None, self.about_info, 0, None),
                                ("/Help/sep2", None, None, 0, "<Separator>"),                                
                                ("/Help/Change Password", None, self.change_password, 0, None),
                                )            
        else:
            self.menu_items = (("/_File", None, None, 0, "<Branch>" ),
                                ("/File/E_xit", None, gtk.main_quit, 0, None ),
                                ("/_Options", None, None, 0, "<Branch>" ),
                                ("/Options/Punch _In", "<control>I", self.clock_in, 0, None),
                                ("/Options/Punch _Out", "<control>O", self.clock_out, 0, None ),
                                ("/Options/sep1", None, None, 0, "<Separator>" ),
                                ("/Options/_Show Punches", "<control>S", self.show_punches, 0, None),
                                ("/Options/sep2", None, None, 0, "<Separator>"),
                                ("/Options/Calc _Time", "<control>T", self.calculate_time, 0, None),
                                ("/_Help", None, None, 0, "<LastBranch>" ),
                                ("/_Help/About", None, self.about_info, 0, None ),
                                ("/Help/sep2", None, None, 0, "<Separator>"),
                                ("/Help/Change Password", None, self.change_password, 0, None),                                
                                )

        self.menubar = self.get_main_menu(self.window)
        self.main_interface.pack_start(self.menubar, False, True, 0)
        self.menubar.show() 

    def build_scroll_window(self):
        self.scroll_window = gtk.ScrolledWindow()
        self.scroll_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.textview = gtk.TextView()
        self.textbuffer = self.textview.get_buffer()
        self.scroll_window.add(self.textview)
        self.scroll_window.show()
        self.textbuffer.set_text(self.ABOUT)
        self.textview.show()
        self.textview.set_editable(False)
        self.textview.set_cursor_visible(False)     
        self.main_interface.pack_start(self.scroll_window)
        
    def build_bottom_buttons(self):
        self.button_box = gtk.HButtonBox()
        self.main_interface.pack_start(self.button_box, False, False, 0)
        self.button_box.show()

        self.button_container = gtk.HBox()
        self.button_container.show()
        self.button_box.pack_start(self.button_container, False, False, 0)

        # Creating Punch In button
        clock_in_button = gtk.Button("Punch In")
        clock_in_button.connect("clicked", self.clock_in)
        self.button_container.pack_start(clock_in_button, False, False, 0)
        clock_in_button.show()

        # Creating Punch Out button
        clock_out_button = gtk.Button("Punch Out")
        clock_out_button.connect("clicked", self.clock_out)
        self.button_container.pack_start(clock_out_button, False, False, 0)
        clock_out_button.show()

        # Creating Show Punches button
        show_punches_button = gtk.Button("Show Punches")
        show_punches_button.connect("clicked", self.show_punches)
        self.button_container.pack_start(show_punches_button, False, False, 0)
        show_punches_button.show()

        # Creates Calc Time button
        calculate_time_button = gtk.Button("Calc Time")
        calculate_time_button.connect("clicked", self.calculate_time)
        self.button_container.pack_start(calculate_time_button, False, False, 0)
        calculate_time_button.show()
        

    def clock_in(self, widget, data=""):
        self.textbuffer.set_text(self.SQL.clock_in(self.user.id))
        
    def clock_out(self, widget, data=""):
        self.textbuffer.set_text(self.SQL.clock_out(self.user.id))

    def show_punches(self, widget, data=""):
        results = self.SQL.get_punches_for_period(self.user.id, self.date_manager.get_first_day_of_period(), self.date_manager.get_last_day_of_period())
        punches = ''
        for result in results:
            punches += "{}   {}   {}\n".format(result['time_in'], result['time_out'], result['total'])
        punches += "\nTotal: {}".format(self.calculate_time(False, True))
        self.textbuffer.set_text(punches)

    def calculate_time(self, widget, data=""):
        total = self.SQL.get_total_time(self.user.id, self.date_manager.get_first_day_of_period(), self.date_manager.get_last_day_of_period())
        if data:
            return total
        else:
            self.textbuffer.set_text("Total Time: {}".format(total))

    def about_info(self, widget, data=""):
        self.textbuffer.set_text(self.ABOUT)

    def change_password(self, widget, data=""):
        self.window.set_size_request(400,150)
        self.menubar.hide()
        self.scroll_window.hide()
        self.textview.hide()
        self.button_box.hide()

        password1 = gtk.Entry(max=0)        
        password1.set_visibility(False)
        password2 = gtk.Entry(max=0) 
        password2.set_visibility(False)
        
        self.password_reset_box = gtk.VBox(False, 10)
        self.password_reset_box.set_border_width(10)

        reset_button = gtk.Button("Reset Password")
        reset_button.connect_object("clicked", self.check_passwords_match, self.password_reset_box, password1, password2, reset_button)

        self.vertical_box_main.pack_start(self.password_reset_box, True, True, 0)
        self.password_reset_box.show()
        
        self.password_reset_box.pack_start(password1, False, True, 0)
        self.password_reset_box.pack_start(password2, False, True, 0)
        self.password_reset_box.pack_start(reset_button, False, True, 0)
        password1.show()
        password2.show()
        reset_button.show()  
 
    def check_passwords_match(self, widget, password1, password2, reset_button):
        if password1.get_text() == password2.get_text():
            widget.hide()
            self.window.set_size_request(400,500)
            self.menubar.show()
            self.scroll_window.show()
            self.textview.show()
            self.button_box.show()
            newpassword = hashlib.sha512(password1.get_text() + SALTY_GOODNESS).hexdigest()
            self.user.password = newpassword
            self.SQL.run_query(self.user.set_password())
            
            self.textbuffer.set_text("Password changed successfully")
        else:
            self.password_reset_box.remove(password1)
            self.password_reset_box.remove(password2)
            self.password_reset_box.remove(reset_button)
            self.password_reset_box.hide()
            self.change_password(widget)        
        
    def close_application(self, widget):
        gtk.main_quit()

    def get_main_menu(self, window):
        accel_group = gtk.AccelGroup()
        item_factory = gtk.ItemFactory(gtk.MenuBar, "<main>", accel_group)
        item_factory.create_items(self.menu_items)
        window.add_accel_group(accel_group)
        self.item_factory = item_factory
        return item_factory.get_widget("<main>")        
##End of class