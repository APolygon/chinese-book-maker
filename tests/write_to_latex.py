import os
import subprocess

def write_latex_to_pdf(tex_code: str, output_basename: str, tex_dir: str = ".") -> None:
    os.makedirs(tex_dir, exist_ok=True)
    tex_file = os.path.join(tex_dir, f"{output_basename}.tex")

    with open(tex_file, "w", encoding="utf-8") as f:
        f.write(tex_code)

    subprocess.run(
        ["xelatex", "-interaction=nonstopmode", f"{output_basename}.tex"],
        cwd=tex_dir,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    print(f"✅ PDF generated: {os.path.join(tex_dir, f'{output_basename}.pdf')}")