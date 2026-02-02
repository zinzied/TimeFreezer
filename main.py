import sys
import ctypes
import os
import logging
from ui import TimeFreezerApp

# Set up logging to a file in the same directory
log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app_log.txt")
logging.basicConfig(filename=log_path, level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if __name__ == "__main__":
    logging.info("Application starting...")
    if is_admin():
        logging.info("Running with Admin privileges.")
        try:
            app = TimeFreezerApp()
            app.mainloop()
        except Exception as e:
            logging.error(f"UI Error: {e}")
    else:
        logging.info("Admin privileges not found. Requesting elevation...")
        # Re-run the program with admin rights
        # We use [sys.executable] + sys.argv to ensure we use the same python interpreter
        params = " ".join([f'"{arg}"' for arg in sys.argv])
        try:
            ret = ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
            if ret <= 32:
                logging.error(f"Elevation failed with code: {ret}")
            else:
                logging.info(f"Elevation request sent. ShellExecute return code: {ret}")
        except Exception as e:
            logging.error(f"Elevation Exception: {e}")
            print(f"Failed to elevate: {e}")
