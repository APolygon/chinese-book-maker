import os
import subprocess
from bs4 import BeautifulSoup
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

from utils import get_hanzi_stroke_svgs, generate_stroke_step_pngs

def analyze_svg_file(svg_path):
    """Analyze an SVG file to count strokes and check for potential issues."""
    with open(svg_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "xml")
    
    # Find all paths with stroke classes
    stroke_paths = []
    for path in soup.find_all("path"):
        stroke_class = path.get('class', '')
        if stroke_class and isinstance(stroke_class, str) and stroke_class.startswith('stroke'):
            stroke_paths.append(path)
    
    return len(stroke_paths)

def test_stroke_generation():
    # Test a variety of characters with different stroke counts
    test_chars = ["龍", "長", "中", "國", "人"]
    
    # Create output directories relative to project root
    output_dir = os.path.join(project_root, "test_output")
    pngs_dir = os.path.join(project_root, "output/pngs")
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(pngs_dir, exist_ok=True)
    
    # Base path for SVG files
    svg_base_path = os.path.join(project_root, "makemeahanzi/svgs-still")
    
    for char in test_chars:
        print(f"\nTesting character: {char}")
        
        # Get SVG files
        svg_files = get_hanzi_stroke_svgs(char)
        print(f"Found {len(svg_files)} SVG files")
        
        for svg_file in svg_files:
            char_code = svg_file.split('-')[0]
            hanzi_char = chr(int(char_code))
            print(f"\nProcessing character: {hanzi_char}")
            
            # Construct full SVG path
            svg_path = os.path.join(svg_base_path, svg_file)
            print(f"Using SVG path: {svg_path}")
            
            # Analyze original SVG
            num_strokes = analyze_svg_file(svg_path)
            print(f"Number of strokes in original SVG: {num_strokes}")
            
            # Check if all PNGs already exist
            all_pngs_exist = True
            for i in range(1, num_strokes + 1):
                png_path = os.path.join(pngs_dir, f"{hanzi_char}_step_{i:02d}.png")
                if not os.path.exists(png_path) or os.path.getsize(png_path) == 0:
                    all_pngs_exist = False
                    break
            
            if all_pngs_exist:
                print(f"⏩ All PNGs for {hanzi_char} already exist, skipping generation")
            else:
                # Generate stroke steps
                generate_stroke_step_pngs(svg_path, hanzi_char)
            
            # Verify each step
            step = 1
            while True:
                png_path = os.path.join(pngs_dir, f"{hanzi_char}_step_{step:02d}.png")
                if not os.path.exists(png_path):
                    break
                    
                # Check if the PNG exists and is valid
                if os.path.getsize(png_path) == 0:
                    print(f"❌ Step {step}: Empty PNG file")
                else:
                    print(f"✅ Step {step}: PNG exists ({os.path.getsize(png_path)} bytes)")
                
                step += 1
            
            total_steps = step - 1
            print(f"\nSummary for {hanzi_char}:")
            print(f"- Total strokes in SVG: {num_strokes}")
            print(f"- Total PNG steps generated: {total_steps}")
            if num_strokes != total_steps:
                print(f"❌ Warning: Number of strokes ({num_strokes}) doesn't match number of steps ({total_steps})")
            else:
                print("✅ Number of strokes matches number of steps")

if __name__ == "__main__":
    test_stroke_generation() 