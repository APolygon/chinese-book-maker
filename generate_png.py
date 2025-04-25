from bs4 import BeautifulSoup
import os
import subprocess

def generate_stroke_step_pngs(svg_path: str, output_prefix: str, output_dir: str):
    # Use absolute path to avoid any confusion with Inkscape's behavior
    png_dir = os.path.abspath(os.path.join(output_dir, "pngs"))
    os.makedirs(png_dir, exist_ok=True)

    # Read the SVG file
    with open(svg_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "xml")

    # Remove all stroke number labels (text)
    for text in soup.find_all("text"):
        text.decompose()

    # Remove any mirrored transforms like scale(-1, ...)
    for g in soup.find_all("g"):
        if g.has_attr("transform") and "scale(-1" in g["transform"]:
            del g["transform"]

    # Collect all stroke paths and force them to black
    all_strokes = soup.find_all("path")
    for path in all_strokes:
        path.attrs = {}
        path["style"] = "fill:none;stroke:#000000;stroke-width:3"

    # Build gray background stroke set
    gray_paths = []
    for path in all_strokes:
        gray_path = BeautifulSoup(str(path), "xml").find("path")
        gray_path.attrs = {}
        gray_path["style"] = "fill:none;stroke:#CCCCCC;stroke-width:3"
        gray_paths.append(gray_path)

    for i in range(1, len(all_strokes) + 1):
        step_svg_path = os.path.join(png_dir, f"{output_prefix}_step_{i:02d}.svg")
        step_png_path = os.path.join(png_dir, f"{output_prefix}_step_{i:02d}.png")

        if os.path.exists(step_png_path):
            continue  # Skip if already rendered

        # Create a new SVG document
        step_soup = BeautifulSoup(
            '<svg xmlns="http://www.w3.org/2000/svg" width="109" height="109" viewBox="0 0 109 109"></svg>',
            "xml"
        )
        svg_root = step_soup.svg

        # Add background gray strokes
        for gp in gray_paths:
            svg_root.append(gp)

        # Add black strokes up to step i
        for j in range(i):
            black_path = BeautifulSoup(str(all_strokes[j]), "xml").find("path")
            black_path.attrs = {}
            black_path["style"] = "fill:none;stroke:#000000;stroke-width:3"
            svg_root.append(black_path)

        # Write the step SVG to disk
        with open(step_svg_path, "w", encoding="utf-8") as out_svg:
            out_svg.write(str(step_soup))

        # Convert SVG to PNG using Inkscape with absolute paths
        step_svg_path = os.path.abspath(step_svg_path)
        step_png_path = os.path.abspath(step_png_path)

        print(f"🔄 Rendering: {step_png_path}")

        subprocess.run([
            "inkscape",
            step_svg_path,
            "--export-type=png",
            "--export-area-drawing",
            "--export-width=300",
            f"--export-filename={step_png_path}"
        ], check=True)

        print(f"✅ Created: {step_png_path}")