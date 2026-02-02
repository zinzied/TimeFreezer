import json
import os

class HistoryManager:
    def __init__(self, filename="history.json"):
        # Put history file in the same directory as main.py
        self.filepath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), filename)
        self.max_entries = 10

    def load_history(self):
        if not os.path.exists(self.filepath):
            return []
        try:
            with open(self.filepath, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []

    def save_history(self, history):
        try:
            with open(self.filepath, 'w') as f:
                json.dump(history, f, indent=4)
        except IOError:
            print(f"Error: Could not save history to {self.filepath}")

    def add_entry(self, mode, name, path=None, date=None):
        history = self.load_history()
        
        # Define the entry
        new_entry = {
            "mode": mode,
            "name": name,
            "path": path,
            "date": date
        }

        # Check for duplicates and remove them (keep the newest)
        history = [e for e in history if not (e['mode'] == mode and e['name'] == name)]
        
        # Insert at the beginning
        history.insert(0, new_entry)
        
        # Limit size
        history = history[:self.max_entries]
        
        self.save_history(history)
        return history

    def clear_history(self):
        self.save_history([])
