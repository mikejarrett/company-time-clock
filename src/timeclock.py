# -*- coding: utf-8 -*-

from calendar import weekday, monthrange
from manager import DateManager, SQLConnection, User
import hashlib
import sys
import time, datetime

import pygtk
if not sys.platform == 'win32':
    pygtk.require('2.0')
import gtk

from .settings import SALTY_GOODNESS

class TimeClock(object):

    def __init__(self):
        self.date_manager = DateManager()
        self.SQL = SQLConnection()
        self.user = None
        self.VERSION = "v1.5.0"
        self.ABOUT = "Company, Inc. Time Clock {}\n\nCreated by Mike Jarrett for internal Company use.\n\nReport all errors to jarrettm@msu.edu or xXXXX\n(c)2007".format(self.VERSION)

        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_size_request(400,150)
        self.window.set_position(gtk.WIN_POS_CENTER - 350)
        self.window.set_resizable(False)
        self.window.connect("destroy", self.close_application)
        self.window.set_title("Time Clock {}".format(self.VERSION))
        self.window.set_border_width(0)

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
        self.status_Bar = gtk.Statusbar()


        self.vertical_box_main.pack_start(self.main_interface, True, True, 0)
        self.main_interface.show()
        self.window.show()


    def process_login(self, login_box):
        username = self.username_entry.get_text()
        password = hashlib.sha512(self.password_entry.get_text() + SALTY_GOODNESS).hexdigest()
        self.user = self.SQL.get_user(username, password)
        if self.user:
            if self.user.active:
                self.login_box.remove(self.username_entry)
                self.login_box.remove(self.password_entry)
                self.login_box.remove(self.login_button)
                self.login_box.hide()
                if self.user.admin:
                    self.window.set_title("Time Clock {} - {} (admin)".format(self.VERSION, self.user.username))
                else:
                    self.window.set_title("Time Clock {} - {}".format(self.VERSION, self.user.username))
                self.window.set_size_request(400,500)
                self.build_menu_bar()
                self.build_scroll_window()
                self.build_bottom_buttons()
            elif not self.user.active:
                dialog = gtk.MessageDialog(message_format="User {} is not active".format(self.user.username), buttons=gtk.BUTTONS_OK)
                dialog.run()
                dialog.destroy()

                self.login_box.remove(self.username_entry)
                self.login_box.remove(self.password_entry)
                self.login_box.remove(self.login_button)
                self.login_box.hide()
                self.build_login_box()
        else:
            dialog = gtk.MessageDialog(message_format="User {} could not be found".format(username), buttons=gtk.BUTTONS_OK)
            dialog.run()
            dialog.destroy()

            self.login_box.remove(self.username_entry)
            self.login_box.remove(self.password_entry)
            self.login_box.remove(self.login_button)
            self.login_box.hide()
            self.build_login_box()

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
                                ("/File/E_xit", "<control>X", gtk.main_quit, 0, None),
                                ("/A_dmin", None, None, 0, "<Branch>"),
                                ("/Admin/_Admin Panel", "<control>A", self.admin_panel, 0, None),
                                ("/_Options", "<control>O", None, 0, "<Branch>"),
                                ("/Options/Punch _In", "<control>I", self.clock_in, 0, None),
                                ("/Options/Punch _Out", "<control>O", self.clock_out, 0, None),
                                ("/Options/sep1", None, None, 0, "<Separator>" ),
                                ("/Options/_Show Punches", "<control>S", self.show_punches, 0, None),
                                ("/Options/sep2", None, None, 0, "<Separator>"),
                                ("/Options/Calc _Time", "<control>T", self.calculate_time, 0, None),
                                ("/_Help", None, None, 0, "<LastBranch>"),
                                ("/Help/Abo_ut", "<control>U", self.about_info, 0, None),
                                ("/Help/sep2", None, None, 0, "<Separator>"),
                                ("/Help/Change Password", "control>P", self.change_password, 0, None),
                                )
        else:
            self.menu_items = (("/_File", None, None, 0, "<Branch>" ),
                                ("/File/E_xit", None, gtk.main_quit, 0, None ),
                                ("/_Options", "<control>O", None, 0, "<Branch>"),
                                ("/Options/Punch _In", "<control>I", self.clock_in, 0, None),
                                ("/Options/Punch _Out", "<control>O", self.clock_out, 0, None),
                                ("/Options/sep1", None, None, 0, "<Separator>" ),
                                ("/Options/_Show Punches", "<control>S", self.show_punches, 0, None),
                                ("/Options/sep2", None, None, 0, "<Separator>"),
                                ("/Options/Calc _Time", "<control>T", self.calculate_time, 0, None),
                                ("/_Help", None, None, 0, "<LastBranch>"),
                                ("/Help/Abo_ut", "<control>U", self.about_info, 0, None),
                                ("/Help/sep2", None, None, 0, "<Separator>"),
                                ("/Help/Change Password", "control>P", self.change_password, 0, None),
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

        ## Creating Punch In button
        clock_in_button = gtk.Button("Punch In")
        clock_in_button.connect("clicked", self.clock_in)
        self.button_container.pack_start(clock_in_button, False, False, 0)
        clock_in_button.show()

        ## Creating Punch Out button
        clock_out_button = gtk.Button("Punch Out")
        clock_out_button.connect("clicked", self.clock_out)
        self.button_container.pack_start(clock_out_button, False, False, 0)
        clock_out_button.show()

        ## Creating Show Punches button
        show_punches_button = gtk.Button("Show Punches")
        show_punches_button.connect("clicked", self.show_punches)
        self.button_container.pack_start(show_punches_button, False, False, 0)
        show_punches_button.show()

        ## Creates Calc Time button
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
        help_string = "Report any bugs to jarrettm@msu.edu \n\n"
        help_string += "This software is freely distributed in accordance with \n"
        help_string += "the GNU Lesser General Public (LGPL) license, version 3 \n"
        help_string += "or later as published by the Free Software Foundation. \n"
        help_string += "For details see LGPL: http://www.gnu.org/licenses/lgpl.html \n"
        help_string += "and GPL: http://www.gnu.org/licenses/gpl-3.0.html \n\n"
        help_string += "This software is provided by the copyright holders and \n"
        help_string += "contributors 'as is' and any express or implied warranties, \n"
        help_string += "including, but not limited to, the implied warranties of \n"
        help_string += "merchantability and fitness for a particular purpose are \n"
        help_string += "disclaimed. In no event shall the copyright owner or \n"
        help_string += "contributors be liable for any direct, indirect, incidental, \n"
        help_string += "special, exemplary, or consequential damages (including, \n"
        help_string += "but not limited to, procurement of substitute goods or \n"
        help_string += "services; loss of use, data, or profits; or business \n"
        help_string += "interruption) however caused and on any theory of \n"
        help_string += "liability, whether in contract, strict liability, \n"
        help_string += "or tort (including negligence or otherwise) arising \n"
        help_string += "in any way out of the use of this software, even \n"
        help_string += "if advised of the possibility of such damage."
        self.textbuffer.set_text(help_string)

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

        hbox = gtk.HBox(False, 10)
        hbox.set_border_width(10)

        reset_button = gtk.Button("Reset Password")
        reset_button.connect_object("clicked", self.check_passwords_match, self.password_reset_box, password1, password2, hbox)
        cancel_button = gtk.Button("Cancel")
        cancel_button.connect_object("clicked", self.rebuild_main_window, self.password_reset_box, False)

        hbox.pack_start(reset_button, False, True, 0)
        hbox.pack_start(cancel_button, False, True, 0)
        hbox.show()

        self.vertical_box_main.pack_start(self.password_reset_box, True, True, 0)
        self.password_reset_box.show()

        self.password_reset_box.pack_start(password1, False, True, 0)
        self.password_reset_box.pack_start(password2, False, True, 0)
        self.password_reset_box.pack_start(hbox, False, True, 0)
        password1.show()
        password2.show()
        reset_button.show()
        cancel_button.show()

    def check_passwords_match(self, widget, password1, password2, hbox):
        if password1.get_text() == password2.get_text():
            newpassword = hashlib.sha512(password1.get_text() + SALTY_GOODNESS).hexdigest()
            self.user.password = newpassword
            self.user.set_password()
            self.rebuild_main_window(widget, None)
            self.textbuffer.set_text("Password changed successfully")
        else:
            dialog = gtk.MessageDialog(message_format="Passwords don't match. Please try again", buttons=gtk.BUTTONS_OK)
            dialog.run()
            dialog.destroy()
            password1.set_text("")
            password2.set_text("")

    def rebuild_main_window(self, widget, data):
        widget.hide()
        self.window.set_size_request(400,500)
        self.menubar.show()
        self.scroll_window.show()
        self.textview.show()
        self.button_box.show()

    def close_application(self, widget):
        gtk.main_quit()

    def admin_panel(self, widget, data=''):
        admin = AdminControlPanel(self.user, self.window)

    def get_main_menu(self, window):
        accel_group = gtk.AccelGroup()
        item_factory = gtk.ItemFactory(gtk.MenuBar, "<main>", accel_group)
        item_factory.create_items(self.menu_items)
        window.add_accel_group(accel_group)
        self.item_factory = item_factory
        return item_factory.get_widget("<main>")

    def on_dialog_key_press(self, dialog, event):
        print dialog
        print event
        if event.string == ' ':
            dialog.response(gtk.RESPONSE_OK)
            return True
        return False


class AdminControlPanel(TimeClock):
    def delete_event(self, widget, event, data=None):
        self.MAIN_WINDOW.show()
        self.window.destroy()
        return False

    def __init__(self, user, window):
        self.OPTIONS = ["Activate", "Deactivate", "Admin", "Revoke"]
        self.MAIN_WINDOW = window
        self.MAIN_WINDOW.hide()
        self.SQL = SQLConnection()
        self.user = user
        self.ABOUT = ""

        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_size_request(400,250)
        self.window.set_position(gtk.WIN_POS_CENTER)
        self.window.set_resizable(False)
        self.window.connect("delete_event", self.delete_event)
        self.window.set_title("Admin Control Panel")
        self.window.set_border_width(0)

        self.vertical_box_main = gtk.VBox(False, 0)
        self.window.add(self.vertical_box_main)

        self.main_interface = gtk.VBox(False, 10)
        self.main_interface.set_border_width(10)

        self.vertical_box_main.pack_start(self.main_interface, True, True, 0)

        self.build_menu_bar()
        self.build_scroll_window()

        self.textbuffer.set_text("Welcome to the admin interface. \nPerform actions using the options menu. \n(TODO - fill this out more)")
        self.window.show_all()

    def build_menu_bar(self):
        self.menu_items = (("/_File", None, None, 0, "<Branch>" ),
                            ("/File/_Close Window", "<control>C", self.delete_event, 0, None ),
                            ("/_Options", None, None, 0, "<Branch>" ),
                            ("/Options/_Add a user", "<control>A", self.add_a_user, 0, None),
                            ("/Options/Ac_tivate a user", "<control>T", self.select_user, 0, None),
                            ("/Options/_Deactivate a user", "<control>D", self.select_user, 1, None),
                            ("/Options/sep1", None, None, 0, "<Separator>" ),
                            ("/Options/_Make user an admin", "<control>M", self.select_user, 2, None),
                            ("/Options/_Revoke admin on user", "<control>R", self.select_user, 3, None),
                            )
        self.menubar = self.get_main_menu(self.window)
        self.main_interface.pack_start(self.menubar, False, True, 0)
        self.menubar.show()

    def add_a_user(self, widget, data=""):
        self.add_user_window = gtk.Window()
        self.add_user_window.set_position(gtk.WIN_POS_CENTER)
        self.add_user_window.set_size_request(400, 200)
        self.add_user_window.set_title("Add User")

        self.vertical_box = gtk.VBox(False, 0)
        self.add_user_window.add(self.vertical_box)

        self.box = gtk.VBox(False, 10)
        self.box.set_border_width(10)
        self.vertical_box.pack_start(self.box, True, True, 0)

        self.username_entry = gtk.Entry(max=0)
        self.password_entry = gtk.Entry(max=0)
        self.password_entry.set_visibility(False)

        self.admin_checkbutton = gtk.CheckButton("Admin")
        self.active_checkbutton = gtk.CheckButton("Active")
        self.active_checkbutton.set_active(True)
        self.hbox = gtk.HBox(False, 10)
        self.hbox.set_border_width(10)
        self.hbox.pack_start(self.admin_checkbutton, False, False, 0)
        self.hbox.pack_start(self.active_checkbutton, False, False, 0)

        self.add_user_button = gtk.Button("Add User")
        self.add_user_button.connect_object("clicked", self.add_user, self.username_entry, self.password_entry, self.admin_checkbutton, self.active_checkbutton)

        self.box.pack_start(self.username_entry, True, True, 0)
        self.box.pack_start(self.password_entry, True, True, 0)
        self.box.pack_start(self.hbox, True, True, 0)
        self.box.pack_start(self.add_user_button, True, True, 0)
        self.add_user_window.show_all()

    def add_user(self, username, password, make_admin, make_active):
        username = username.get_text()
        password = hashlib.sha512(password.get_text() + SALTY_GOODNESS).hexdigest()
        admin = make_admin.get_active()
        active = make_active.get_active()
        user = User(id=None, username=username, password=password, active=active, admin=admin)
        if user.save():
            self.add_user_window.destroy()
            text = " User '{0}' added successfully. \n username: {0} \n active: {1} \n admin: {2}".format(username, active, admin)
            self.textbuffer.set_text(text)

    def select_user(self, option, data=""):
        self.select_user_window = gtk.Window()
        self.select_user_window.set_position(gtk.WIN_POS_CENTER)
        self.select_user_window.set_size_request(400, 100)
        self.select_user_window.set_title("Find a user to {}".format(self.OPTIONS[option].lower()))

        self.vertical_box = gtk.VBox(False, 0)
        self.select_user_window.add(self.vertical_box)

        self.box = gtk.VBox(False, 10)
        self.box.set_border_width(10)
        self.vertical_box.pack_start(self.box, True, True, 0)

        self.select_username_entry = gtk.Entry(max=0)
        self.select_user_button = gtk.Button("Find User")
        self.select_user_button.connect_object("clicked", self.find_user, option)

        self.box.pack_start(self.select_username_entry, True, True, 0)
        self.box.pack_start(self.select_user_button, True, True, 0)
        self.select_user_window.show_all()

    def find_user(self, option):
        username = self.select_username_entry.get_text()
        selected_user = self.SQL.get_user(username, None)
        if selected_user:
            self.select_user_window.hide()
        else:
            print "TODO - Couldn't find user"
            self.select_user_window.hide()

        if option == 0:
            selected_user.set_active()
            text = " User '{0}' activated successfully. \n username: {0} \n active: {1} \n admin: {2}".format(selected_user.username, selected_user.active, selected_user.admin)
            self.textbuffer.set_text(text)
        elif option == 1:
            selected_user.set_inactive()
            text = " User '{0}' de-activated successfully. \n username: {0} \n active: {1} \n admin: {2}".format(selected_user.username, selected_user.active, selected_user.admin)
            self.textbuffer.set_text(text)
        elif option == 2:
            selected_user.set_as_admin()
            text = " User '{0}' admin rights added successfully. \n username: {0} \n active: {1} \n admin: {2}".format(selected_user.username, selected_user.active, selected_user.admin)
            self.textbuffer.set_text(text)
        elif option == 3:
            selected_user.revoke_admin()
            text = " User '{0}' admin rights revoked successfully. \n username: {0} \n active: {1} \n admin: {2}".format(selected_user.username, selected_user.active, selected_user.admin)
            self.textbuffer.set_text(text)
        else:
            self.select_user_window.hide()
            self.textbuffer.set_text("TODO - Something went wrong")
