import os

def generate_latex_stroke_sequence(char_label: str) -> str:
    """Generate LaTeX code for including a sequence of stroke images."""
    output_dir = "output/pngs"  # Keep the same output directory as original
    steps = []
    
    # Start tikzpicture with chain setup
    steps.append(r"\begin{tikzpicture}[start chain=going right,node distance=0pt]")
    
    # Add images
    for i in range(1, 30):
        png_path = os.path.join(output_dir, f"{char_label}_step_{i:02d}.png")
        if not os.path.exists(png_path):
            break
        steps.append(rf"\node[draw,on chain,inner sep=0pt,outer sep=0pt,join] {{\includegraphics[width=0.12\linewidth]{{{char_label}_step_{i:02d}.png}}}};")
    
    # End tikzpicture
    steps.append(r"\end{tikzpicture}\\[1em]")
    return '\n'.join(steps)
