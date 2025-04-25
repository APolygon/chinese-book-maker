from pycccedict.cccedict import CcCedict

# Initialize the dictionary
cccedict = CcCedict()

def lookup(word: str) -> list[str]:
    """
    Look up the English translations for a Chinese word.
    
    Args:
        word (str): The Chinese word to look up (can be traditional or simplified)
        
    Returns:
        list[str]: A list of English definitions for the word
    """
    try:
        cedict = CcCedict()
        entries = cedict.get_entries()
        
        # Find entries where either traditional or simplified matches our word
        matching_entries = [
            entry for entry in entries 
            if entry['traditional'] == word or entry['simplified'] == word
        ]
        
        # Collect all definitions from matching entries
        all_definitions = []
        for entry in matching_entries:
            all_definitions.extend(entry['definitions'])
            
        return all_definitions
        
    except Exception as e:
        print(f"Error looking up word: {e}")
        return []

if __name__ == "__main__":
    # Interactive testing
    while True:
        word = input("Enter a Chinese word or character (or press Enter to quit): ")
        if not word:
            break

        translations = lookup(word)
        if translations:
            print(f"\n{word} translations:")
            for i, trans in enumerate(translations, 1):
                print(f"{i}. {trans}")
        else:
            print("No match found.")