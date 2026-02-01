import customtkinter as ctk
import os
import threading
from tkinter import filedialog, messagebox
from tkcalendar import DateEntry
from core.history_manager import HistoryManager
from core.win_utils import WinUtils
from modules.freezer import TimeFreezer
from modules.resetter import TrialResetter

class TimeFreezerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("TimeFreezer Pro - Premium Trial Management")
        self.geometry("900x650")

        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        self.history_manager = HistoryManager()
        self.history = self.history_manager.load_history()

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar_frame = ctk.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=2, sticky="nsew")

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="TimeFreezer", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.pack(pady=20)

        self.btn_freeze = ctk.CTkButton(self.sidebar_frame, text="Time Freeze", command=self.show_freeze_tab)
        self.btn_freeze.pack(pady=10, padx=20)

        self.btn_reset = ctk.CTkButton(self.sidebar_frame, text="Trial Reset", command=self.show_reset_tab)
        self.btn_reset.pack(pady=10, padx=20)

        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(0, weight=1)

        self.freeze_tab = self.create_freeze_tab()
        self.reset_tab = self.create_reset_tab()

        self.bottom_frame = ctk.CTkFrame(self, height=250)
        self.bottom_frame.grid(row=1, column=1, sticky="nsew", padx=20, pady=(0, 20))
        self.bottom_frame.grid_columnconfigure(0, weight=1)

        self.progress_bar = ctk.CTkProgressBar(self.bottom_frame)
        self.progress_bar.pack(fill="x", padx=20, pady=10)
        self.progress_bar.set(0)

        self.console = ctk.CTkTextbox(self.bottom_frame, height=150, font=("Consolas", 12))
        self.console.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        self.log("Welcome to TimeFreezer Pro. Ready.")

        self.show_freeze_tab()

    def log(self, message):
        self.console.insert("end", f"> {message}\n")
        self.console.see("end")

    def show_freeze_tab(self):
        self.reset_tab.grid_forget()
        self.freeze_tab.grid(row=0, column=0, sticky="nsew")

    def show_reset_tab(self):
        self.freeze_tab.grid_forget()
        self.reset_tab.grid(row=0, column=0, sticky="nsew")

    def create_freeze_tab(self):
        frame = ctk.CTkFrame(self.main_container, fg_color="transparent")

        ctk.CTkLabel(frame, text="Freeze Application Date", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=10)

        self.freeze_exe_path = ctk.StringVar(value="No file selected")
        ctk.CTkLabel(frame, textvariable=self.freeze_exe_path, wraplength=500).pack(pady=5)

        ctk.CTkButton(frame, text="Select .exe", command=self.select_freeze_exe).pack(pady=5)

        ctk.CTkLabel(frame, text="Target Freeze Date:").pack(pady=(10, 0))
        self.date_picker = DateEntry(frame, width=12, background="#1f538d", foreground="white", borderwidth=2, date_pattern="yyyy-mm-dd")
        self.date_picker.pack(pady=5)

        self.freeze_lock_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(frame, text="Use Registry Lock (Hard Freeze)", variable=self.freeze_lock_var).pack(pady=5)

        ctk.CTkLabel(frame, text="History:").pack(pady=(10, 0))
        self.freeze_history_menu = ctk.CTkOptionMenu(frame, values=self.get_history_list("Freeze"), command=self.load_freeze_history, width=300)
        self.freeze_history_menu.set("Recent History")
        self.freeze_history_menu.pack(pady=5)

        ctk.CTkButton(frame, text="LAUNCH WITH FROZEN TIME", fg_color="#1f538d", hover_color="#14375e", command=self.run_freeze).pack(pady=20)

        return frame

    def create_reset_tab(self):
        frame = ctk.CTkFrame(self.main_container, fg_color="transparent")

        ctk.CTkLabel(frame, text="Deep Trial Reset", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=10)

        self.reset_app_name = ctk.CTkEntry(frame, placeholder_text="App Name (e.g. Photoshop)", width=300)
        self.reset_app_name.pack(pady=10)

        ctk.CTkButton(frame, text="Auto-Detect from .exe", fg_color="#2c3e50", hover_color="#1a252f", command=self.detect_reset_app).pack(pady=5)

        self.reset_deep_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(frame, text="Deep Heuristic Scan", variable=self.reset_deep_var).pack(pady=5)

        self.reset_lock_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(frame, text="Lock Registry after Reset", variable=self.reset_lock_var).pack(pady=5)

        ctk.CTkLabel(frame, text="History:").pack(pady=(10, 0))
        self.reset_history_menu = ctk.CTkOptionMenu(frame, values=self.get_history_list("Reset"), command=self.load_reset_history, width=300)
        self.reset_history_menu.set("Recent History")
        self.reset_history_menu.pack(pady=5)

        btn_row = ctk.CTkFrame(frame, fg_color="transparent")
        btn_row.pack(pady=20)

        ctk.CTkButton(btn_row, text="SCAN ONLY", fg_color="#7f8c8d", hover_color="#636e72", width=140, command=lambda: self.run_reset(scan_only=True)).pack(side="left", padx=10)
        ctk.CTkButton(btn_row, text="FULL RESET", fg_color="#d35400", hover_color="#a04000", width=140, command=self.run_reset).pack(side="left", padx=10)

        return frame

    def get_history_list(self, mode):
        items = [f"{e['name']} ({e.get('date') or 'Reset'})" for e in self.history if e['mode'] == mode]
        base = ["Recent History", "Clear History"]
        if items:
            return base + ["---"] + items
        return base + ["No History"]

    def load_freeze_history(self, choice):
        if choice in ["Recent History", "Clear History", "---", "No History"]:
            if choice == "Clear History":
                self.history_manager.clear_history()
                self.refresh_ui()
            return
        for e in self.history:
            if e['mode'] == "Freeze" and choice.startswith(e['name']):
                self.freeze_exe_path.set(e['path'])
                self.date_picker.set_date(e['date'])
                break

    def load_reset_history(self, choice):
        if choice in ["Recent History", "Clear History", "---", "No History"]:
            if choice == "Clear History":
                self.history_manager.clear_history()
                self.refresh_ui()
            return
        for e in self.history:
            if e['mode'] == "Reset" and choice.startswith(e['name']):
                self.reset_app_name.delete(0, "end")
                self.reset_app_name.insert(0, e['name'])
                break

    def refresh_ui(self):
        self.history = self.history_manager.load_history()
        self.freeze_history_menu.configure(values=self.get_history_list("Freeze"))
        self.freeze_history_menu.set("Recent History")
        self.reset_history_menu.configure(values=self.get_history_list("Reset"))
        self.reset_history_menu.set("Recent History")

    def select_freeze_exe(self):
        path = filedialog.askopenfilename(filetypes=[("EXE", "*.exe")])
        if path:
            self.freeze_exe_path.set(path)

    def detect_reset_app(self):
        path = filedialog.askopenfilename(filetypes=[("EXE", "*.exe")])
        if path:
            self.log(f"Extracting metadata from {os.path.basename(path)}...")
            info = WinUtils.get_exe_info(path)
            if info and info["ProductName"]:
                name = info["ProductName"]
                self.log(f"Detected: {name}")
            else:
                name = os.path.basename(os.path.dirname(path))
                self.log(f"Metadata not found. Using folder name: {name}")

            self.reset_app_name.delete(0, "end")
            self.reset_app_name.insert(0, name)

    def run_freeze(self):
        exe = self.freeze_exe_path.get()
        date = self.date_picker.get()
        if exe == "No file selected":
            messagebox.showerror("Error", "Please select an EXE and enter a date.")
            return

        self.progress_bar.set(0)
        self.progress_bar.start()

        def task():
            try:
                freezer = TimeFreezer(exe, date, log_callback=self.log)
                freezer.launch(lock_registry=self.freeze_lock_var.get())
                self.history_manager.add_entry("Freeze", os.path.basename(exe), exe, date)
            except Exception as e:
                self.log(f"ERROR: {e}")
            self.after(0, self.finish_task)

        threading.Thread(target=task, daemon=True).start()

    def run_reset(self, scan_only=False):
        name = self.reset_app_name.get()
        if not name:
            messagebox.showerror("Error", "Please enter the application name.")
            return

        if not scan_only and not messagebox.askyesno("Confirm", f"Perform full reset for {name}?"):
            return

        self.progress_bar.set(0)
        self.progress_bar.start()

        def task():
            try:
                resetter = TrialResetter(name, log_callback=self.log)
                resetter.run_full_reset(
                    deep_scan=self.reset_deep_var.get(),
                    lock=self.reset_lock_var.get(),
                    scan_only=scan_only
                )
                if not scan_only:
                    self.history_manager.add_entry("Reset", name)
            except Exception as e:
                self.log(f"ERROR: {e}")
            self.after(0, self.finish_task)

        threading.Thread(target=task, daemon=True).start()

    def finish_task(self):
        self.progress_bar.stop()
        self.progress_bar.set(1)
        self.refresh_ui()
        messagebox.showinfo("Done", "Operation completed.")

if __name__ == "__main__":
    app = TimeFreezerApp()
    app.mainloop()
