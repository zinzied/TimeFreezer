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
            try:
                hBase = winreg.OpenKey(root, base_path, 0, winreg.KEY_READ)
                i = 0
                while True:
                    try:
                        subkey_name = winreg.EnumKey(hBase, i)
                        full_path = f"{base_path}\{subkey_name}"
                        
                        # Match app name (case insensitive)
                        if self.app_name.lower() in subkey_name.lower():
                            if scan_only:
                                self.log(f"[FOUND] Registry Key: {full_path}")
                            else:
                                self.delete_key_recursive(root, full_path)
                                self.log(f"Deleted Registry Key: {full_path}")
                                # Since we deleted, the index shifts, don't increment i
                                continue
                        i += 1
                    except OSError:
                        break
                winreg.CloseKey(hBase)
            except FileNotFoundError:
                pass
            except Exception as e:
                self.log(f"Error accessing base registry path {base_path}: {e}")

    def reset_files(self, scan_only=False):
        """Deletes AppData and LocalAppData folders."""
        base_folders = [
            os.environ.get('APPDATA', ''),
            os.environ.get('LOCALAPPDATA', ''),
            os.environ.get('PROGRAMDATA', 'C:\ProgramData')
        ]
        
        for base_folder in base_folders:
            if not base_folder or not os.path.exists(base_folder):
                continue
                
            try:
                for entry in os.listdir(base_folder):
                    full_path = os.path.join(base_folder, entry)
                    if os.path.isdir(full_path) and self.app_name.lower() in entry.lower():
                        if scan_only:
                            self.log(f"[FOUND] Folder: {full_path}")
                        else:
                            try:
                                shutil.rmtree(full_path)
                                self.log(f"Deleted Folder: {full_path}")
                            except Exception as e:
                                self.log(f"Error deleting folder {full_path}: {e}")
            except Exception as e:
                self.log(f"Error scanning base folder {base_folder}: {e}")

    def run_full_reset(self, deep_scan=False, lock=False, scan_only=False):
        self.log(f"{'Scanning' if scan_only else 'Starting reset'} for: {self.app_name}")
        self.reset_registry(scan_only=scan_only)
        self.reset_files(scan_only=scan_only)
        
        if deep_scan or lock:
            self.log("Running deep heuristic scan for trial keys...")
            scanner = RegistryScanner()
            found_keys = scanner.scan_clsid_keys()
            
            # If deep scan, also scan for trial keywords that match the app name
            if deep_scan:
                keyword_keys = scanner.scan_trial_keywords()
                # Only keep those that also mention the app name
                filtered_keywords = [k for k in keyword_keys if self.app_name.lower() in k[1].lower()]
                found_keys.extend(filtered_keywords)

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
