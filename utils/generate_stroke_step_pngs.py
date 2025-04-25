import os
import subprocess
from bs4 import BeautifulSoup
from .process_svg import process_svg

def generate_stroke_step_pngs(svg_path: str, output_prefix: str):
    """Generate PNG files for each stroke step of a character."""
    soup = process_svg(svg_path)
    
    # Find all unique stroke numbers
    all_paths = soup.find_all("path")
    stroke_numbers = set()
    for path in all_paths:
        stroke_class = path.get('class', '')
        if stroke_class and isinstance(stroke_class, str) and stroke_class.startswith('stroke-'):
            try:
                stroke_num = int(stroke_class.split('-')[1])
                stroke_numbers.add(stroke_num)
            except (IndexError, ValueError):
                print(f"Warning: Invalid stroke class format: {stroke_class}")
    
    if not stroke_numbers:
        print(f"Warning: No strokes found in {svg_path}")
        return
    
    output_dir = "output/pngs"  # Keep the same output directory as original
    max_stroke = max(stroke_numbers)
    
    # Check for missing stroke numbers
    missing_strokes = set(range(1, max_stroke + 1)) - stroke_numbers
    if missing_strokes:
        print(f"Warning: Missing stroke numbers: {sorted(missing_strokes)}")
    
    # Generate each step: gray background + progressively more black strokes
    for i in range(1, max_stroke + 1):
        png_out = os.path.join(output_dir, f"{output_prefix}_step_{i:02d}.png")
        
        # Skip if PNG already exists
        if os.path.exists(png_out) and os.path.getsize(png_out) > 0:
            print(f"⏩ Skipping: {png_out} (already exists)")
            continue
            
        step_soup = BeautifulSoup(str(soup), "xml")
        
        # Remove all paths for strokes after the current one
        for j in range(i + 1, max_stroke + 1):
            remove_paths = step_soup.find_all("path", class_=f"stroke-{j}")
            for path in remove_paths:
                path.decompose()

        svg_out = os.path.join(output_dir, f"{output_prefix}_step_{i:02d}.svg")

        with open(svg_out, "w", encoding="utf-8") as out_svg:
            out_svg.write(str(step_soup))

        subprocess.run([
            "inkscape", svg_out,
            "--export-type=png",
            f"--export-filename={png_out}",
            "--export-width=300"
        ], check=True)

        print(f"✅ Created: {png_out}")
