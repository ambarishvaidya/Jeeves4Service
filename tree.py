import os

def print_tree(start_path, exclude_dirs, prefix=''):
    """Prints a directory tree, excluding specified directories."""
    if os.path.basename(start_path) in exclude_dirs and os.path.isdir(start_path):
        return

    contents = []
    try:
        # os.scandir is more efficient for large directories
        with os.scandir(start_path) as entries:
            contents = sorted(entries, key=lambda entry: (entry.is_file(), entry.name.lower()))
    except (PermissionError, FileNotFoundError):
        # Handle cases where we don't have permission or dir disappears
        return

    pointers = [('├── ', '└── ')][0]

    for i, entry in enumerate(contents):
        is_last = (i == len(contents) - 1)
        pointer = pointers[1] if is_last else pointers[0]
        print(f"{prefix}{pointer}{entry.name}")

        if entry.is_dir():
            # Recursively call for subdirectories, adjusting the prefix
            new_prefix = prefix + ('    ' if is_last else '│   ')
            print_tree(entry.path, exclude_dirs, new_prefix)

if __name__ == "__main__":
    target_directory = "."  # Current directory
    excluded = {".venv", "__pycache__", "logs", ".git"} # Set of directories to exclude

    # Print the root directory itself
    print(os.path.abspath(target_directory))
    print_tree(target_directory, excluded)