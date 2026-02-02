import os
import time
import subprocess
import win32api
import win32security
import ntsecuritycon as con
from datetime import datetime

class TimeFreezer:
    def __init__(self, target_exe, target_date_str):
        self.target_exe = target_exe
        self.target_date = datetime.strptime(target_date_str, "%Y-%m-%d")
        self.original_time = None

    def enable_time_privilege(self):
        """Enables the privilege to change system time."""
        hToken = win32security.OpenProcessToken(win32api.GetCurrentProcess(),
                                                win32security.TOKEN_ADJUST_PRIVILEGES | win32security.TOKEN_QUERY)
        id = win32security.LookupPrivilegeValue(None, win32security.SE_SYSTEMTIME_NAME)
        win32security.AdjustTokenPrivileges(hToken, 0, [(id, win32security.SE_PRIVILEGE_ENABLED)])

    def set_system_time(self, new_date):
        """Sets the system time (Requires Admin)."""
        # Format for SetSystemTime: (Year, Month, DayOfWeek, Day, Hour, Minute, Second, Milliseconds)
        # We'll keep the current time portion but change the date
        current = datetime.now()
        time_tuple = (new_date.year, new_date.month, 0, new_date.day, 
                      current.hour, current.minute, current.second, 0)
        win32api.SetSystemTime(*time_tuple)

    def launch(self, delay=5):
        """
        Temporarily changes time, launches exe, and restores time.
        """
        try:
            self.enable_time_privilege()
            self.original_time = datetime.now()
            
            print(f"Bypassing trial... temporarily setting date to {self.target_date.date()}")
            self.set_system_time(self.target_date)
            
            # Launch process
            print(f"Launching {self.target_exe}...")
            # Use subprocess.Popen so we don't block
            subprocess.Popen([self.target_exe], cwd=os.path.dirname(self.target_exe))
            
            print(f"Waiting {delay} seconds for initialization...")
            time.sleep(delay)
            
        except Exception as e:
            print(f"An error occurred: {e}")
            if "privelege" in str(e).lower():
                print("Tip: Run as Administrator to allow time changes.")
        finally:
            if self.original_time:
                try:
                    print("Restoring system time...")
                    self.set_system_time(self.original_time)
                    print("Done.")
                except Exception as e:
                    print(f"Warning: Could not restore system time. Error: {e}")

if __name__ == "__main__":
    # Example usage (must be admin)
    # freezer = TimeFreezer("C:\\Windows\\System32\\notepad.exe", "2020-01-01")
    # freezer.launch()
    pass
