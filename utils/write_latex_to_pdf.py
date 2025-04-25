import os
import subprocess

def write_latex_to_pdf(tex_code: str, output_basename: str):
    """Write LaTeX code to a file and compile it to PDF."""
    output_dir = "output/pngs"  # Keep the same output directory as original
    tex_file = os.path.join(output_dir, f"{output_basename}.tex")

    with open(tex_file, "w", encoding="utf-8") as f:
        f.write(tex_code)

    subprocess.run(
        ["xelatex", "-interaction=nonstopmode", f"{output_basename}.tex"],
        cwd=output_dir,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    print(f"✅ PDF generated: {os.path.join(output_dir, f'{output_basename}.pdf')}") 