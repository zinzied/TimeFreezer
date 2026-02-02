import customtkinter as ctk
import os
import threading
from tkinter import filedialog, messagebox
from tkcalendar import DateEntry
from core.history_manager import HistoryManager
from modules.freezer import TimeFreezer
from modules.resetter import TrialResetter

class TimeFreezerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("TimeFreezer Pro - Premium Trial Management")
        self.geometry("800x500")
        
        # Set appearance
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        # History Manager
        self.history_manager = HistoryManager()
        self.history = self.history_manager.load_history()

        # Create sidebar
        self.sidebar_frame = ctk.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="TimeFreezer", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        self.sidebar_button_1 = ctk.CTkButton(self.sidebar_frame, text="Time Freeze", command=self.show_freeze_tab)
        self.sidebar_button_1.grid(row=1, column=0, padx=20, pady=10)
        
        self.sidebar_button_2 = ctk.CTkButton(self.sidebar_frame, text="Trial Reset", command=self.show_reset_tab)
        self.sidebar_button_2.grid(row=2, column=0, padx=20, pady=10)

        # Main content area
        self.main_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.setup_freeze_tab()
        self.setup_reset_tab()
        
        self.show_freeze_tab()

    def setup_freeze_tab(self):
        self.freeze_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        
        label = ctk.CTkLabel(self.freeze_frame, text="Freeze Application Date", font=ctk.CTkFont(size=24, weight="bold"))
        label.pack(pady=20)
        
        self.exe_path_var = ctk.StringVar(value="No file selected")
        self.exe_label = ctk.CTkLabel(self.freeze_frame, textvariable=self.exe_path_var)
        self.exe_label.pack(pady=5)
        
        self.select_button = ctk.CTkButton(self.freeze_frame, text="Select .exe", command=self.select_exe)
        self.select_button.pack(pady=10)
        
        # Calendar Label
        self.cal_label = ctk.CTkLabel(self.freeze_frame, text="Target Freeze Date:")
        self.cal_label.pack(pady=(10, 0))
        
        # DateEntry with custom styling to match dark theme
        self.date_picker = DateEntry(self.freeze_frame, width=12, background='#1f538d', 
                                     foreground='white', borderwidth=2, 
                                     date_pattern='yyyy-mm-dd')
        self.date_picker.pack(pady=10)
        
        # History Dropdown for Freeze
        self.freeze_history_var = ctk.StringVar(value="Recent History")
        self.freeze_history_dropdown = ctk.CTkComboBox(self.freeze_frame, 
                                                       values=self.get_history_values("Freeze"),
                                                       variable=self.freeze_history_var,
                                                       command=self.load_from_freeze_history,
                                                       width=300)
        self.freeze_history_dropdown.pack(pady=10)

        self.launch_button = ctk.CTkButton(self.freeze_frame, text="LAUNCH WITH FROZEN TIME", 
                                           fg_color="#1f538d", hover_color="#14375e", command=self.run_freeze)
        self.launch_button.pack(pady=20)
        
        self.status_label = ctk.CTkLabel(self.freeze_frame, text="", text_color="gray")
        self.status_label.pack(pady=10)
        
        # New: Path Hint Label
        self.hint_label = ctk.CTkLabel(self.freeze_frame, 
                                       text="💡 Tip: Look in 'C:\\Program Files' for the app's .exe.\n'ProgramData' usually only contains trial data files.",
                                       text_color="#3498db", font=ctk.CTkFont(size=12))
        self.hint_label.pack(pady=10)

    def setup_reset_tab(self):
        self.reset_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        
        label = ctk.CTkLabel(self.reset_frame, text="Deep Trial Reset", font=ctk.CTkFont(size=24, weight="bold"))
        label.pack(pady=20)
        
        # App name entry
        self.app_name_entry = ctk.CTkEntry(self.reset_frame, placeholder_text="Enter App Name (e.g. Photoshop)", width=300)
        self.app_name_entry.pack(pady=10)
        
        # Browse button
        self.reset_browse_button = ctk.CTkButton(self.reset_frame, text="Or Browse for .exe", 
                                                  fg_color="#2c3e50", hover_color="#1a252f", command=self.browse_reset_exe)
        self.reset_browse_button.pack(pady=5)
        
        # History Dropdown for Reset
        self.reset_history_var = ctk.StringVar(value="Recent History")
        self.reset_history_dropdown = ctk.CTkComboBox(self.reset_frame, 
                                                      values=self.get_history_values("Reset"),
                                                      variable=self.reset_history_var,
                                                      command=self.load_from_reset_history,
                                                      width=300)
        self.reset_history_dropdown.pack(pady=10)

        self.scan_button = ctk.CTkButton(self.reset_frame, text="SCAN & RESET APP", 
                                         fg_color="#d35400", hover_color="#a04000", command=self.run_reset)
        self.scan_button.pack(pady=20)
        
        self.reset_status = ctk.CTkTextbox(self.reset_frame, height=150, width=500)
        self.reset_status.pack(pady=10)


    def show_freeze_tab(self):
        self.reset_frame.pack_forget()
        self.freeze_frame.pack(fill="both", expand=True)

    def show_reset_tab(self):
        self.freeze_frame.pack_forget()
        self.reset_frame.pack(fill="both", expand=True)

    def select_exe(self):
        # Default to Program Files if possible
        init_dir = "C:\\Program Files (x86)" if os.path.exists("C:\\Program Files (x86)") else "C:\\Program Files"
        
        filename = filedialog.askopenfilename(
            title="Select Application Executable",
            initialdir=init_dir,
            filetypes=[("Executable files", "*.exe"), ("All Files", "*.*")]
        )
        if filename:
            self.exe_path_var.set(filename)

    def browse_reset_exe(self):
        """Browse for an .exe file and extract the app name from the folder."""
        init_dir = "C:\\Program Files (x86)" if os.path.exists("C:\\Program Files (x86)") else "C:\\Program Files"
        
        filename = filedialog.askopenfilename(
            title="Select Application Executable",
            initialdir=init_dir,
            filetypes=[("Executable files", "*.exe"), ("All Files", "*.*")]
        )
        if filename:
            # Extract the folder name as the app name (e.g., "Internet Download Manager" from the path)
            folder_name = os.path.basename(os.path.dirname(filename))
            self.app_name_entry.delete(0, "end")
            self.app_name_entry.insert(0, folder_name)

    def get_history_values(self, mode):
        filtered = [f"{e['name']} ({e['date'] or e['path']})" for e in self.history if e['mode'] == mode]
        return ["Recent History"] + filtered

    def load_from_freeze_history(self, choice):
        if choice == "Recent History": return
        # Find entry
        for e in self.history:
            if e['mode'] == "Freeze" and choice.startswith(e['name']):
                self.exe_path_var.set(e['path'])
                self.date_picker.set_date(e['date'])
                break

    def load_from_reset_history(self, choice):
        if choice == "Recent History": return
        for e in self.history:
            if e['mode'] == "Reset" and choice.startswith(e['name']):
                self.app_name_entry.delete(0, "end")
                self.app_name_entry.insert(0, e['name'])
                break

    def refresh_history_ui(self):
        self.history = self.history_manager.load_history()
        self.freeze_history_dropdown.configure(values=self.get_history_values("Freeze"))
        self.freeze_history_var.set("Recent History")
        self.reset_history_dropdown.configure(values=self.get_history_values("Reset"))
        self.reset_history_var.set("Recent History")

    def run_freeze(self):

        exe = self.exe_path_var.get()
        date_str = self.date_picker.get()
        
        if exe == "No file selected" or not date_str:
            messagebox.showerror("Error", "Please select an EXE and enter a date.")
            return

        def task():
            self.status_label.configure(text="Processing... Please wait.")
            freezer = TimeFreezer(exe, date_str)
            freezer.launch()
            # Save to history
            app_name = os.path.basename(exe)
            self.history_manager.add_entry("Freeze", app_name, exe, date_str)
            self.after(0, self.refresh_history_ui)
            
            self.status_label.configure(text="Process launched and time restored.")
            messagebox.showinfo("Success", "Application launched successfully!")

        threading.Thread(target=task).start()

    def run_reset(self):
        app_name = self.app_name_entry.get()
        if not app_name:
            messagebox.showerror("Error", "Please enter the application name.")
            return
        
        if messagebox.askyesno("Confirm Reset", f"Are you sure you want to reset all data for '{app_name}'? \nThis action cannot be undone."):
            self.reset_status.delete("1.0", "end")
            resetter = TrialResetter(app_name)
            logs = resetter.run_full_reset()
            # Save to history
            self.history_manager.add_entry("Reset", app_name)
            self.refresh_history_ui()
            
            for log in logs:
                self.reset_status.insert("end", log + "\n")
            messagebox.showinfo("Reset Complete", "The application trial reset has finished.")

if __name__ == "__main__":
    app = TimeFreezerApp()
    app.mainloop()
