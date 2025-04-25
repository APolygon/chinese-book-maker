import json
import os
from pycccedict.cccedict import CcCedict

def create_translation_map():
    """
    Create a map of Chinese words to their translations from CC-CEDICT.
    
    Returns:
        dict: A dictionary mapping Chinese words to their translations
    """
    print("Loading CC-CEDICT dictionary...")
    cedict = CcCedict()
    entries = cedict.get_entries()
    
    # Create a map for both traditional and simplified characters
    translation_map = {}
    for entry in entries:
        # Add simplified character mapping
        if entry['simplified'] not in translation_map:
            translation_map[entry['simplified']] = []
        translation_map[entry['simplified']].extend(entry['definitions'])
        
        # Add traditional character mapping if different
        if entry['traditional'] != entry['simplified']:
            if entry['traditional'] not in translation_map:
                translation_map[entry['traditional']] = []
            translation_map[entry['traditional']].extend(entry['definitions'])
    
    print(f"Dictionary loaded with {len(translation_map)} entries")
    return translation_map

def add_translations(words):
    """
    Add translations to each word in the list using a pre-loaded translation map.
    
    Args:
        words: List of word dictionaries
        
    Returns:
        List of word dictionaries with added translations
    """
    # Create translation map once
    translation_map = create_translation_map()
    
    total = len(words)
    print("Adding translations...")
    for i, word in enumerate(words, 1):
        if i % 100 == 0:  # Print progress every 100 words
            print(f"\rProcessing word {i}/{total}", end='')
            
        chinese_word = word['chineseword']
        word['translations'] = translation_map.get(chinese_word, [])
    
    print("\nTranslation completed!")
    return words

if __name__ == "__main__":
    # Get the directory of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Input and output file paths
    input_path = os.path.join(current_dir, "..", "chinese_words_all.json")
    output_path = os.path.join(current_dir, "..", "chinese_words_with_translations.json")
    
    # Read existing words
    print(f"Reading words from {input_path}")
    with open(input_path, "r", encoding="utf-8") as f:
        words = json.load(f)
    
    # Add translations
    words_with_translations = add_translations(words)
    
    # Save updated words
    print(f"\nSaving words with translations to {output_path}")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(words_with_translations, f, ensure_ascii=False, indent=2)
    
    print("\nDone! Sample of first 5 words with translations:")
    for word in words_with_translations[:5]:
        print(f"\n{word['chineseword']} ({word['pinyin']}):")
        print(f"Translations:")
        for i, trans in enumerate(word['translations'], 1):
            print(f"  {i}. {trans}")
        print(f"Grammar: {word['grammar']}")
        print(f"Level: {word['lowest_level']}") 