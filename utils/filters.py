from typing import List, Dict, Optional, Callable, Tuple
import unicodedata

def filter_by_level(words: List[Dict], level: str) -> List[Dict]:
    """
    Filter words by their lowest level.
    
    Args:
        words: List of word dictionaries
        level: Level to filter by ('beginner', 'intermediate', 'advanced')
        
    Returns:
        Filtered list of words
    """
    return [word for word in words if word.get('lowest_level', '') == level]

def filter_by_grammar(words: List[Dict], grammar: str) -> List[Dict]:
    """
    Filter words by their grammar category.
    
    Args:
        words: List of word dictionaries
        grammar: Grammar category to filter by (e.g., 'N', 'V', 'ADJ')
        
    Returns:
        Filtered list of words
    """
    # Handle both formats: with and without parentheses
    grammar = grammar.upper()
    return [word for word in words 
            if word.get('grammar', '').upper() == grammar 
            or word.get('grammar', '').upper() == f'({grammar})'
            or word.get('grammar', '').upper().startswith(f'{grammar}/')
            or word.get('grammar', '').upper().startswith(f'({grammar})/')
    ]

def filter_by_multiple_levels(words: List[Dict], min_levels: int = 2) -> List[Dict]:
    """
    Filter words that appear in multiple levels.
    
    Args:
        words: List of word dictionaries
        min_levels: Minimum number of levels a word should appear in
        
    Returns:
        Filtered list of words
    """
    return [word for word in words if len(word.get('levels', [])) >= min_levels]

def filter_by_custom(words: List[Dict], predicate: Callable[[Dict], bool]) -> List[Dict]:
    """
    Filter words using a custom predicate function.
    
    Args:
        words: List of word dictionaries
        predicate: Function that takes a word dictionary and returns True/False
        
    Returns:
        Filtered list of words
    """
    return [word for word in words if predicate(word)]

def apply_filters(words: List[Dict], filters: List[Callable[[List[Dict]], List[Dict]]]) -> List[Dict]:
    """
    Apply multiple filters in sequence.
    
    Args:
        words: List of word dictionaries
        filters: List of filter functions to apply
        
    Returns:
        Filtered list of words
    """
    result = words
    for filter_func in filters:
        result = filter_func(result)
    return result

# Example predicates for custom filtering
def has_translation_containing(text: str) -> Callable[[Dict], bool]:
    """Create a predicate to filter words by translation content."""
    def predicate(word: Dict) -> bool:
        return any(text.lower() in trans.lower() for trans in word.get('translations', []))
    return predicate

def appears_in_level(level: str) -> Callable[[Dict], bool]:
    """Create a predicate to filter words that appear in a specific level."""
    def predicate(word: Dict) -> bool:
        return level in word.get('levels', [])
    return predicate

def normalize_pinyin(text: str) -> str:
    """Remove tone marks from pinyin."""
    return ''.join(char for char in unicodedata.normalize('NFD', text)
                  if unicodedata.category(char) != 'Mn')

def filter_by_text(words: List[Dict], field: str, query: str, normalize: bool = False) -> List[Dict]:
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
    
    def matches(word: Dict) -> bool:
        field_value = word.get(field, '').lower()
        if normalize and field == 'pinyin':
            field_value = normalize_pinyin(field_value)
        return query in field_value
    
    return filter_by_custom(words, matches)

def filter_by_translation(words: List[Dict], query: str, exact: bool = False) -> List[Dict]:
    """
    Filter words by their translations.
    
    Args:
        words: List of word dictionaries
        query: Text to search for in translations
        exact: If True, only match complete words, not substrings
        
    Returns:
        Filtered list of words containing the query in any of their translations
    """
    query = query.lower()
    
    def matches_translation(translation: str) -> bool:
        translation = translation.lower()
        if exact:
            # Split translation into words and check if query matches any complete word
            trans_words = set(word.strip('.,;()[]') for word in translation.split())
            return query in trans_words
        else:
            # Check if query appears anywhere in the translation
            return query in translation
    
    return [word for word in words 
            if any(matches_translation(trans) for trans in word.get('translations', []))]

def sort_by_pinyin(words: List[Dict], reverse: bool = False) -> List[Dict]:
    """
    Sort words by pinyin alphabetically.
    
    Args:
        words: List of word dictionaries
        reverse: If True, sort in reverse order
        
    Returns:
        Sorted list of words
    """
    return sorted(words, key=lambda x: x['pinyin'], reverse=reverse)

def sort_by_stroke_count(words: List[Dict], reverse: bool = False) -> List[Dict]:
    """
    Sort words by total stroke count.
    
    Args:
        words: List of word dictionaries
        reverse: If True, sort in reverse order
        
    Returns:
        Sorted list of words
    """
    return sorted(words, key=lambda x: sum(x.get('stroke_numbers', (0,))), reverse=reverse)

def sort_by_frequency(words: List[Dict], reverse: bool = False) -> List[Dict]:
    """
    Sort words by frequency score.
    If frequency data is not available, falls back to pinyin sorting.
    
    Args:
        words: List of word dictionaries
        reverse: If True, sort in reverse order
        
    Returns:
        Sorted list of words
    """
    # Check if any word has frequency data
    words_with_frequency = [word for word in words if 'frequency_score' in word and word['frequency_score'] is not None]
    
    if not words_with_frequency:
        print("Warning: No frequency data found in the words. All frequency_score values are missing or None.")
        print("Falling back to pinyin sorting.")
        return sort_by_pinyin(words, reverse)
    
    # Ensure frequency values are treated as numbers
    def get_frequency(word: Dict) -> float:
        freq = word.get('frequency_score')
        if freq is None:
            return 0.0
        # Convert to float if it's a string
        if isinstance(freq, str):
            try:
                return float(freq)
            except ValueError:
                return 0.0
        return float(freq)
    
    return sorted(words, key=get_frequency, reverse=reverse)

def sort_by_level(words: List[Dict], reverse: bool = False) -> List[Dict]:
    """
    Sort words by their lowest level.
    Levels are ordered: foundation < beginner < intermediate < advanced
    
    Args:
        words: List of word dictionaries
        reverse: If True, sort in reverse order
        
    Returns:
        Sorted list of words
    """
    level_order = {'foundation': 0, 'beginner': 1, 'intermediate': 2, 'advanced': 3}
    return sorted(words, key=lambda x: level_order.get(x.get('lowest_level', ''), -1), reverse=reverse)

def apply_sort(words: List[Dict], sort_func: Callable[[List[Dict], bool], List[Dict]], reverse: bool = False) -> List[Dict]:
    """
    Apply a sorting function to the list of words.
    
    Args:
        words: List of word dictionaries
        sort_func: Sorting function to apply
        reverse: If True, sort in reverse order
        
    Returns:
        Sorted list of words
    """
    return sort_func(words, reverse) 