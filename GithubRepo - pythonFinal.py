import subprocess
import sys
import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk
from datetime import datetime
import json
import os
import webbrowser
from win10toast import ToastNotifier

def install_missing_modules():
    required_modules = ["tkinter", "win10toast"]  # Ensure win10toast is installed
    for module in required_modules:
        try:
            __import__(module)  # Try importing the module
        except ImportError:
            print(f"Installing missing module: {module}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", module])

install_missing_modules()

toaster = ToastNotifier()

# Function to display Windows notifications
def show_notification(event):
    toaster.show_toast(
        "Calender Reminder",
        f"Event: {event['description']} at {event['time'].strftime('%I:%M %p')}",
        duration=10,  # Notification duration in seconds
        threaded=True  # Allows the notification to run in the background
    )

# Default settings
DEFAULT_EVENTS_FILE = "events.txt"
DEFAULT_GAP_DURATION = 15  # in minutes
DEFAULT_INFO = """Version: 1.0.6-PRE
Date Of Coded: 3-22-25
MWAI: True, With Human Configuration
(c)dxvProjects All Rights Are Faked.
Uploaded on github at *https://github.com/dxvC0des*
Contact Info: [REDACTED]
PRE_RELEASE BETA - Github Dist
"""

# Load the configuration from a file (if exists)
def load_config():
    if os.path.exists("config.json"):
        with open("config.json", "r") as file:
            config = json.load(file)
            return config
    return {
        "events_file": DEFAULT_EVENTS_FILE,
        "gap_duration": DEFAULT_GAP_DURATION,
        "info": DEFAULT_INFO,
    }

# Save the configuration to a file
def save_config(config):
    with open("config.json", "w") as file:
        json.dump(config, file)

# Load configuration settings
config = load_config()

events = []
user_preferences = {"preferred_time_window": (1, 12)}  # Prefer mornings for tasks (9 AM to 12 PM)
file_name = config["events_file"]  # File to store events
gap_duration = config["gap_duration"]  # Gap duration between events in minutes

class ScheduleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Scheduler@Work - V1.0.6-PRE")
        self.root.geometry("750x650")
        self.root.configure(bg="#f7f7f7")  # Light background color
        
        # Create a frame for the app info section at the top right
        self.info_frame = tk.Frame(self.root, bg="#f7f7f7")
        self.info_frame.grid(row=0, column=2, padx=20, pady=10, sticky="e")

        # App Info Button
        self.app_info_button = tk.Button(self.info_frame, text="App Info", command=self.show_app_info, font=("Arial", 12), bg="#2196F3", fg="white", relief="flat")
        self.app_info_button.grid(row=0, column=0, padx=10, pady=5)

        # Title Label
        self.title_label = tk.Label(root, text="Schedule Manager", font=("Helvetica", 18, "bold"), bg="#f7f7f7")
        self.title_label.grid(row=0, column=1, pady=20)

        # Event Entry
        self.event_label = tk.Label(root, text="Event Description:", font=("Arial", 12), bg="#f7f7f7")
        self.event_label.grid(row=1, column=0, padx=20, pady=10, sticky="e")
        self.event_entry = tk.Entry(root, width=30, font=("Arial", 12))
        self.event_entry.grid(row=1, column=1, pady=10)

        # Time Entry
        self.time_label = tk.Label(root, text="Event Time (HH:MM):", font=("Arial", 12), bg="#f7f7f7")
        self.time_label.grid(row=2, column=0, padx=20, pady=10, sticky="e")
        self.time_entry = tk.Entry(root, width=15, font=("Arial", 12))
        self.time_entry.grid(row=2, column=1, pady=10)

        # AM/PM Dropdown
        self.am_pm_label = tk.Label(root, text="AM/PM:", font=("Arial", 12), bg="#f7f7f7")
        self.am_pm_label.grid(row=2, column=2, padx=20, pady=10)
        self.am_pm_combo = ttk.Combobox(root, values=["AM", "PM"], width=10, font=("Arial", 12))
        self.am_pm_combo.set("AM")  # Default to AM
        self.am_pm_combo.grid(row=2, column=3, pady=10)

        # Add Event Button
        self.add_button = tk.Button(root, text="Add Event", command=self.add_event, font=("Arial", 12), bg="#4CAF50", fg="white", relief="flat")
        self.add_button.grid(row=3, column=1, pady=20)

        # AI Suggestion Button
        self.suggest_button = tk.Button(root, text="Time Schedule Suggestion", command=self.suggest_time, font=("Arial", 12), bg="#FF9800", fg="white", relief="flat")
        self.suggest_button.grid(row=4, column=1, pady=20)

        # Remove Event Button
        self.remove_button = tk.Button(root, text="Remove Event", command=self.remove_event, font=("Arial", 12), bg="#F44336", fg="white", relief="flat")
        self.remove_button.grid(row=6, column=1, pady=20)

        # Event Listbox
        self.event_listbox = tk.Listbox(root, width=40, height=10, font=("Arial", 12), bg="#ffffff", selectbackground="#4CAF50", selectmode="single")
        self.event_listbox.grid(row=5, column=0, columnspan=4, pady=20)

        # Load existing events from file
        self.load_events()  # Ensure the load_events method is available

    def load_events(self):
        """Load events from the events file"""
        try:
            with open(file_name, "r") as file:
                events.clear()  # Clear the events list before loading new data
                for line in file.readlines():
                    event_desc, event_time_str = line.strip().split(", ")
                    event_time_obj = datetime.strptime(event_time_str, "%I:%M %p")
                    events.append({"description": event_desc, "time": event_time_obj})
            self.update_event_listbox()
        except FileNotFoundError:
            pass  # If the file doesn't exist, ignore this error

    def save_events(self):
        """Save events to the text file"""
        with open(file_name, "w") as file:
            for event in events:
                event_time_str = event["time"].strftime("%I:%M %p")
                file.write(f"{event['description']}, {event_time_str}\n")

    def add_event(self):
        """Adds an event to the schedule"""
        event_desc = self.event_entry.get()
        event_time = self.time_entry.get()
        am_pm = self.am_pm_combo.get()

        # Simple validation for event time format (HH:MM)
        try:
            # Combine the time with AM/PM
            event_time_str = f"{event_time} {am_pm}"
            event_time_obj = datetime.strptime(event_time_str, "%I:%M %p")

            # Check if the event time conflicts with existing events
            for event in events:
                if event["time"] == event_time_obj:
                    messagebox.showerror("Error", f"Event time {event_time_obj.strftime('%I:%M %p')} is already booked.")
                    return

            # Store the event
            events.append({"description": event_desc, "time": event_time_obj})
            self.update_event_listbox()
            self.event_entry.delete(0, tk.END)
            self.time_entry.delete(0, tk.END)

            # Save the event to the text file
            self.save_events()

            messagebox.showinfo("Success", "Event added successfully!")
        except ValueError:
            messagebox.showerror("Error", "Invalid time format. Please use HH:MM.")

    def update_event_listbox(self):
        self.event_listbox.delete(0, tk.END)
        for event in events:
            self.event_listbox.insert(tk.END, f"{event['description']} at {event['time'].strftime('%I:%M %p')}")

    def suggest_time(self):
        response = messagebox.askyesno("Time Schedule Suggestion", "This is a paid feature, would you like to check out the website to unlock more additional features?")
        
        if response == True:  # If user clicks Yes
            webbrowser.open("https://google.com/")  # Open the website



    def remove_event(self):
        # Get the selected event from the listbox
        try:
            selected_index = self.event_listbox.curselection()[0]
            event_to_remove = events[selected_index]

            # Remove event from the list
            events.remove(event_to_remove)

            # Update the listbox
            self.update_event_listbox()

            # Save the updated events list to the text file
            self.save_events()

            messagebox.showinfo("Success", f"Event '{event_to_remove['description']}' removed successfully!")
        except IndexError:
            messagebox.showerror("Error", "Please select an event to remove.")

    def show_app_info(self):
        """Show a window with app info"""
        info_window = tk.Toplevel(self.root)
        info_window.title("Scheduler@Work - App Info")

        # Set a reasonable initial size for the window
        info_window.geometry("650x200")
        info_window.resizable(False, False)  # Disable resizing

        # Create a label with the app info text
        info_label = tk.Label(info_window, text=config["info"], justify="left", padx=10, pady=10)

        # Pack the label and ensure it doesn't expand too much
        info_label.pack(fill="both", expand=False)

    def check_event_time(self):
        """Check if an event is due and show a notification."""
        current_time = datetime.now().strftime("%I:%M %p")  # Get current time

        for event in events:
            event_time = event["time"].strftime("%I:%M %p")
            if event_time == current_time:  # If the event time matches current time
                show_notification(event)  # Use win10toast to show notification

        # Schedule the function to run again every minute
        self.root.after(60000, self.check_event_time)


# Initialize Tkinter window
root = tk.Tk()
app = ScheduleApp(root)
root.mainloop()
