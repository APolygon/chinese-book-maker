import json
import os
from wordfreq import word_frequency

def add_frequency_scores(words):
    """
    Add frequency scores to each word in the list.
    
    Args:
        words: List of word dictionaries
        
    Returns:
        List of word dictionaries with added frequency scores
    """
    total = len(words)
    print("Adding frequency scores...")
    for i, word in enumerate(words, 1):
        if i % 100 == 0:  # Print progress every 100 words
            print(f"\rProcessing word {i}/{total}", end='')
            
        chinese_word = word['chineseword']
        # Get frequency score using wordfreq
        # Use 'zh' for Mandarin Chinese with best wordlist
        word['frequency_score'] = word_frequency(chinese_word, 'zh', wordlist='best')
    
    print("\nFrequency score update completed!")
    return words

if __name__ == "__main__":
    # Get the directory of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Input and output file paths
    input_path = os.path.join(current_dir, "..", "chinese_words_with_translations.json")
    output_path = os.path.join(current_dir, "..", "chinese_words_with_frequency.json")
    
    # Read existing words
    print(f"Reading words from {input_path}")
    with open(input_path, "r", encoding="utf-8") as f:
        words = json.load(f)
    
    # Add frequency scores
    words_with_frequency = add_frequency_scores(words)
    
    # Save updated words
    print(f"\nSaving words with frequency scores to {output_path}")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(words_with_frequency, f, ensure_ascii=False, indent=2)
    
    print("\nDone! Sample of first 5 words with frequency scores:")
    for word in words_with_frequency[:5]:
        print(f"\n{word['chineseword']} ({word['pinyin']}):")
        print(f"Frequency score: {word['frequency_score']:.6f}")
        print(f"Translations: {', '.join(word['translations'])}")
        print(f"Grammar: {word['grammar']}")
        print(f"Level: {word['lowest_level']}") 