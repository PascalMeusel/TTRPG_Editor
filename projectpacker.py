import os

# --- Configuration ---
OUTPUT_FILENAME = "project_snapshot.txt"
EXCLUDED_DIRS = {".git", "venv", "__pycache__", ".idea", ".vscode"}
EXCLUDED_FILES = {OUTPUT_FILENAME, "project_snapshot.txt.py", ".gitignore"}

def write_directory_tree(start_path, output_file, exclusions):
    """Walks through the directory and writes a tree structure to the file."""
    for root, dirs, files in os.walk(start_path, topdown=True):
        # Exclude specified directories from traversal
        dirs[:] = [d for d in dirs if d not in exclusions]
        
        level = root.replace(start_path, '').count(os.sep)
        indent = ' ' * 4 * (level)
        output_file.write(f'{indent}📂 {os.path.basename(root)}/\n')
        
        sub_indent = ' ' * 4 * (level + 1)
        for f in sorted(files):
            if f not in exclusions:
                output_file.write(f'{sub_indent}📄 {f}\n')

def write_python_files_content(start_path, output_file, exclusions):
    """Walks through the directory and appends the content of all .py files."""
    for root, dirs, files in os.walk(start_path, topdown=True):
        # Exclude specified directories
        dirs[:] = [d for d in dirs if d not in exclusions]
        
        for f in sorted(files):
            if f.endswith('.py') and f not in exclusions:
                file_path = os.path.join(root, f)
                relative_path = os.path.relpath(file_path, start_path)
                
                output_file.write("\n" + "="*80 + "\n")
                output_file.write(f"--- FILE: {relative_path} ---\n")
                output_file.write("="*80 + "\n\n")
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as py_file:
                        output_file.write(py_file.read())
                except Exception as e:
                    output_file.write(f"*** ERROR READING FILE: {e} ***")
                output_file.write("\n")

def main():
    """Main function to generate the project snapshot."""
    start_path = '.'
    try:
        with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("PROJECT DIRECTORY STRUCTURE\n")
            f.write("="*80 + "\n\n")
            write_directory_tree(start_path, f, EXCLUDED_DIRS)
            
            f.write("\n\n" + "="*80 + "\n")
            f.write("PYTHON FILE CONTENTS\n")
            f.write("="*80 + "\n")
            write_python_files_content(start_path, f, EXCLUDED_DIRS.union(EXCLUDED_FILES))

        print(f"✅ Successfully created '{OUTPUT_FILENAME}'")
        print("You can now send the content of this file in the next chat.")

    except Exception as e:
        print(f"❌ An error occurred: {e}")

if __name__ == "__main__":
    main()
