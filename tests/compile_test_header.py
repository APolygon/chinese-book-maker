import os
import subprocess

def compile_latex(tex_file: str) -> None:
    """Compile a LaTeX file using xelatex."""
    try:
        # Run xelatex twice to ensure proper compilation
        for _ in range(2):
            result = subprocess.run(
                ["xelatex", "-interaction=nonstopmode", tex_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            if result.returncode != 0:
                print("Error in LaTeX compilation:")
                print(result.stdout)
                print(result.stderr)
                return
            
        print(f"✅ Successfully compiled {tex_file}")
        
        # Clean up auxiliary files
        extensions_to_clean = ['.aux', '.log']
        base_name = tex_file.rsplit('.', 1)[0]
        for ext in extensions_to_clean:
            try:
                os.remove(base_name + ext)
            except FileNotFoundError:
                pass
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # First run test_header.py to generate the .tex file
    print("Generating LaTeX file...")
    subprocess.run(["python", "test_header.py"])
    
    # Then compile it
    print("\nCompiling LaTeX file...")
    compile_latex("test_header.tex") 