from utils import generate_latex_header

# Example usage
pinyin = "bīngxiāng"
characters = "冰箱"
translation = "Kühlschrank"

header_latex = generate_latex_header(pinyin, characters, translation)

# Create the full LaTeX document
full_latex = (
    "\\documentclass{article}\n"
    "\\usepackage{fontspec}\n"
    "\\usepackage{xeCJK}\n"
    "\n"
    "% Fonts\n"
    "\\setmainfont{Times New Roman}\n"  # Common system font
    "\\setCJKmainfont{STSong}\n"  # Common Chinese font
    "\n"
    "\\usepackage[a4paper,margin=2cm]{geometry}\n"
    "\\usepackage{parskip}\n"
    "\n"
    "\\begin{document}\n"
    "\n"
    f"{header_latex}\n"
    "\n"
    "\\end{document}"
)

# Write to file
with open("test_header.tex", "w", encoding="utf-8") as f:
    f.write(full_latex)

print("✅ LaTeX file generated: test_header.tex") 