import pandas as pd
import os
from typing import List, Dict
from collections import Counter

def extract_chinese_words(excel_path: str, sheet_names: list[str]) -> List[Dict[str, str]]:
    """
    Extract Chinese words from multiple sheets in the TOCFL Excel file.
    Keep only unique words with their lowest level occurrence.
    
    Args:
        excel_path: Path to the Excel file
        sheet_names: List of sheet names to read
        
    Returns:
        List of dictionaries containing word information:
        {
            'chineseword': str,  # Chinese characters
            'pinyin': str,       # Pinyin representation
            'grammar': str,      # Grammar category
            'levels': list,      # All levels where the word appears
            'lowest_level': str  # The lowest level (foundation < beginner < intermediate < advanced)
        }
    """
    # Map sheet names to English levels
    level_mapping = {
        '基礎': 'foundation',
        '進階(初等)': 'beginner',
        '高階(中等)': 'intermediate',
        '流利(高等)': 'advanced'
    }
    
    # Define level ranking (lower index = lower level)
    level_ranking = ['foundation', 'beginner', 'intermediate', 'advanced']
    
    try:
        word_dict = {}  # Dictionary to store word information
        
        # Process sheets in order from highest to lowest level
        for sheet_name in reversed(sheet_names):
            print(f"\nProcessing sheet: {sheet_name}")
            current_level = level_mapping[sheet_name]
            
            # Read the Excel file with specified sheet
            df = pd.read_excel(excel_path, sheet_name=sheet_name)
            
            # Get the words starting from row 3
            for _, row in df.iloc[2:].iterrows():
                if pd.isna(row['詞彙']):  # Skip empty rows
                    continue
                    
                word = str(row['詞彙']).strip()
                
                # Only process if it contains Chinese characters
                if any('\u4e00' <= char <= '\u9fff' for char in word):
                    if word not in word_dict:
                        # Initialize new word entry
                        word_dict[word] = {
                            'chineseword': word,
                            'pinyin': str(row['拼音']).strip() if not pd.isna(row['拼音']) else '',
                            'grammar': str(row['詞類']).strip() if not pd.isna(row['詞類']) else '',
                            'levels': [],
                            'lowest_level': current_level
                        }
                    
                    # Add current level to levels list if not already present
                    if current_level not in word_dict[word]['levels']:
                        word_dict[word]['levels'].append(current_level)
                    
                    # Update lowest level if current level is lower
                    if level_ranking.index(current_level) < level_ranking.index(word_dict[word]['lowest_level']):
                        word_dict[word]['lowest_level'] = current_level
                        # Update pinyin and grammar from the lowest level occurrence
                        word_dict[word]['pinyin'] = str(row['拼音']).strip() if not pd.isna(row['拼音']) else ''
                        word_dict[word]['grammar'] = str(row['詞類']).strip() if not pd.isna(row['詞類']) else ''
        
        # Convert dictionary to list
        unique_words = list(word_dict.values())
        
        # Find duplicates (words that appear in more than one level)
        duplicates = {word: info['levels'] for word, info in word_dict.items() if len(info['levels']) > 1}
        
        # Print statistics
        print_statistics(unique_words)
        
        if duplicates:
            print("\nWords that appear in multiple levels:")
            for word, levels in duplicates.items():
                print(f"'{word}' appears in levels: {', '.join(levels)} (lowest level: {word_dict[word]['lowest_level']})")
        
        return unique_words
        
    except Exception as e:
        print(f"Error processing Excel file: {e}")
        return []

def print_statistics(results: List[Dict]):
    """Print statistics about search results."""
    print(f"\nTotal matches found: {len(results)}")
    
    # Count by lowest level
    level_counts = Counter(word['lowest_level'] for word in results)
    print("\nDistribution by lowest level:")
    for level in ['foundation', 'beginner', 'intermediate', 'advanced']:
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

if __name__ == "__main__":
    # Get the directory of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the Excel file (relative to the script's directory)
    excel_path = os.path.join(current_dir, "..", "TOCFL_14425_vocab_list", "TOCFL_8000", "chinese 8000.xls")
    
    # Sheets to process (in order from highest to lowest level)
    sheets_to_process = ['流利(高等)', '高階(中等)', '進階(初等)', '基礎']
    
    if not os.path.exists(excel_path):
        print(f"Error: File not found at {excel_path}")
    else:
        words = extract_chinese_words(excel_path, sheets_to_process)
        
        # Save unique words to a JSON file in the root directory
        import json
        output_path = os.path.join(current_dir, "..", "chinese_words_all.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(words, f, ensure_ascii=False, indent=2)
        
        print(f"\nUnique words saved to {output_path}")
        
        # Print first 10 words as a sample
        print("\nSample of first 10 unique words:")
        for word in words[:10]:
            print(word) 