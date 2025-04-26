import os
import json
import argparse
from typing import List, Tuple, Optional, Callable
from make_latex_group import make_latex_group
from utils import write_latex_to_pdf
from utils.filters import (
    filter_by_level,
    filter_by_grammar,
    filter_by_multiple_levels,
    filter_by_custom,
    apply_filters,
    appears_in_level
)

def compile_pdf(entries: List[Tuple[str, str, str]], output_basename: str = "chinese_strokes", chars_per_page: int = 4):
    """
    Compile a list of character entries into a PDF with stroke sequences.
    
    Args:
        entries: List of tuples containing (pinyin, character, translations)
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
    for i, (pinyin, word, translations) in enumerate(entries):
        latex_entries.append(make_latex_group(pinyin, word, translations))
        
        # Add page break after every chars_per_page entries (except for the last page)
        if (i + 1) % chars_per_page == 0 and i < len(entries) - 1:
            latex_entries.append("\\pagebreak")
    
    # Add document end
    latex_entries.append("\\end{document}")
    
    # Combine all LaTeX code
    full_latex = "\n\n".join(latex_entries)
    
    # Write and compile PDF
    write_latex_to_pdf(full_latex, output_basename)

def load_entries_from_json(
    json_path: str,
    cutoff: Optional[int] = None,
    level_filter: Optional[str] = None,
    grammar_filter: Optional[str] = None,
    min_levels: Optional[int] = None,
    custom_filter: Optional[Callable[[dict], bool]] = None
) -> List[Tuple[str, str, str]]:
    """
    Load entries from a JSON file containing word dictionaries.
    
    Args:
        json_path: Path to the JSON file
        cutoff: Maximum number of entries to load (None for all)
        level_filter: Filter by lowest level ('beginner', 'intermediate', 'advanced')
        grammar_filter: Filter by grammar category
        min_levels: Filter words appearing in at least this many levels
        custom_filter: Custom filter function
        
    Returns:
        List of tuples (pinyin, character, translations)
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        words = json.load(f)
    
    # Build list of filters to apply
    filters = []
    if level_filter:
        filters.append(lambda w: filter_by_level(w, level_filter))
    if grammar_filter:
        filters.append(lambda w: filter_by_grammar(w, grammar_filter))
    if min_levels:
        filters.append(lambda w: filter_by_multiple_levels(w, min_levels))
    if custom_filter:
        filters.append(lambda w: filter_by_custom(w, custom_filter))
    
    # Apply filters
    if filters:
        words = apply_filters(words, filters)
    
    # Apply cutoff after filtering
    if cutoff:
        words = words[:cutoff]
    
    # Convert to entry format
    entries = []
    for word in words:
        # Join all translations with semicolons
        translations = '; '.join(word['translations']) if word['translations'] else ''
        entry = (
            word['pinyin'],
            word['chineseword'],
            translations
        )
        entries.append(entry)
    
    return entries

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate PDF with Chinese character stroke sequences')
    parser.add_argument('--cutoff', type=int, help='Number of words to process (default: all)')
    parser.add_argument('--output', type=str, default='chinese_strokes', help='Output PDF basename')
    parser.add_argument('--chars-per-page', type=int, default=4, help='Number of characters per page')
    parser.add_argument('--level', choices=['beginner', 'intermediate', 'advanced'],
                      help='Filter by lowest level')
    parser.add_argument('--grammar', help='Filter by grammar category (e.g., N, V, ADJ)')
    parser.add_argument('--min-levels', type=int, help='Filter words appearing in at least this many levels')
    parser.add_argument('--appears-in', help='Filter words that appear in this level')
    
    args = parser.parse_args()
    
    # Get the directory of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the JSON file
    json_path = os.path.join(current_dir, "chinese_words_with_translations.json")
    
    if not os.path.exists(json_path):
        print(f"Error: File not found at {json_path}")
    else:
        print(f"Loading words from {json_path}")
        
        # Create custom filter if --appears-in is specified
        custom_filter = appears_in_level(args.appears_in) if args.appears_in else None
        
        entries = load_entries_from_json(
            json_path,
            args.cutoff,
            args.level,
            args.grammar,
            args.min_levels,
            custom_filter
        )
        
        print(f"Processing {len(entries)} words...")
        
        output_name = f"{args.output}_{len(entries)}" if args.cutoff else args.output
        compile_pdf(entries, output_name, args.chars_per_page)
        print(f"PDF generated: {output_name}.pdf") 