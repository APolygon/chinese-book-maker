def get_hanzi_stroke_svgs(word: str) -> list[str]:
    """Get a list of SVG filenames for each character in the word."""
    return [f"{ord(char)}-still.svg" for char in word]
