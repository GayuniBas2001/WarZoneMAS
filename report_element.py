import tkinter as tk
from tkinter import messagebox

def display_report(report):
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    report_text = ""
    for key, value in report.items():
        report_text += f"{key}:\n"
        for sub_key, sub_value in value.items():
            report_text += f"  {sub_key}: {sub_value}\n"
        report_text += "\n"
    messagebox.showinfo("Simulation Report", report_text)
    root.destroy()