import winreg
import os
import shutil
import pathlib
from modules.registry_scanner import RegistryScanner
from core.win_utils import WinUtils

class TrialResetter:
    def __init__(self, app_name, log_callback=None):
        self.app_name = app_name
        self.logs = []
        self.log_callback = log_callback

    def log(self, message):
        self.logs.append(message)
        if self.log_callback:
            self.log_callback(message)
        print(message)

    def delete_key_recursive(self, key, subkey):
        """Recursively deletes a registry key and all its subkeys."""
        try:
            hKey = winreg.OpenKey(key, subkey, 0, winreg.KEY_ALL_ACCESS)
        except FileNotFoundError:
            return

        while True:
            try:
                child = winreg.EnumKey(hKey, 0)
                self.delete_key_recursive(hKey, child)
            except OSError:
                break
        
        winreg.CloseKey(hKey)
        winreg.DeleteKey(key, subkey)

    def reset_registry(self, scan_only=False):
        """Attempts to delete registry keys associated with the app name recursively."""
        locations = [
            (winreg.HKEY_CURRENT_USER, r"Software"),
            (winreg.HKEY_LOCAL_MACHINE, r"Software"),
            (winreg.HKEY_CURRENT_USER, r"Software\Classes\VirtualStore\MACHINE\SOFTWARE")
        ]
        
        for root, base_path in locations:
            path = f"{base_path}\{self.app_name}"
            try:
                # Check if exists
                hKey = winreg.OpenKey(root, path)
                winreg.CloseKey(hKey)
                if scan_only:
                    self.log(f"[FOUND] Registry Key: {path}")
                else:
                    self.delete_key_recursive(root, path)
                    self.log(f"Deleted Registry Key: {path}")
            except FileNotFoundError:
                pass
            except Exception as e:
                self.log(f"Error accessing registry key {path}: {e}")

    def reset_files(self, scan_only=False):
        """Deletes AppData and LocalAppData folders."""
        folders = [
            os.path.join(os.environ.get('APPDATA', ''), self.app_name),
            os.path.join(os.environ.get('LOCALAPPDATA', ''), self.app_name),
            os.path.join(os.environ.get('PROGRAMDATA', 'C:\ProgramData'), self.app_name)
        ]
        
        for folder in folders:
            if os.path.exists(folder):
                if scan_only:
                    self.log(f"[FOUND] Folder: {folder}")
                else:
                    try:
                        shutil.rmtree(folder)
                        self.log(f"Deleted Folder: {folder}")
                    except Exception as e:
                        self.log(f"Error deleting folder {folder}: {e}")

    def run_full_reset(self, deep_scan=False, lock=False, scan_only=False):
        self.log(f"{'Scanning' if scan_only else 'Starting reset'} for: {self.app_name}")
        self.reset_registry(scan_only=scan_only)
        self.reset_files(scan_only=scan_only)
        
        if deep_scan or lock:
            self.log("Running deep heuristic scan for trial keys...")
            scanner = RegistryScanner()
            found_keys = scanner.scan_clsid_keys()

            if scan_only:
                for root, path in found_keys:
                    self.log(f"[FOUND] Heuristic Match: {path}")
            else:
                if deep_scan:
                    for root, path in found_keys:
                        try:
                            self.delete_key_recursive(root, path)
                            self.log(f"Heuristic Match Removed: {path}")
                        except Exception as e:
                            self.log(f"Failed to remove heuristic match {path}: {e}")
                
                if lock:
                    self.log("Applying permanent registry lock to trial markers...")
                    for root, path in found_keys:
                        if WinUtils.set_registry_lock(root, path, lock=True):
                            self.log(f"Locked Key: {path}")
                        else:
                            self.log(f"Failed to lock key: {path}")
                    
        self.log(f"{'Scan' if scan_only else 'Reset'} process completed.")
        return self.logs
