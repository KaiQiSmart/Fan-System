# _1d1_creo.py
import os
import re
from collections import defaultdict

def read_solid_xyz(file_path):
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
    # Matches: [BladeID]_[ModelName]_Section[Num].txt
    match = re.match(r"(\d+_[A-Za-z0-9_]+)_Section(\d+)\.txt", file)
    if not match:
        return None, None
    blade_id = match.group(1)
    section_id = int(match.group(2))
    return blade_id, section_id

def write_curve_block(out, section_id, coords, start_idx, end_idx):
    
    # Output "begin section!X" + "begin curve" block
    # coords: all coordinate data
    # start_idx, end_idx: the start and end index in coords (0-based)

    out.write(f"begin section!{section_id}\n")
    out.write("begin curve\n")

    for i in range(start_idx, end_idx + 1):
        idx = i + 1  
        x, y, z = coords[i]
        out.write(f"{idx}\t{x:.4f}\t{y:.4f}\t{z:.4f}\n")

    out.write("\n")

def generate_creo_ibl(source_folder, output_folder):
    """
    Reads .txt files from source_folder and writes .ibl files to output_folder.
    Now splits every section into:
        - curve1: index 1–61
        - curve2: index 61–end   (index does NOT restart)
    """
    if not os.path.exists(source_folder):
        print(f"Source directory not found: {source_folder}")
        return
    
    os.makedirs(output_folder, exist_ok=True)

    files = [f for f in os.listdir(source_folder) if f.endswith(".txt") and "Section" in f]
    grouped = defaultdict(dict)

    for file in files:
        blade_id, section_id = parse_filename(file)
        if blade_id is not None:
            grouped[blade_id][section_id] = file

    for blade_id, sections in grouped.items():
        output_path = os.path.join(output_folder, f"{blade_id}_creo.ibl")

        with open(output_path, "w") as out:
            out.write("Open\n")
            out.write("arclength\n")

            for sec in sorted(sections.keys()):
                coords = read_solid_xyz(os.path.join(source_folder, sections[sec]))
                if not coords:
                    continue

                total_pts = len(coords)

                # ---- 1 curve：1–61 ----
                first_end = min(61, total_pts) - 1
                write_curve_block(out, sec, coords, 0, first_end)

                # ---- 2 curve：61–last ----
                if total_pts > 61:
                    write_curve_block(out, sec, coords, 60, total_pts - 1)

        print(f"✔ Generated Creo IBL in {output_folder}: {os.path.basename(output_path)}")


if __name__ == "__main__":
    generate_creo_ibl(".", "./output")