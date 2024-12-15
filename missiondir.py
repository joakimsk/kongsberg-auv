import os
from tkinter import Tk
from tkinter.filedialog import askdirectory

def get_open_access_filepaths():
    # Hide the root Tkinter window
    Tk().withdraw()

    # Open a dialog to select the root directory
    root_folder = askdirectory(title="Select Root Folder")
    if not root_folder:
        print("No folder selected. Exiting.")
        return []

    # Directories to exclude
    relative_exclusions = [
        os.path.join(root_folder, "HiSASRaw"),
        os.path.join(root_folder, "post", "HISAS"),
        os.path.join(root_folder, "pp", "EM2040")
    ]

    keyword_exclusions = [
        "restricted_access"
    ]

    # List to store the filtered file paths
    filtered_files = []

    # Walk through the root folder
    for dirpath, dirnames, filenames in os.walk(root_folder):
        # Check if the directory is in exclusions
        if any(dirpath.startswith(exclusion) for exclusion in relative_exclusions):
            continue

        # Filter out directories with keyword exclusions
        dirnames[:] = [d for d in dirnames if not any(keyword in d for keyword in keyword_exclusions)]

        # Add files in the current directory to the list
        for file in filenames:
            filtered_files.append(os.path.join(dirpath, file))

    return filtered_files

def get_restricted_access_filepaths():
    # Hide the root Tkinter window
    Tk().withdraw()

    # Open a dialog to select the root directory
    root_folder = askdirectory(title="Select Root Folder")
    if not root_folder:
        print("No folder selected. Exiting.")
        return []

    # Directories to exclude
    relative_exclusions = [
    ]

    keyword_exclusions = [
    ]

    # List to store the filtered file paths
    filtered_files = []

    # Walk through the root folder
    for dirpath, dirnames, filenames in os.walk(root_folder):
        # Check if the directory is in exclusions
        if any(dirpath.startswith(exclusion) for exclusion in relative_exclusions):
            continue

        # Filter out directories with keyword exclusions
        dirnames[:] = [d for d in dirnames if not any(keyword in d for keyword in keyword_exclusions)]

        # Add files in the current directory to the list
        for file in filenames:
            filtered_files.append(os.path.join(dirpath, file))

    return filtered_files

# Example usage
if __name__ == "__main__":
    filtered_file_paths = get_open_access_filepaths()
    if filtered_file_paths:
        print("Filtered Files:")
        for file_path in filtered_file_paths:
            print(file_path)
    else:
        print("No files found or operation cancelled.")
