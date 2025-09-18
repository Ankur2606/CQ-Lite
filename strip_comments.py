"""
Strip comments from Python files while preserving function docstrings.
"""

import sys
import os
import token
import tokenize
from pathlib import Path
import time

def should_keep_docstring(toktype, ttext, prev_toktype, lines):
    """
    Determine if a docstring should be kept.
    Only keep function/method docstrings, not module or class docstrings.
    """
    if toktype != token.STRING or prev_toktype != token.INDENT:
        return False

    # Look at the previous lines to see if this is a function definition
    current_line_idx = len(lines) - 1
    if current_line_idx < 1:
        return False

    # Check if the previous line contains 'def ' or 'async def '
    prev_line = lines[current_line_idx - 1].strip()
    return prev_line.startswith('def ') or prev_line.startswith('async def ')

def process_file(fname):
    """Process a single Python file to remove comments while keeping function docstrings."""
    try:
        with open(fname, 'r', encoding='utf-8') as source:
            lines = source.readlines()

        with open(fname + ',strip', 'w', encoding='utf-8') as mod:
            prev_toktype = token.INDENT
            last_lineno = -1
            last_col = 0

            tokgen = tokenize.generate_tokens(lambda: next((line for line in lines if line), ''))
            for toktype, ttext, (slineno, scol), (elineno, ecol), ltext in tokgen:
                if slineno > last_lineno:
                    last_col = 0
                if scol > last_col:
                    mod.write(" " * (scol - last_col))

                if toktype == token.STRING and should_keep_docstring(toktype, ttext, prev_toktype, lines[:slineno]):
                    # Keep function docstrings
                    mod.write(ttext)
                elif toktype == tokenize.COMMENT:
                    # Remove comments
                    pass
                else:
                    mod.write(ttext)

                prev_toktype = toktype
                last_col = ecol
                last_lineno = elineno

        # Replace original file with cleaned version
        os.replace(fname + ',strip', fname)
        return True

    except Exception as e:
        print(f"Error processing {fname}: {e}")
        return False

def find_python_files(directory):
    """Find all Python files in the given directory recursively."""
    python_files = []
    for root, dirs, files in os.walk(directory):
        # Skip common directories that shouldn't be processed
        dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', '.venv', 'node_modules', '.next']]

        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))

    return python_files

def main():
    """Main function to process all Python files."""
    if len(sys.argv) > 1:
        # Process specific file
        success = process_file(sys.argv[1])
        if success:
            print(f"Processed: {sys.argv[1]}")
        return

    # Process all Python files in current directory and subdirectories
    current_dir = os.getcwd()
    python_files = find_python_files(current_dir)

    if not python_files:
        print("No Python files found.")
        return

    print(f"Found {len(python_files)} Python files to process.")

    processed = 0
    errors = 0

    for i, file in enumerate(python_files, 1):
        print(f"Processing {i}/{len(python_files)}: {os.path.basename(file)}")
        if process_file(file):
            processed += 1
        else:
            errors += 1

        # Small delay to prevent overwhelming the system
        time.sleep(0.01)

    print(f"\nCompleted! Successfully processed {processed} files.")
    if errors > 0:
        print(f"Errors encountered: {errors} files")

if __name__ == '__main__':
    main()