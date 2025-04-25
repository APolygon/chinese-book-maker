import os
from utils import (
    get_hanzi_stroke_svgs,
    generate_stroke_step_pngs,
    generate_latex_stroke_sequence,
    generate_latex_header
)

def make_latex_group(pinyin: str, word: str, translation: str) -> str:
    """
    Generate LaTeX code for a character group including stroke sequences.
    
    Args:
        pinyin: The pinyin pronunciation of the character
        word: The Chinese character(s)
        translation: The translation of the character
    Returns:
        str: LaTeX code for the character group
    """
    latex_entries = []
    svg_base_path = "makemeahanzi/svgs-still"
    output_dir = "output/pngs"
    os.makedirs(output_dir, exist_ok=True)

    # Generate header
    header_latex = generate_latex_header(pinyin, word, translation)
    latex_entries.append(header_latex)

    # Generate stroke sequences
    for svg_file in get_hanzi_stroke_svgs(word):
        codepoint = int(svg_file.split('-')[0])
        hanzi_char = chr(codepoint)
        svg_path = os.path.join(svg_base_path, svg_file)

        generate_stroke_step_pngs(svg_path, hanzi_char)
        latex_code = generate_latex_stroke_sequence(hanzi_char)
        latex_entries.append(latex_code)

    return "\n\n".join(latex_entries)