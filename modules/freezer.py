import os
import time
import subprocess
import win32api
import win32security
import ntsecuritycon as con
from datetime import datetime
from core.win_utils import WinUtils
from modules.registry_scanner import RegistryScanner

class TimeFreezer:
    def __init__(self, target_exe, target_date_str, log_callback=None):
        self.target_exe = target_exe
        self.target_date = datetime.strptime(target_date_str, "%Y-%m-%d")
        self.original_time = None
        self.log_callback = log_callback

    def log(self, message):
        if self.log_callback:
            self.log_callback(message)
        print(message)

    def enable_time_privilege(self):
        """Enables the privilege to change system time."""
        hToken = win32security.OpenProcessToken(win32api.GetCurrentProcess(),
                                                win32security.TOKEN_ADJUST_PRIVILEGES | win32security.TOKEN_QUERY)
        id = win32security.LookupPrivilegeValue(None, win32security.SE_SYSTEMTIME_NAME)
        win32security.AdjustTokenPrivileges(hToken, 0, [(id, win32security.SE_PRIVILEGE_ENABLED)])

    def set_local_time(self, new_date):
        """Sets the system time (Requires Admin)."""
        current = datetime.now()
        # Windows SYSTEMTIME structure: (year, month, dayOfWeek, day, hour, minute, second, millisecond)
        time_tuple = (new_date.year, new_date.month, 0, new_date.day, 
                      current.hour, current.minute, current.second, 0)
        win32api.SetLocalTime(*time_tuple)

    def launch(self, delay=5, lock_registry=False):
        try:
            self.enable_time_privilege()
            self.original_time = datetime.now()
            
            if lock_registry:
                self.log("Protecting registry trial keys...")
                scanner = RegistryScanner()
                keys = scanner.scan_clsid_keys()
                for root, path in keys:
                    WinUtils.set_registry_lock(root, path, lock=True)
                self.log(f"Locked {len(keys)} potential trial keys.")

            self.log(f"Bypassing trial... temporarily setting date to {self.target_date.date()}")
            self.set_local_time(self.target_date)
            
            self.log(f"Launching {self.target_exe}...")
            subprocess.Popen([self.target_exe], cwd=os.path.dirname(self.target_exe))
            
            self.log(f"Waiting {delay} seconds for initialization...")
            time.sleep(delay)
            
        except Exception as e:
            self.log(f"An error occurred: {e}")
        finally:
            if self.original_time:
                try:
                    self.log("Restoring system time...")
                    self.set_local_time(self.original_time)
                    self.log("Time restored.")
                except Exception as e:
                    self.log(f"Warning: Could not restore system time. Error: {e}")
