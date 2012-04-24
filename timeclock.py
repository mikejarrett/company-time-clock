import sys
import pygtk
if not sys.platform == 'win32':
    pygtk.require('2.0')
import gtk
import time, datetime
from calendar import weekday, monthrange
from log_manager import LogManager

class TimeClock:
    def __init__(self):
        self.log_manager = LogManager()
        self.VERSION = "Company Time Clock v1.2.1"
        self.ABOUT = "\nCompany, Inc. Time Clock\n{}\n\nCreated by Mike Jarrett for internal Company use.\n\nReport all errors to jarrettm@msu.edu or xXXXX\n(c)2007".format(self.VERSION)
        
        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.set_resizable(False)  
        window.connect("destroy", self.close_application)
        window.set_title("%s" % self.VERSION)
        window.set_border_width(0)
        window.set_size_request(400,500)

        vertical_box_main = gtk.VBox(False, 0)
        window.add(vertical_box_main)
        vertical_box_main.show()

        box2 = gtk.VBox(False, 10)
        box2.set_border_width(10)
        vertical_box_main.pack_start(box2, True, True, 0)
        box2.show()

        self.menu_items = (
        ( "/_File", None, None, 0, "<Branch>" ),
        ( "/File/E_xit", None, gtk.main_quit, 0, None ),
        ( "/_Options", None, None, 0, "<Branch>" ),
        ( "/Options/Punch _In", "<control>I", self.punchIn, 0, None),
        ( "/Options/Punch _Out", "<control>O", self.punchOut, 0, None ),
        ( "/Options/sep1", None, None, 0, "<Separator>" ),
        ( "/Options/_Show Punches", "<control>S", self.showPunches, 0, None),
        ( "/Options/sep2", None, None, 0, "<Separator>"),
        ( "/Options/Calc _Time", "<control>T", self.calculateTime, 0, None),
        ( "/_Help", None, None, 0, "<LastBranch>" ),
        ( "/_Help/About", None, self.aboutMenu, 0, None ),
        )

        menubar = self.get_main_menu(window)
        box2.pack_start(menubar, False, True, 0)
        menubar.show()
    
        scroll_window = gtk.ScrolledWindow()
        scroll_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.textview = gtk.TextView()
        self.textbuffer = self.textview.get_buffer()
        scroll_window.add(self.textview)
        scroll_window.show()
        self.textview.show()

        self.textview.set_editable(False)
        self.textview.set_cursor_visible(False)

        box2.pack_start(scroll_window)
               
        self.textbuffer.set_text(self.ABOUT)

        hbox = gtk.HButtonBox()
        box2.pack_start(hbox, False, False, 0)
        hbox.show()

        vbox = gtk.HBox()
        vbox.show()
        hbox.pack_start(vbox, False, False, 0)

        ## Creating Punch In button
        clockIn = gtk.Button("Punch In")
        clockIn.connect("clicked", self.punchIn)
        vbox.pack_start(clockIn, False, False, 0)
        clockIn.show()

        ## Creating Punch Out button
        clockOut = gtk.Button("Punch Out")
        clockOut.connect("clicked", self.punchOut)
        vbox.pack_start(clockOut, False, False, 0)
        clockOut.show()

        ## Creating Show Punches button
        showPunch = gtk.Button("Show Punches")
        showPunch.connect("clicked", self.showPunches)
        vbox.pack_start(showPunch, False, False, 0)
        showPunch.show()

        ## Creates Calc Time button
        timeCalc = gtk.Button("Calc Time")
        timeCalc.connect("clicked", self.calculateTime)
        vbox.pack_start(timeCalc, False, False, 0)
        timeCalc.show()

        separator = gtk.HSeparator()
        vertical_box_main.pack_start(separator, False, True, 0)
        separator.show()

        box2 = gtk.VBox(False, 10)
        box2.set_border_width(0)
        vertical_box_main.pack_start(box2, False, True, 0)
        box2.show()       
        
        window.show()

    def get_decimal_time(self):
        '''Puts hours minutes into a floating point so that the difference can easily
        be calculated.'''
        calcedTime = (int(time.strftime("%H")) + (float(time.strftime("%M")) / 60.0))
        theTime = time.strftime("%d %b %Y %I:%M%p")
        return calcedTime, theTime

    def punchIn(self, widget, data=""):
        timeDec, timeNow = self.get_decimal_time()
        punchTime = "Clock In:  %s  #%2.2f\n" % (timeNow, timeDec)
        try:
            timeFile = open(self.log_manager._get_file_name(), "a+r")
            lines = timeFile.readlines()
            lastLine = lines[len(lines)-1]
            checkPunchIn = lastLine.split(":")[0]
            timeFile.close()
            try:
                if checkPunchIn == "Clock In":
                    self.textbuffer.set_text("\nYou are already punched in!")
                else:
                    timeFile.close()               
                    timeFile = open(self.log_manager._get_file_name(), "a+r")
                    timeFile.writelines(punchTime)
                    self.textbuffer.set_text(punchTime[:32])
            except NameError, nameerror:
                timeFile = open(self.log_manager._get_file_name(), "a+r")
                timeFile.writelines(punchTime)
                timeFile.close()
                self.textbuffer.set_text(punchTime[:32])
        except IOError, e:
            print str(e)
            pass
        
    def punchOut(self, widget, data=""):
        timeDec, timeNow = self.get_decimal_time()
        punchTime = "Clock Out: %s  #%2.2f\n" % (timeNow, timeDec)
        try:
            timeFile = open(self.log_manager._get_file_name(), "a+r")
            lines = timeFile.readlines()
            lastLine = lines[len(lines)-1]
            checkPunchIn = lastLine.split(":")[0]
            timeFile.close()
            if checkPunchIn != 'Clock Out':
                timeFile.close()               
                timeFile = open(self.log_manager._get_file_name(), "a+r")
                timeFile.writelines(punchTime)
                self.textbuffer.set_text(punchTime[:32])
            elif checkPunchIn == "Clock Out":
                self.textbuffer.set_text("\nYou are already punched out!")
        except IOError:
            pass

    def showPunches(self, widget, data=""):
        string = ""
        try:
            timeFile = open(self.log_manager._get_file_name(), "a+r")
            if timeFile:
                punchesList = [(line.strip().split("#")[0]) for line in timeFile]
                for index in punchesList:
                    string = string + index.strip() + "\n"
                    timeFile.close()
                    self.textbuffer.set_text(string)
        except IOError:
            ioError = "\nThere was no time file for this week.\nPlease punch in to create a new file."
            self.textbuffer.set_text(ioError)

    def calculateTime(self, widget, data=""):
        totalHours = 0
        try:
            timeFile = open(self.log_manager._get_file_name(), "a+r")
            calcList = []
            for line in timeFile:
                try:
                    calcList.append(float(line.strip().split("#")[1]))
                except IndexError:
                    pass
            if len(calcList) % 2 == 0:
                totalHours = sum([-(calcList[x] - calcList[x+1]) for x in range(0,len(calcList),2)])
                string = "Total Hours: %2.1f\n" % totalHours
            else:
                totalHours = sum([-(calcList[x] - calcList[x+1]) for x in range(0,(len(calcList)-1),2)])
                string = "\nMissing Punches\nTotal Hours: %2.1f" % totalHours
            timeFile.close()        
            self.textbuffer.set_text(string)
        except IOError:
            string = "\nThere was no time file for this week.\nPlease punch in to create a new file."
            self.textbuffer.set_text(string)

    def aboutMenu(self, w, data):
        self.textbuffer.set_text(self.ABOUT)

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

#def main():
#    gtk.main()
#    return 0       
#
#if __name__ == "__main__":
#    TimeClock()
#    main()