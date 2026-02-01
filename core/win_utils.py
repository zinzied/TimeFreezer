import win32api
import win32security
import ntsecuritycon as con
import winreg
import win32con

class WinUtils:
    @staticmethod
    def enable_privileges():
        """Enables backup, restore, and ownership privileges."""
        privileges = [
            win32security.SE_BACKUP_NAME,
            win32security.SE_RESTORE_NAME,
            win32security.SE_TAKE_OWNERSHIP_NAME
        ]
        
        hToken = win32security.OpenProcessToken(
            win32api.GetCurrentProcess(),
            win32security.TOKEN_ADJUST_PRIVILEGES | win32security.TOKEN_QUERY
        )
        
        for priv in privileges:
            try:
                luid = win32security.LookupPrivilegeValue(None, priv)
                win32security.AdjustTokenPrivileges(hToken, 0, [(luid, win32security.SE_PRIVILEGE_ENABLED)])
            except Exception as e:
                print(f"Warning: Could not enable privilege {priv}: {e}")

    @staticmethod
    def take_ownership(handle):
        """Sets the owner of the given registry handle to the Administrators group."""
        try:
            admin_sid = win32security.CreateWellKnownSid(win32security.WinBuiltinAdministratorsSide)
            
            # Set the owner
            sd = win32security.GetSecurityInfo(handle, win32security.SE_REGISTRY_KEY, win32security.OWNER_SECURITY_INFORMATION)
            sd.SetSecurityDescriptorOwner(admin_sid, False)
            win32security.SetSecurityInfo(handle, win32security.SE_REGISTRY_KEY, win32security.OWNER_SECURITY_INFORMATION, admin_sid, None, None, None)
            return True
        except Exception as e:
            print(f"Failed to take ownership: {e}")
            return False

    @staticmethod
    def set_registry_lock(root_key, path, lock=True):
        """
        Locks or unlocks a registry key by modifying its ACL.
        If locked, 'Everyone' is denied FullControl.
        """
        WinUtils.enable_privileges()
        
        # Open the key for permission changes
        try:
            # We need to open it with WRITE_OWNER to change owner first, then change ACL
            hKey = win32api.RegOpenKeyEx(root_key, path, 0, con.WRITE_OWNER | con.WRITE_DAC | win32con.READ_CONTROL)
        except Exception as e:
            # If we fail to open, we might not have ownership
            try:
                hKey = win32api.RegOpenKeyEx(root_key, path, 0, win32con.READ_CONTROL)
            except:
                print(f"Could not open key {path} for locking: {e}")
                return False

        # Take ownership if we are locking
        if lock:
            WinUtils.take_ownership(hKey)

        # Create the ACL
        everyone_sid = win32security.CreateWellKnownSid(win32security.WinWorldSid)
        
        # Initialize an empty DACL
        dacl = win32security.ACL()
        
        if lock:
            # Add Deny ACE for Everyone
            # con.GENERIC_ALL covers FullControl
            dacl.AddAccessDeniedAce(win32security.ACL_REVISION, con.GENERIC_ALL, everyone_sid)
        else:
            # Add Allow ACE for Everyone (Reset to default-ish)
            dacl.AddAccessAllowedAce(win32security.ACL_REVISION, con.GENERIC_ALL, everyone_sid)

        # Apply the DACL
        try:
            win32security.SetSecurityInfo(hKey, win32security.SE_REGISTRY_KEY, win32security.DACL_SECURITY_INFORMATION, None, None, dacl, None)
            win32api.RegCloseKey(hKey)
            return True
        except Exception as e:
            print(f"Failed to set ACL for {path}: {e}")
            win32api.RegCloseKey(hKey)
            return False

    @staticmethod
    def get_exe_info(file_path):
        """Extracts Product Name and Company Name from an EXE file."""
        import os
        if not os.path.exists(file_path):
            return None
        
        try:
            # Get the size of the version info
            size = win32api.GetFileVersionInfoSize(file_path)
            if not size:
                return None
            
            # Get the translation list
            trans = win32api.GetFileVersionInfo(file_path, "\\VarFileInfo\\Translation")
            if not trans:
                return None
            
            lang, codepage = trans[0]
            
            # Format the string for querying
            str_info = u"\\StringFileInfo\\%04X%04X\\%s"
            
            def get_val(name):
                try:
                    return win32api.GetFileVersionInfo(file_path, str_info % (lang, codepage, name))
                except:
                    return None

            product_name = get_val("ProductName")
            company_name = get_val("CompanyName")
            
            return {
                "ProductName": product_name.strip() if product_name else None,
                "CompanyName": company_name.strip() if company_name else None
            }
        except Exception:
            return None
