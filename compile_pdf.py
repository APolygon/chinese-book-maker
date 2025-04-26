import os
import json
import argparse
from typing import List, Tuple, Optional, Callable
from make_latex_group import make_latex_group
from utils import write_latex_to_pdf
from utils.search_words import search_words, load_words, print_statistics
from utils.filters import (
    filter_by_level,
    filter_by_grammar,
    filter_by_multiple_levels,
    filter_by_custom,
    filter_by_text,
    filter_by_translation,
    appears_in_level,
    apply_filters,
    sort_by_pinyin,
    sort_by_stroke_count,
    sort_by_frequency,
    sort_by_level,
    apply_sort
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

def filter_by_text(words: List[dict], field: str, query: str, normalize: bool = False) -> List[dict]:
    """
    Filter words by text content in a specific field.
    
    Args:
        words: List of word dictionaries
        field: Field to search in (e.g., 'chineseword', 'pinyin')
        query: Text to search for
        normalize: Whether to normalize pinyin (remove tone marks) before comparison
        
    Returns:
        Filtered list of words
    """
    query = query.lower()
    if normalize and field == 'pinyin':
        query = normalize_pinyin(query)
        print(f"Normalized query: {query}")
    
    def matches(word: dict) -> bool:
        field_value = word.get(field, '').lower()
        if normalize and field == 'pinyin':
            field_value = normalize_pinyin(field_value)
            print(f"Word: {word.get('chineseword')}, Original pinyin: {word.get('pinyin')}, Normalized: {field_value}")
        return query in field_value
    
    return filter_by_custom(words, matches)

def generate_default_filename(args: argparse.Namespace) -> str:
    """
    Generate a descriptive default filename based on the filters and cutoff.
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        Descriptive filename without extension
    """
    parts = []
    
    # Add search filters
    if args.pinyin:
        parts.append(f"pinyin_{args.pinyin}")
    if args.character:
        parts.append(f"character_{args.character}")
    if args.translation:
        parts.append(f"translation_{args.translation}")
    if args.grammar:
        parts.append(f"grammar_{args.grammar}")
    if args.level:
        parts.append(f"level_{args.level}")
    if args.appears_in:
        parts.append(f"appears_in_{args.appears_in}")
    if args.min_levels:
        parts.append(f"min_levels_{args.min_levels}")
        
    # Add exact flag if used
    if args.exact:
        parts.append("exact")
        
    # If no filters were used, use a default name
    if not parts:
        return "output"
        
    return f"output_{'_'.join(parts)}"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate PDF with Chinese character stroke sequences')
    parser.add_argument('--cutoff', type=int, help='Number of words to process (default: all)')
    parser.add_argument('--output', type=str, help='Output PDF basename (default: auto-generated from filters)')
    parser.add_argument('--chars-per-page', type=int, default=4, help='Number of characters per page')
    
    # Search filters
    parser.add_argument('--pinyin', help='Filter by pinyin (can be partial match)')
    parser.add_argument('--character', help='Filter by Chinese character (can be partial match)')
    parser.add_argument('--translation', help='Filter by translation text (can be partial match)')
    parser.add_argument('--exact', action='store_true', help='For translation search: match complete words only')
    parser.add_argument('--grammar', help='Filter by grammar category (e.g., N, V, ADJ)')
    parser.add_argument('--level', choices=['foundation', 'beginner', 'intermediate', 'advanced'],
                      help='Filter by lowest level')
    parser.add_argument('--appears-in', help='Filter words that appear in this level')
    parser.add_argument('--min-levels', type=int, help='Filter words appearing in at least this many levels')
    parser.add_argument('--count', action='store_true', help='Show statistics about the results')
    
    # Sorting options
    parser.add_argument('--sort', choices=['pinyin', 'stroke', 'frequency', 'level'],
                      help='Sort results by specified field')
    parser.add_argument('--reverse', action='store_true', help='Sort in reverse order')
    
    args = parser.parse_args()
    
    # Get the directory of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the JSON file
    json_path = os.path.join(current_dir, "chinese_words_with_frequency.json")
    
    if not os.path.exists(json_path):
        print(f"Error: File not found at {json_path}")
        exit(1)
        
    print(f"Loading words from {json_path}")
    
    # Load words
    words = load_words(json_path)
    if not words:
        exit(1)
        
    # Apply search filters
    if args.pinyin:
        words = search_words(words, args.pinyin, 'pinyin', args.exact)
    elif args.character:
        words = search_words(words, args.character, 'chinese', args.exact)
    elif args.translation:
        words = search_words(words, args.translation, 'translation', args.exact)
    elif args.grammar:
        words = search_words(words, args.grammar, 'grammar', args.exact)
    elif args.level:
        words = search_words(words, args.level, 'level', args.exact)
        
    # Apply additional filters
    filters = []
    if args.appears_in:
        filters.append(appears_in_level(args.appears_in))
    if args.min_levels:
        filters.append(lambda w: filter_by_multiple_levels(w, args.min_levels))
        
    # Apply additional filters
    if filters:
        words = apply_filters(words, filters)
        
    # Apply cutoff after filtering
    if args.cutoff:
        words = words[:args.cutoff]
        
    # Apply sorting if specified
    if args.sort:
        sort_funcs = {
            'pinyin': sort_by_pinyin,
            'stroke': sort_by_stroke_count,
            'frequency': sort_by_frequency,
            'level': sort_by_level
        }
        words = apply_sort(words, sort_funcs[args.sort], args.reverse)
    
    # Show statistics if requested
    if args.count:
        print_statistics(words)
        if not words:
            exit(0)
            
    # Convert to entry format
    entries = []
    for word in words:
        translations = '; '.join(word['translations']) if word['translations'] else ''
        entry = (
            word['pinyin'],
            word['chineseword'],
            translations
        )
        entries.append(entry)
    
    print(f"Processing {len(entries)} words...")
    
    # Generate output filename
    if args.output:
        output_name = args.output
    else:
        output_name = generate_default_filename(args)
        
    # Add number of entries to filename if cutoff was specified
    if args.cutoff:
        output_name = f"{output_name}_{len(entries)}"
        
    compile_pdf(entries, output_name, args.chars_per_page)
    print(f"PDF generated: {output_name}.pdf") 