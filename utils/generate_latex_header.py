def generate_latex_header(pinyin: str, characters: str, translation: str) -> str:
    """
    Generate LaTeX code for a header section with pinyin, Chinese characters, and translation.
    
    Args:
        pinyin: The pinyin representation of the word
        characters: The Chinese characters
        translation: The translation in the target language (can be multiple translations separated by '; ')
        
    Returns:
        str: LaTeX code for the header section
    """
    # Format translations: split by semicolon and number them
    translations = translation.split('; ')
    if len(translations) > 1:
        formatted_trans = '\\\\'.join(f"{i+1}. {trans}" for i, trans in enumerate(translations))
    else:
        formatted_trans = translation

    return (
        "\\noindent\n"
        "\\begin{minipage}[t]{0.25\\linewidth}\n"
        "\\raggedright\n"  # Left align
        "{\\Large " + pinyin + "}\n"
        "\\end{minipage}\n"
        "\\hfill\n"
        "\\begin{minipage}[t]{0.35\\linewidth}\n"
        "\\centering\n"
        "{\\fontsize{32pt}{36pt}\\selectfont " + characters + "}\n"
        "\\end{minipage}\n"
        "\\hfill\n"
        "\\begin{minipage}[t]{0.35\\linewidth}\n"
        "\\raggedright\n"  # Left align
        "{\\large\\parbox[t]{\\linewidth}{" + formatted_trans + "}}\n"
        "\\end{minipage}\n"
        "\\vspace{1em}\n"
    ) 