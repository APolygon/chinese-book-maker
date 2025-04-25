import os

def generate_latex_stroke_sequence(char_label: str) -> str:
    """Generate LaTeX code for including a sequence of stroke images."""
    output_dir = "output/pngs"  # Keep the same output directory as original
    steps = []
    
    # Count total number of strokes
    total_strokes = 0
    for i in range(1, 30):
        png_path = os.path.join(output_dir, f"{char_label}_step_{i:02d}.png")
        if not os.path.exists(png_path):
            break
        total_strokes += 1
    
    # Calculate number of lines needed (8 strokes per line)
    strokes_per_line = 8
    num_lines = (total_strokes + strokes_per_line - 1) // strokes_per_line
    
    # Generate LaTeX code with line breaks
    for line in range(num_lines):
        # Start new tikzpicture for each line
        steps.append(r"\begin{tikzpicture}[start chain=going right,node distance=0pt]")
        
        # Add images for this line
        start_stroke = line * strokes_per_line + 1
        end_stroke = min((line + 1) * strokes_per_line, total_strokes)
        
        for i in range(start_stroke, end_stroke + 1):
            steps.append(rf"\node[draw,on chain,inner sep=0pt,outer sep=0pt,join] {{\includegraphics[width=0.12\linewidth]{{{char_label}_step_{i:02d}.png}}}};")
        
        # End tikzpicture and add spacing
        steps.append(r"\end{tikzpicture}")
        
        # Add vertical space between lines, but no page break
        if line < num_lines - 1:
            steps.append(r"\\[2em]")  # Vertical space between lines
    
    # Add some vertical space after the stroke sequence
    steps.append(r"\vspace{2em}")
    
    return '\n'.join(steps)
