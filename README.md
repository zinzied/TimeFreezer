![TimeFreezer Pro](./assets/timefreezer_banner.png)

# TimeFreezer Pro

**TimeFreezer Pro** is a powerful Windows utility designed to help users manage trial software effortlessly. It provides two primary methods for bypassing trial limitations: a non-destructive **Time Freeze** and a comprehensive **Deep Trial Reset**.

---

## 🚀 Key Features

### ⏳ Time Freeze
Launch any application with a "frozen" system clock. 
- **Temporary Clock Shift**: The app changes the system date right before launching the target executable.
- **Auto-Restoration**: Once the target app is initialized, TimeFreezer automatically restores the system clock to the current real time.
- **Stealth Preservation**: Bypasses many "first run" date checks without permanently altering your system settings.

### 🧹 Deep Trial Reset
For software that leaves persistent traces in your system, the Trial Reset feature performs a surgical cleanup.
- **Registry Scrubbing**: Scans and removes trial-related keys from `HKEY_CURRENT_USER` and `HKEY_LOCAL_MACHINE`.
- **Folder Cleanup**: Automatically detects and deletes hidden trial data in `AppData`, `LocalAppData`, and `ProgramData`.
- **Intelligent Discovery**: Extract app names directly from executable paths for precise targeting.

---

## 🛠️ Installation

### 1. Prerequisites
Ensure you have **Python 3.8+** installed on your Windows system.

### 2. Install Dependencies
Run the following command to install the required libraries:
```powershell
pip install customtkinter tkcalendar pywin32
```

### 3. Run the Application
Start the program with Administrator privileges (it will request them automatically if not provided):
```powershell
python main.py
```

---

## 🖥️ Usage Guide

1. **Select Mode**: Use the sidebar to switch between **Time Freeze** and **Trial Reset**.
2. **Choose Target**: 
   - For **Time Freeze**, browse for the `.exe` of the application you want to launch.
   - For **Trial Reset**, enter the application name or browse to let the tool identify it for you.
3. **Configure**:
   - Set the **Target Freeze Date** using the integrated calendar.
4. **Execute**: Click the prominent **LAUNCH** or **RESET** button to begin the process.

---

## 🛑 Disclaimer

> [!WARNING]
> **Education and Recovery Only**: This tool is provided for educational purposes and for recovering access to your own data or testing software compatibility. Using this tool to bypass commercial licensing agreements may violate the Terms of Service of software providers. The authors are not responsible for any misuse of this software.

---

## 🧬 Tech Stack
- **Language**: Python
- **GUI Framework**: [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
- **Time/Registry Ops**: `pywin32` (win32api, winreg)
- **UI Components**: `tkcalendar`

---
*Created with ❤️ for efficient software management.*
