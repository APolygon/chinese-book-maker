import os
import json
import argparse
from typing import List, Tuple
from make_latex_group import make_latex_group
from utils import write_latex_to_pdf

def compile_pdf(entries: List[Tuple[str, str, str]], output_basename: str = "chinese_strokes", chars_per_page: int = 4):
    """
    Compile a list of character entries into a PDF with stroke sequences.
    
    Args:
        entries: List of tuples containing (pinyin, character, translation)
        output_basename: Base name for the output PDF file
        chars_per_page: Number of characters to show per page
    """
    latex_entries = []
    
    # Add LaTeX document preamble
    latex_entries.append(
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
        "\\usepackage{tikz}\n"
        "\\usetikzlibrary{chains}\n"
        "\n"
        "\\begin{document}\n"
    )
    
    # Generate LaTeX for each entry
    for i, (pinyin, word, translation) in enumerate(entries):
        latex_entries.append(make_latex_group(pinyin, word, translation))
        
        # Add page break after every chars_per_page entries (except for the last page)
        if (i + 1) % chars_per_page == 0 and i < len(entries) - 1:
            latex_entries.append("\\pagebreak")
    
    # Add document end
    latex_entries.append("\\end{document}")
    
    # Combine all LaTeX code
    full_latex = "\n\n".join(latex_entries)
    
    # Write and compile PDF
    write_latex_to_pdf(full_latex, output_basename)

def load_entries_from_json(json_path: str, cutoff: int = None) -> List[Tuple[str, str, str]]:
    """
    Load entries from a JSON file containing word dictionaries.
    
    Args:
        json_path: Path to the JSON file
        cutoff: Maximum number of entries to load (None for all)
        
    Returns:
        List of tuples (pinyin, character, translation)
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        words = json.load(f)
    
    if cutoff:
        words = words[:cutoff]
    
    entries = []
    for word in words:
        # Get the first translation from the translations list
        translation = word['translations'][0] if word['translations'] else ''
        entry = (
            word['pinyin'],
            word['chineseword'],
            translation
        )
        entries.append(entry)
    
    return entries

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate PDF with Chinese character stroke sequences')
    parser.add_argument('--cutoff', type=int, help='Number of words to process (default: all)')
    parser.add_argument('--output', type=str, default='chinese_strokes', help='Output PDF basename')
    parser.add_argument('--chars-per-page', type=int, default=4, help='Number of characters per page')
    args = parser.parse_args()
    
    # Get the directory of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the JSON file
    json_path = os.path.join(current_dir, "chinese_words_with_translations.json")
    
    if not os.path.exists(json_path):
        print(f"Error: File not found at {json_path}")
    else:
        print(f"Loading words from {json_path}")
        entries = load_entries_from_json(json_path, args.cutoff)
        print(f"Processing {len(entries)} words...")
        
        output_name = f"{args.output}_{len(entries)}" if args.cutoff else args.output
        compile_pdf(entries, output_name, args.chars_per_page)
        print(f"PDF generated: {output_name}.pdf") 