import os
from utils import (
    get_hanzi_stroke_svgs,
    generate_stroke_step_pngs,
    generate_latex_stroke_sequence,
    write_latex_to_pdf
)

# -----------------------------
# CONFIGURATION
# -----------------------------
word = "冰箱"
svg_base_path = "makemeahanzi/svgs-still"
output_dir = "output/pngs"
os.makedirs(output_dir, exist_ok=True)

# -----------------------------
# MAIN
# -----------------------------

latex_entries = []

for svg_file in get_hanzi_stroke_svgs(word):
    codepoint = int(svg_file.split('-')[0])
    hanzi_char = chr(codepoint)
    svg_path = os.path.join(svg_base_path, svg_file)

    generate_stroke_step_pngs(svg_path, hanzi_char)
    latex_code = generate_latex_stroke_sequence(hanzi_char)

    latex_entries.append(rf"\section*{{{hanzi_char}}}" + "\n" + latex_code)

# Generate LaTeX
full_latex = (
    "\\documentclass{article}\n"
    "\\usepackage{graphicx}\n"
    "\\usepackage[a4paper,margin=2cm]{geometry}\n"
    "\\usepackage{xeCJK}\n"
    "\\usepackage{tikz}\n"
    "\\usetikzlibrary{chains}\n"
    "\\setCJKmainfont{Noto Serif CJK TC}\n"
    "\\begin{document}\n"
) + "\n\n".join(latex_entries) + "\\end{document}"

write_latex_to_pdf(full_latex, output_basename="bingxiang_strokes_colored")