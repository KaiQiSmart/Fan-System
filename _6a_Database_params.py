# _6a_Database_params.py
import json
import os
from _6a_Database_path import DatabasePath

class DatabaseManager:
    def __init__(self):
        self.path_config = DatabasePath()
        self.all_data = []
        self.all_keys = []

    def flatten_json(self, y):
        """Standard recursive flattening."""
        out = {}
        def flatten(x, name=''):
            if type(x) is dict:
                for a in x:
                    flatten(x[a], name + a + '.')
            elif type(x) is list:
                out[name[:-1]] = ", ".join(map(str, x))
            else:
                out[name[:-1]] = x
        flatten(y)
        return out

    def load_blade_parameters(self):
        self.all_data = []
        ordered_keys = {}
        blade_files = self.path_config.get_blade_files()
        
        for file in blade_files:
            file_path = os.path.join(self.path_config.fan_data_dir, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    raw_content = json.load(f)
                    flat_record = self.flatten_json(raw_content)
                    for k in flat_record.keys():
                        ordered_keys[k] = None
                    self.all_data.append(flat_record)
            except Exception as e:
                print(f"Error loading {file}: {e}")

        self.all_keys = list(ordered_keys.keys())
        return self.all_data, self.all_keys

    def filter_data(self, active_filters):
        """Filter data and print debug info to console."""
        filtered_list = self.all_data.copy()
        
        for col, (min_v, max_v) in active_filters.items():
            temp = []
            for record in filtered_list:
                val = record.get(col)
                if val is None: continue
                try:
                    num_val = float(val)
                    if min_v <= num_val <= max_v:
                        temp.append(record)
                except (ValueError, TypeError):
                    continue
            filtered_list = temp
            
        print(f"Filter applied on [{col}]: {len(filtered_list)} items found.")
        return filtered_list

    def sort_data(self, target_list, key, reverse=False):
        def sort_logic(x):
            val = x.get(key, 0)
            if val is None or val == "": return -1e9
            try:
                if isinstance(val, str) and "," in val:
                    return float(val.split(",")[0])
                return float(val)
            except (ValueError, TypeError):
                return str(val).lower()
        target_list.sort(key=sort_logic, reverse=reverse)
        return target_list