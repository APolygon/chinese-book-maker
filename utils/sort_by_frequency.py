from utils.get_frequency_score import get_frequency_score

def sort_characters_by_frequency(characters: str) -> list[tuple[str, int]]:
    """
    Sort Chinese characters by their frequency score.
    
    Args:
        characters: A string containing Chinese characters to sort
        
    Returns:
        A list of tuples containing (character, frequency_score) sorted by frequency (highest first)
    """
    # Get frequency scores for each character
    char_scores = [(char, get_frequency_score(char)) for char in characters]
    
    # Sort by frequency score in descending order
    sorted_chars = sorted(char_scores, key=lambda x: x[1], reverse=True)
    
    return sorted_chars

if __name__ == "__main__":
    # Example usage
    test_chars = "龍長中國人"
    sorted_result = sort_characters_by_frequency(test_chars)
    
    print("Characters sorted by frequency (highest to lowest):")
    for char, score in sorted_result:
        print(f"{char}: {score}") 