import winreg
import os
import shutil
import pathlib

class TrialResetter:
    def __init__(self, app_name):
        self.app_name = app_name
        self.logs = []

    def log(self, message):
        self.logs.append(message)
        print(message)

    def reset_registry(self):
        """Attempts to delete registry keys associated with the app name."""
        locations = [
            (winreg.HKEY_CURRENT_USER, r"Software"),
            (winreg.HKEY_LOCAL_MACHINE, r"Software"),
            (winreg.HKEY_CURRENT_USER, r"Software\Classes\VirtualStore\MACHINE\SOFTWARE")
        ]
        
        for root, base_path in locations:
            try:
                path = f"{base_path}\\{self.app_name}"
                winreg.DeleteKey(root, path)
                self.log(f"Deleted Registry Key: {path}")
            except FileNotFoundError:
                pass
            except Exception as e:
                self.log(f"Error deleting registry key {base_path}\\{self.app_name}: {e}")

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

    def run_full_reset(self):
        self.log(f"Starting reset for: {self.app_name}")
        self.reset_registry()
        self.reset_files()
        self.log("Reset process completed.")
        return self.logs

if __name__ == "__main__":
    # Test with a dummy name
    resetter = TrialResetter("NonExistentTestApp")
    resetter.run_full_reset()
