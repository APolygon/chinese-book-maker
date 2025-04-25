#!/usr/bin/env python3
import json
import argparse
import os
from typing import List, Dict
import unicodedata
from collections import Counter

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

def search_words(words: List[Dict], query: str, search_type: str = 'chinese') -> List[Dict]:
    """
    Search for words based on query and search type.
    
    Args:
        words: List of word dictionaries
        query: Search query
        search_type: Type of search ('chinese', 'pinyin', 'grammar', 'level')
    
    Returns:
        List of matching word dictionaries
    """
    query = query.lower()
    if search_type == 'pinyin':
        query = normalize_pinyin(query)
    results = []
    
    for word in words:
        if search_type == 'chinese':
            if query in word['chineseword'].lower():
                results.append(word)
        elif search_type == 'pinyin':
            normalized_pinyin = normalize_pinyin(word['pinyin'].lower())
            if query in normalized_pinyin:
                results.append(word)
        elif search_type == 'grammar':
            if query in word['grammar'].lower():
                results.append(word)
        elif search_type == 'level':
            if query in word.get('lowest_level', '').lower():
                results.append(word)
    
    return results

def format_word(word: Dict) -> str:
    """Format a word dictionary for display."""
    return (f"Chinese: {word['chineseword']}\n"
            f"Pinyin: {word['pinyin']}\n"
            f"Grammar: {word['grammar']}\n"
            f"Level: {word.get('lowest_level', '')}\n"
            f"All levels: {', '.join(word.get('levels', []))}\n")

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

def main():
    parser = argparse.ArgumentParser(description='Search for words in the TOCFL vocabulary list.')
    parser.add_argument('query', help='Search query')
    parser.add_argument('--type', choices=['chinese', 'pinyin', 'grammar', 'level'],
                      default='chinese', help='Type of search (default: chinese)')
    parser.add_argument('--json', default='chinese_words_all.json',
                      help='Path to JSON file (default: chinese_words_all.json)')
    parser.add_argument('--count', action='store_true',
                      help='Show only statistics about the search results')
    
    args = parser.parse_args()
    
    # Get the directory of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Construct path to JSON file
    json_path = os.path.join(current_dir, '..', args.json)
    
    # Load words
    words = load_words(json_path)
    if not words:
        return
    
    # Search
    results = search_words(words, args.query, args.type)
    
    # Display results
    if results:
        if args.count:
            print_statistics(results)
        else:
            print(f"\nFound {len(results)} matching words:\n")
            for word in results:
                print(format_word(word))
                print("-" * 40)
            print("\nAdd --count to see statistics about the results.")
    else:
        print(f"\nNo words found matching '{args.query}' in {args.type} search.")

if __name__ == "__main__":
    main() 