import winreg
import re

class RegistryScanner:
    def __init__(self):
        # Common GUID pattern
        self.guid_pattern = re.compile(r'^\{[A-F0-9]{8}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{12}\}$')
        self.exclude_subkeys = ["LocalServer32", "InProcServer32", "InProcHandler32"]
        self.trial_value_patterns = ["MData", "Model", "scansk", "Therad"]

    def scan_clsid_keys(self):
        """Scans for potential trial tracking keys in HKCU classes."""
        found_keys = []
        # Areas to scan
        scan_paths = [
            (winreg.HKEY_CURRENT_USER, r"Software\Classes\CLSID"),
            (winreg.HKEY_CURRENT_USER, r"Software\Classes\Wow6432Node\CLSID")
        ]

        for root, base_path in scan_paths:
            try:
                hKey = winreg.OpenKey(root, base_path)
            except FileNotFoundError:
                continue

            # Enumerate all subkeys
            i = 0
            while True:
                try:
                    name = winreg.EnumKey(hKey, i)
                    i += 1
                    
                    if not self.guid_pattern.match(name.upper()):
                        continue
                    
                    full_path = f"{base_path}\\{name}"
                    if self._is_trial_key(root, full_path):
                        found_keys.append((root, full_path))
                except OSError:
                    break
            winreg.CloseKey(hKey)
            
        return found_keys

    def scan_trial_keywords(self):
        """Scans Software keys for trial keywords."""
        found_keys = []
        locations = [
            (winreg.HKEY_CURRENT_USER, r"Software"),
            (winreg.HKEY_LOCAL_MACHINE, r"Software")
        ]
        keywords = ["trial", "license", "activation", "registration", "expired", "period"]
        
        for root, base_path in locations:
            try:
                hBase = winreg.OpenKey(root, base_path, 0, winreg.KEY_READ)
                i = 0
                while True:
                    try:
                        subkey_name = winreg.EnumKey(hBase, i)
                        full_path = f"{base_path}\{subkey_name}"
                        if any(kw in subkey_name.lower() for kw in keywords):
                            found_keys.append((root, full_path))
                        i += 1
                    except OSError:
                        break
                winreg.CloseKey(hBase)
            except Exception:
                pass
        return found_keys

    def _is_trial_key(self, root, path):
        """Heuristic check for trial tracking keys based on zied.cmd logic."""
        try:
            hKey = winreg.OpenKey(root, path)
            
            # 1. Get subkey names
            subkeys = []
            j = 0
            while True:
                try:
                    subkeys.append(winreg.EnumKey(hKey, j))
                    j += 1
                except OSError:
                    break
            
            # Exclude keys that have standard COM subkeys
            if any(k in subkeys for k in self.exclude_subkeys):
                winreg.CloseKey(hKey)
                return False

            # 2. Get values
            values = {}
            k = 0
            while True:
                try:
                    v_name, v_val, v_type = winreg.EnumValue(hKey, k)
                    values[v_name] = v_val
                    k += 1
                except OSError:
                    break

            # Heuristic A: Empty key
            if not subkeys and not values:
                winreg.CloseKey(hKey)
                return True

            # Heuristic B: Default value exists and is just digits
            default_val = values.get('', None)
            if default_val and isinstance(default_val, str):
                if not subkeys and default_val.isdigit():
                    winreg.CloseKey(hKey)
                    return True
                # Heuristic C: Default value contains + or =
                if not subkeys and ('+' in default_val or '=' in default_val):
                    winreg.CloseKey(hKey)
                    return True

            # Heuristic D: Version subkey with numeric default
            if "Version" in subkeys and len(subkeys) == 1:
                try:
                    hVer = winreg.OpenKey(hKey, "Version")
                    ver_val, _ = winreg.QueryValueEx(hVer, "")
                    winreg.CloseKey(hVer)
                    if str(ver_val).isdigit():
                        winreg.CloseKey(hKey)
                        return True
                except:
                    pass

            # Heuristic E: Value name matches trial markers
            for v_name in values.keys():
                if any(p in v_name for p in self.trial_value_patterns):
                    winreg.CloseKey(hKey)
                    return True

            winreg.CloseKey(hKey)
        except Exception:
            pass
        return False
