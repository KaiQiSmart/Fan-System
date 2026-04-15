#_2d1_XYZ_creo.py

import os
import re
from collections import defaultdict

def read_solid_xyz(file_path):
    """
    Reads X, Y, Z coordinates from a space-separated text file.
    """
    coords = []
    if not os.path.exists(file_path):
        return coords
    with open(file_path, "r") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) == 3:
                try:
                    x, y, z = map(float, parts)
                    coords.append((x, y, z))
                except ValueError:
                    continue
    return coords

def parse_filename(file):
    """
    Parses the filename to extract BladeID and Section index.
    Expected format: [BladeID]_[ModelName]_Section[Num].txt
    """
    # Matches: [BladeID]_[ModelName]_Section[Num].txt
    match = re.match(r"(\d+_[A-Za-z0-9_]+)_RibSection(\d+)\.txt", file)
    if not match:
        return None, None
    blade_id = match.group(1)
    section_id = int(match.group(2))
    return blade_id, section_id

def write_single_section_block(out, section_id, coords):
    """
    Writes a single 'begin section' and 'begin curve' block for the entire coordinate set.
    """
    out.write(f"begin section!{section_id}\n")
    out.write("begin curve\n")

    for i, (x, y, z) in enumerate(coords):
        idx = i + 1  # 1-based index for IBL format
        out.write(f"{idx}\t{x:.4f}\t{y:.4f}\t{z:.4f}\n")

    out.write("\n")

def generate_full_creo_ibl(source_folder, output_folder):
    """
    Reads .txt files and generates .ibl files where each section contains one complete curve.
    """
    if not os.path.exists(source_folder):
        print(f"Source directory not found: {source_folder}")
        return
    
    os.makedirs(output_folder, exist_ok=True)

    # Filter files that contain "Section" and end with ".txt"
    files = [f for f in os.listdir(source_folder) if f.endswith(".txt") and "Section" in f]
    grouped = defaultdict(dict)

    for file in files:
        blade_id, section_id = parse_filename(file)
        if blade_id is not None:
            grouped[blade_id][section_id] = file

    for blade_id, sections in grouped.items():
        output_path = os.path.join(output_folder, f"{blade_id}_XYZ_creo.ibl")

        with open(output_path, "w") as out:
            # IBL Header
            out.write("Open\n")
            out.write("arclength\n")

            # Process sections in numerical order
            for sec in sorted(sections.keys()):
                file_full_path = os.path.join(source_folder, sections[sec])
                coords = read_solid_xyz(file_full_path)
                
                if not coords:
                    continue

                # Write the entire coordinates as one curve per section
                write_single_section_block(out, sec, coords)

        print(f"✔ Generated Full XYZ IBL: {os.path.basename(output_path)}")


if __name__ == "__main__":
    # Execute the conversion
    # Source: Current directory (.), Output: ./output
    generate_full_creo_ibl(".", "./output")