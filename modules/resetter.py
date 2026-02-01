import winreg
import os
import shutil
import pathlib
from modules.registry_scanner import RegistryScanner
from core.win_utils import WinUtils

class TrialResetter:
    def __init__(self, app_name):
        self.app_name = app_name
        self.logs = []

    def log(self, message):
        self.logs.append(message)
        print(message)

    def delete_key_recursive(self, key, subkey):
        """Recursively deletes a registry key and all its subkeys."""
        try:
            hKey = winreg.OpenKey(key, subkey, 0, winreg.KEY_ALL_ACCESS)
        except FileNotFoundError:
            return

        while True:
            try:
                # Always delete the first child until none are left
                child = winreg.EnumKey(hKey, 0)
                self.delete_key_recursive(hKey, child)
            except OSError:
                break
        
        winreg.CloseKey(hKey)
        winreg.DeleteKey(key, subkey)

    def reset_registry(self):
        """Attempts to delete registry keys associated with the app name recursively."""
        locations = [
            (winreg.HKEY_CURRENT_USER, r"Software"),
            (winreg.HKEY_LOCAL_MACHINE, r"Software"),
            (winreg.HKEY_CURRENT_USER, r"Software\Classes\VirtualStore\MACHINE\SOFTWARE")
        ]
        
        for root, base_path in locations:
            path = f"{base_path}\\{self.app_name}"
            try:
                self.delete_key_recursive(root, path)
                self.log(f"Deleted Registry Key: {path}")
            except FileNotFoundError:
                pass
            except Exception as e:
                self.log(f"Error deleting registry key {path}: {e}")

    def reset_files(self):
        """Deletes AppData and LocalAppData folders."""
        folders = [
            os.path.join(os.environ.get('APPDATA', ''), self.app_name),
            os.path.join(os.environ.get('LOCALAPPDATA', ''), self.app_name),
            os.path.join(os.environ.get('PROGRAMDATA', 'C:\\ProgramData'), self.app_name)
        ]
        
        for folder in folders:
            if os.path.exists(folder):
                try:
                    shutil.rmtree(folder)
                    self.log(f"Deleted Folder: {folder}")
                except Exception as e:
                    self.log(f"Error deleting folder {folder}: {e}")

    def run_full_reset(self, deep_scan=False):
        self.log(f"Starting reset for: {self.app_name}")
        self.reset_registry()
        self.reset_files()
        
        if deep_scan:
            self.log("Running deep heuristic scan for trial keys...")
            scanner = RegistryScanner()
            keys = scanner.scan_clsid_keys()
            for root, path in keys:
                try:
                    self.delete_key_recursive(root, path)
                    self.log(f"Heuristic Match Removed: {path}")
                except Exception as e:
                    self.log(f"Failed to remove heuristic match {path}: {e}")
                    
        self.log("Reset process completed.")
        return self.logs

if __name__ == "__main__":
    # Test with a dummy name
    resetter = TrialResetter("NonExistentTestApp")
    resetter.run_full_reset()
