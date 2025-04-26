#!/usr/bin/env python3
import json
import argparse
import os
import sys
from typing import List, Dict, Callable
import unicodedata
from collections import Counter

# Add parent directory to path so we can import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.filters import (
    filter_by_level,
    filter_by_grammar,
    filter_by_text,
    filter_by_translation,
    filter_by_multiple_levels,
    appears_in_level,
    apply_filters,
    sort_by_pinyin,
    sort_by_stroke_count,
    sort_by_frequency,
    sort_by_level,
    apply_sort
)

def normalize_pinyin(text: str) -> str:
    """Remove tone marks from pinyin."""
    return ''.join(char for char in unicodedata.normalize('NFD', text)
                  if unicodedata.category(char) != 'Mn')

def load_words(json_path: str) -> List[Dict]:
    """Load words from JSON file."""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find file {json_path}")
        return []
    except json.JSONDecodeError:
        print(f"Error: File {json_path} is not valid JSON")
        return []

def search_words(words: List[Dict], query: str, search_type: str = 'chinese', exact: bool = False) -> List[Dict]:
    """
    Search for words based on query and search type.
    
    Args:
        words: List of word dictionaries
        query: Search query
        search_type: Type of search ('chinese', 'pinyin', 'grammar', 'level', 'translation')
        exact: If True, only match complete words in translations
    
    Returns:
        List of matching word dictionaries
    """
    if search_type == 'chinese':
        return filter_by_text(words, 'chineseword', query)
    elif search_type == 'pinyin':
        return filter_by_text(words, 'pinyin', query, normalize=True)
    elif search_type == 'grammar':
        return filter_by_grammar(words, query)
    elif search_type == 'level':
        return filter_by_level(words, query)
    elif search_type == 'translation':
        return filter_by_translation(words, query, exact)
    
    return []

def format_word(word: Dict) -> str:
    """Format a word dictionary for display."""
    translations = word.get('translations', [])
    if not translations:
        translations_str = "No translations available"
    else:
        translations_str = '; '.join(translations)
    
    frequency = word.get('frequency_score', 'N/A')
    return (f"Chinese: {word['chineseword']}\n"
            f"Pinyin: {word['pinyin']}\n"
            f"Grammar: {word['grammar']}\n"
            f"Level: {word.get('lowest_level', '')}\n"
            f"All levels: {', '.join(word.get('levels', []))}\n"
            f"Frequency score: {frequency}\n"
            f"Translations: {translations_str}")

def print_statistics(results: List[Dict]):
    """Print statistics about search results."""
    print(f"\nTotal matches found: {len(results)}")
    
    # Count by lowest level
    level_counts = Counter(word['lowest_level'] for word in results)
    print("\nDistribution by lowest level:")
    for level in ['beginner', 'intermediate', 'advanced']:
        count = level_counts.get(level, 0)
        percentage = (count / len(results) * 100) if results else 0
        print(f"  {level.capitalize()}: {count} ({percentage:.1f}%)")
    
    # Count by grammar
    grammar_counts = Counter(word['grammar'] for word in results)
    if grammar_counts:
        print("\nDistribution by grammar:")
        for grammar, count in sorted(grammar_counts.items()):
            percentage = (count / len(results) * 100)
            print(f"  {grammar}: {count} ({percentage:.1f}%)")
    
    # Count words appearing in multiple levels
    multi_level = sum(1 for word in results if len(word.get('levels', [])) > 1)
    if multi_level:
        print(f"\nWords appearing in multiple levels: {multi_level}")

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

def main():
    parser = argparse.ArgumentParser(description='Search for words in the TOCFL vocabulary list.')
    
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
    parser.add_argument('--output', type=str, help='Output filename for results (default: auto-generated from filters)')
    
    # Sorting options
    parser.add_argument('--sort', choices=['pinyin', 'stroke', 'frequency', 'level'],
                      help='Sort results by specified field')
    parser.add_argument('--reverse', action='store_true', help='Sort in reverse order')
    
    # File path option
    parser.add_argument('--json', type=str, default='chinese_words_with_frequency.json',
                      help='Path to JSON file containing word data (default: chinese_words_with_frequency.json)')
    
    args = parser.parse_args()
    
    # Get the directory of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Construct path to JSON file
    json_path = os.path.join(current_dir, '..', args.json)
    
    # Load words
    words = load_words(json_path)
    if not words:
        return
    
    # Build list of filters
    filters = []
    
    # Add text-based filters
    if args.pinyin:
        filters.append(lambda words: filter_by_text(words, 'pinyin', args.pinyin, normalize=not args.exact))
    if args.character:
        filters.append(lambda words: filter_by_text(words, 'chineseword', args.character))
    if args.translation:
        filters.append(lambda words: filter_by_translation(words, args.translation, exact=args.exact))
        
    # Add grammar filter
    if args.grammar:
        filters.append(lambda w: filter_by_grammar(w, args.grammar))
        
    # Add level-based filters
    if args.level:
        filters.append(lambda w: filter_by_level(w, args.level))
    if args.appears_in:
        filters.append(appears_in_level(args.appears_in))
    if args.min_levels:
        filters.append(lambda w: filter_by_multiple_levels(w, args.min_levels))
    
    # Apply all filters
    if filters:
        words = apply_filters(words, filters)
    
    # Apply sorting if specified
    if args.sort:
        sort_funcs = {
            'pinyin': sort_by_pinyin,
            'stroke': sort_by_stroke_count,
            'frequency': sort_by_frequency,
            'level': sort_by_level
        }
        words = apply_sort(words, sort_funcs[args.sort], args.reverse)
    
    # Display results
    if words:
        if args.count:
            print_statistics(words)
        else:
            print(f"\nFound {len(words)} matching words:\n")
            for word in words:
                print(format_word(word))
                print("-" * 40)
            print("\nAdd --count to see statistics about the results.")
            
            # Save results to file if output is specified
            if args.output:
                output_file = args.output
            else:
                output_file = f"{generate_default_filename(args)}.txt"
                
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"Found {len(words)} matching words:\n\n")
                for word in words:
                    f.write(format_word(word))
                    f.write("\n" + "-" * 40 + "\n")
            print(f"\nResults saved to {output_file}")
    else:
        print("\nNo words found matching the specified criteria.")

if __name__ == "__main__":
    main() 