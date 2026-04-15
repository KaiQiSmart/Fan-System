# _6_Database_GUI.py
import tkinter as tk
from tkinter import ttk, messagebox
from _6a_Database_params import DatabaseManager

class DatabaseGUI(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.manager = DatabaseManager()
        self.sort_states = {} 
        self.active_filters = {} 
        self.current_display_data = [] 
        
        self.setup_ui()
        self.refresh_data()

    def setup_ui(self):
        # Top Panel
        top_frame = tk.Frame(self, bg="#f5f5f5", pady=10)
        top_frame.pack(fill="x")

        tk.Button(top_frame, text="🔄 Reload", command=self.refresh_data).pack(side="right", padx=15)

        # Filter Box
        filter_box = tk.LabelFrame(top_frame, text="Numeric Range Filter", padx=10, pady=5)
        filter_box.pack(side="left", padx=15)

        tk.Label(filter_box, text="Param:").pack(side="left")
        self.cb_filter_col = ttk.Combobox(filter_box, width=25, state="readonly")
        self.cb_filter_col.pack(side="left", padx=5)

        tk.Label(filter_box, text="Min:").pack(side="left")
        self.ent_min = tk.Entry(filter_box, width=8)
        self.ent_min.pack(side="left", padx=2)

        tk.Label(filter_box, text="Max:").pack(side="left")
        self.ent_max = tk.Entry(filter_box, width=8)
        self.ent_max.pack(side="left", padx=2)

        # Explicitly binding the command
        tk.Button(filter_box, text="Apply", command=self.apply_filter, bg="#4b6eaf", fg="white", width=8).pack(side="left", padx=10)
        tk.Button(filter_box, text="Reset", command=self.reset_filters, width=8).pack(side="left")

        # Table Panel
        self.tree_container = tk.Frame(self)
        self.tree_container.pack(fill="both", expand=True, padx=10, pady=5)

        self.tree = ttk.Treeview(self.tree_container, show='headings', height=22)
        vsb = ttk.Scrollbar(self.tree_container, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(self.tree_container, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')

        self.tree_container.grid_columnconfigure(0, weight=1)
        self.tree_container.grid_rowconfigure(0, weight=1)

    def refresh_data(self):
        """Complete reset of the table and dropdown."""
        data, keys = self.manager.load_blade_parameters()
        self.current_display_data = data
        
        # Reset Treeview Columns
        self.tree["columns"] = keys
        for key in keys:
            # Display name logic: only show the last part for table headers
            display = key.split('.')[-1]
            self.tree.heading(key, text=display, command=lambda k=key: self.sort_by_column(k))
            self.tree.column(key, width=95, anchor="center", stretch=False)
            self.sort_states[key] = False

        # Dropdown keeps full nested names for exact matching
        self.cb_filter_col['values'] = keys
        if keys: self.cb_filter_col.current(0)
        
        self.update_table(self.current_display_data)

    def apply_filter(self):
        col = self.cb_filter_col.get()
        if not col: return
        
        # Clear previous filters of the SAME column, but keep others (multi-filter)
        try:
            m_in = self.ent_min.get().strip()
            m_ax = self.ent_max.get().strip()
            
            min_v = float(m_in) if m_in else -1e12
            max_v = float(m_ax) if m_ax else 1e12
            
            self.active_filters[col] = (min_v, max_v)
            print(f"DEBUG: Filtering {col} between {min_v} and {max_v}")
            
            self.current_display_data = self.manager.filter_data(self.active_filters)
            self.update_table(self.current_display_data)
        except ValueError:
            messagebox.showerror("Error", "Please enter numeric values only.")

    def reset_filters(self):
        self.active_filters = {}
        self.ent_min.delete(0, tk.END)
        self.ent_max.delete(0, tk.END)
        self.current_display_data = self.manager.all_data
        self.update_table(self.current_display_data)

    def sort_by_column(self, col):
        is_reverse = self.sort_states.get(col, False)
        sorted_list = self.manager.sort_data(self.current_display_data, col, reverse=is_reverse)
        self.sort_states[col] = not is_reverse
        self.update_table(sorted_list)

    def update_table(self, data_list):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        cols = self.tree["columns"]
        for entry in data_list:
            row = [entry.get(k, "—") for k in cols]
            self.tree.insert("", "end", values=row)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Integrated Fan Database")
    root.geometry("1200x750")
    DatabaseGUI(root).pack(fill="both", expand=True)
    root.mainloop()