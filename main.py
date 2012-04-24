import pygtk
import sys
if not sys.platform == 'win32':
    pygtk.require('2.0')
import gtk
from timeclock import TimeClock

def main():
    gtk.main()
    return 0       

if __name__ == "__main__":
    TimeClock()
    main()