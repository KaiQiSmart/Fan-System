"""
================================================================================
PROJECT: Fan Integrated Design Platform
MODULE: _0_GUI.py
DESCRIPTION: 
    The central navigation hub with a visually unified dual-column dashboard.
    Standardized formatting: Labels are left-aligned, and colons are vertically 
    aligned using fixed-width fields.
================================================================================
"""
#230-# open model training GUI 

import tkinter as tk
import sys
from tkinter import messagebox, simpledialog
from tkinter import ttk
from _1_fan_GUI import FanGUI
from _2_rib_GUI import RibGUI
from _3_PQmodel_GUI import ModelTrainingGUI 
from _4_PQpredict_GUI import PQPredictGUI 
from _6_Database_GUI import DatabaseGUI
from _7_Guide_GUI import ParameterGuideGUI

# --- VERSION HISTORY DATA ---
VERSION_HISTORY = [
    {
        "version": "v0.3",
        "date": "2026-03-31",
        "desc": "Rib Reinforcement System",
        "details": "• Added Rib (spiral) design module\n• Integrated IBL generation for Creo elements"
    },
    {
        "version": "v0.2",
        "date": "2026-03-27",
        "desc": "Manufacturing Output & Advanced Geometry",
        "details": "• Added Creo-compatible XYZ coordinate export\n• Implemented upper/lower Ripple features\n• Verified reversed blade feature via -F-angle"
    },
    {
        "version": "v0.1",
        "date": "2026-03-25",
        "desc": "UI/UX Enhancements & Parametric Definitions",
        "details": "• Resolved inconsistency in 2D preview\n• Added Wave and Rise blade features\n• Integrated detailed parameter documentation"
    },
    {
        "version": "v0.0",
        "date": "2026-03-16",
        "desc": "Initial System Launch",
        "details": "• Launched Fan and Rib Design modules\n• Integrated PQ Training & Prediction modules"
    }
]

import tkinter as tk
from tkinter import messagebox
import sys
import os

base_dir = os.path.dirname(os.path.abspath(__file__))

def authenticate(fixed_password="QAQ123"):
    result = False

    win = tk.Tk()
    
    win.title("Authentication")
    win.iconbitmap(os.path.join(base_dir, "delta.ico"))

    win.resizable(False, False)

  
    width, height = 260, 140
    x = (win.winfo_screenwidth() - width) // 2
    y = (win.winfo_screenheight() - height) // 2
    win.geometry(f"{width}x{height}+{x}+{y}")

    
    tk.Label(
        win,
        text="Enter Password:",
        font=("Segoe UI", 12)
    ).pack(pady=(20, 6))


    
    pw_entry = tk.Entry(
        win,
        show="*",
        width=20,
        font=("Segoe UI", 11)
    )
    pw_entry.pack(ipady=3)

    pw_entry.focus_set()

    def check_password(event=None):
        nonlocal result
        if pw_entry.get() == fixed_password:
            result = True
            win.destroy()
        else:
            pw_entry.delete(0, tk.END)

    
    tk.Button(
        win,
        text="OK",
        command=check_password,
        width=10,
        font=("Segoe UI", 11)
    ).pack(pady=16)


    win.bind("<Return>", check_password)
    win.protocol("WM_DELETE_WINDOW", lambda: sys.exit())

    win.mainloop()
    return result


class MainGUI(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Fan Integrated Design Platform")
        self.geometry("1250x850") 
        self.minsize(1150, 750)

        self.iconbitmap(os.path.join(base_dir, "delta.ico"))

        self._build_layout()
        
        # Initial View: Show Welcome Dashboard
        self.show_welcome()

    def _build_layout(self):
        # Left menu configuration
        self.menu_frame = tk.Frame(self, width=240, bg="#2b2b2b")
        self.menu_frame.pack(side="left", fill="y")

        # Main content area
        self.content_frame = tk.Frame(self, bg="white")
        self.content_frame.pack(side="right", fill="both", expand=True)

        # Title in Menu
        tk.Label(
            self.menu_frame, text="ENGINEERING HUB", 
            fg="#888888", bg="#2b2b2b", font=("Arial", 12, "bold")
        ).pack(pady=20)

        # Navigation Menu Items
        menu_items = [
            ("Home Dashboard", self.show_welcome),
            ("1.Fan Design", self.open_fan),
            ("2.Rib Design", self.open_rib),
            ("3.PQ Model Training", self.open_pq_train),
            ("4.PQ Curve Prediction", self.open_pq_predict),
            ("6.Product Parameter Database", self.open_database),
            ("7.Parameter Documentation", self.open_guide), 
            ("Exit", self.quit),
        ]

        for text, command in menu_items:
            btn = tk.Button(
                self.menu_frame,
                text=text,
                command=command,
                bg="#3c3f41",
                fg="white",
                relief="flat",
                height=2,
                font=("Arial", 10),
                activebackground="#4b6eaf"
            )
            btn.pack(fill="x", padx=12, pady=6)

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_welcome(self):
        """Displays the home dashboard with left-aligned labels and aligned colons."""
        self.clear_content()
        
        container = tk.Frame(self.content_frame, bg="white")
        container.pack(expand=True, fill="both", padx=50, pady=40)

        # Header Section
        tk.Label(
            container, text="Welcome to Fan Integrated Design Platform",
            font=("Arial", 22, "bold"), bg="white", fg="#2b2b2b"
        ).pack(anchor="w", pady=(0, 5))

        tk.Label(
            container, text="Select a module from the left menu to begin your design process.",
            font=("Arial", 11), bg="white", fg="#666666"
        ).pack(anchor="w", pady=(0, 30))

        # Main Split
        main_split = tk.Frame(container, bg="white")
        main_split.pack(fill="both", expand=True)

        left_col = tk.Frame(main_split, bg="white")
        left_col.pack(side="left", fill="both", expand=True, padx=(0, 20))

        # --- Helper for Left-Aligned Labels with Aligned Colons ---
        def add_aligned_row(parent, label_text, value_text):
            row = tk.Frame(parent, bg="white")
            row.pack(fill="x", pady=2, padx=20) # Added indent for better look
            
            # Label (Left-aligned 'w' with fixed width 18)
            tk.Label(
                row, text=label_text, 
                bg="white", font=("Arial", 10), 
                width=18, anchor="w" 
            ).pack(side="left")

            # Colon (Fixed position)
            tk.Label(
                row, text=" : ", 
                bg="white", font=("Arial", 10)
            ).pack(side="left")

            # Value (Left-aligned)
            tk.Label(
                row, text=value_text, 
                bg="white", font=("Arial", 10), 
                anchor="w"
            ).pack(side="left")

        # --- 1. DESIGN WORKFLOW GUIDE ---
        workflow_frame = tk.LabelFrame(
            left_col, text="Design Workflow Guide", 
            bg="white", font=("Arial", 11, "bold"), padx=20, pady=15
        )
        workflow_frame.pack(fill="x", pady=(0, 30))

        workflow_data = [
            ("1. Fan Design", "Define blade geometry and generate XYZ coordinates."),
            ("2. Rib Design", "Configure fan housing and rib structures."),
            ("3. PQ Training", "Restricted access for model development."),
            ("4. PQ Prediction", "Predict P-Q curves for your new design."),
            ("5. Database", "Review and sort history designs and PQ results."),
            ("6. Documentation", "View detailed geometric parameter descriptions.")
        ]
        
        for label, desc in workflow_data:
            add_aligned_row(workflow_frame, label, desc)

        # --- 2. SYSTEM INFORMATION ---
        info_frame = tk.LabelFrame(
            left_col, text="System Information", 
            bg="white", font=("Arial", 11, "bold"), padx=20, pady=15
        )
        info_frame.pack(fill="x")

        latest_ver = VERSION_HISTORY[0]["version"]
        latest_date = VERSION_HISTORY[0]["date"]

        info_data = [
            ("System Name", "Fan Integrated Design Platform"),
            ("System Version", f"{latest_ver} "),
            ("Last Updated", latest_date),
            ("Department", "73800830 – IVFBU"),
            ("Team", "Automotive Fan RD 1C"),
            ("Developer", "Ryan Chuang"),
            ("Supervisor", "Chandler Huang")
        ]
        
        for label, value in info_data:
            add_aligned_row(info_frame, label, value)

        # --- RIGHT COLUMN: VERSION HISTORY ---
        right_col = tk.Frame(main_split, bg="white", width=420)
        right_col.pack(side="right", fill="both")
        right_col.pack_propagate(False)

        history_frame = tk.LabelFrame(
            right_col, text="Version History", 
            bg="white", font=("Arial", 11, "bold"), padx=15, pady=15
        )
        history_frame.pack(fill="both", expand=True)

        for item in VERSION_HISTORY:
            ver_header = tk.Frame(history_frame, bg="white")
            ver_header.pack(fill="x", pady=(8, 0))
            
            tk.Label(ver_header, text=item["version"], font=("Arial", 10, "bold"), bg="white", fg="#4b6eaf").pack(side="left")
            tk.Label(ver_header, text=item["date"], font=("Arial", 9), bg="white", fg="#999999").pack(side="right")
            
            tk.Label(history_frame, text=item["desc"], font=("Arial", 9, "italic", "bold"), bg="white", fg="#333333").pack(anchor="w")
            tk.Label(history_frame, text=item["details"], font=("Arial", 9), bg="white", fg="#555555", justify="left").pack(anchor="w", pady=(0, 10))

    # --- Navigation Logic ---
    def open_fan(self):
        self.clear_content()
        FanGUI(self.content_frame).pack(fill="both", expand=True)

    def open_rib(self):
        self.clear_content()
        RibGUI(self.content_frame).pack(fill="both", expand=True)

    def open_pq_train(self):
        self.clear_content()
        ModelTrainingGUI(self.content_frame).pack(fill="both", expand=True)

    def open_pq_predict(self):
        self.clear_content()
        PQPredictGUI(self.content_frame).pack(fill="both", expand=True) 

    def open_database(self):
        self.clear_content()
        DatabaseGUI(self.content_frame).pack(fill="both", expand=True)

    def open_guide(self):
        self.clear_content()
        ParameterGuideGUI(self.content_frame).pack(fill="both", expand=True)

if __name__ == "__main__":
    # FIRST: Check Password
    if authenticate():
        print("Success: Access granted.")
        # SECOND: If correct, launch the main system
        app = MainGUI()
        app.mainloop()
    else:
        print("Error: Access unauthorized.")
        