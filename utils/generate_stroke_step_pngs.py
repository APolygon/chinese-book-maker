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
            stroke_numbers.add(int(stroke_class.split('-')[1]))
    
    if not stroke_numbers:
        print(f"Warning: No strokes found in {svg_path}")
        return
    
    output_dir = "output/pngs"  # Keep the same output directory as original
    num_strokes = max(stroke_numbers)

    # Generate each step: gray background + progressively more black strokes
    for i in range(num_strokes):
        step_soup = BeautifulSoup(str(soup), "xml")
        
        # Remove all paths for strokes after the current one
        for j in range(i + 2, num_strokes + 1):
            remove_paths = step_soup.find_all("path", class_=f"stroke-{j}")
            for path in remove_paths:
                path.decompose()

        svg_out = os.path.join(output_dir, f"{output_prefix}_step_{i+1:02d}.svg")
        png_out = os.path.join(output_dir, f"{output_prefix}_step_{i+1:02d}.png")

        with open(svg_out, "w", encoding="utf-8") as out_svg:
            out_svg.write(str(step_soup))

        subprocess.run([
            "inkscape", svg_out,
            "--export-type=png",
            f"--export-filename={png_out}",
            "--export-width=300"
        ], check=True)

        print(f"✅ Created: {png_out}")
