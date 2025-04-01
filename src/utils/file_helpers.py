import tkinter as tk
from tkinter import filedialog
import platform
import logging

# Basic logging setup (can be configured more centrally later)
logging.basicConfig(level=logging.INFO)

def select_image_file(title="Select Image"):
    """Opens a dialog to select a common image file."""
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    file_path = filedialog.askopenfilename(
        title=title,
        filetypes=[
            ("Images", "*.png *.jpg *.jpeg *.bmp *.gif *.ico *.webp *.tiff"),
            ("All files", "*.*")
        ]
    )
    root.destroy() # Clean up the temporary root window
    if file_path:
        logging.info(f"Image file selected: {file_path}")
    else:
        logging.info("Image file selection cancelled.")
    return file_path

def select_icon_file(title="Select Icon File"):
    """Opens a dialog to select an OS-specific icon file."""
    root = tk.Tk()
    root.withdraw()
    sistema_operativo = platform.system()
    if sistema_operativo == "Windows":
        filetypes = (("Icon files", "*.ico"), ("All files", "*.*"))
    elif sistema_operativo == "Darwin":  # macOS
        filetypes = (("ICNS files", "*.icns"), ("All files", "*.*"))
    else:  # Linux or other (though icon setting isn't supported there in the original script)
        filetypes = (("All files", "*.*"),)

    file_path = filedialog.askopenfilename(title=title, filetypes=filetypes)
    root.destroy()
    if file_path:
        logging.info(f"Icon file selected: {file_path}")
    else:
        logging.info("Icon file selection cancelled.")
    return file_path

def select_folder(title="Select Folder"):
    """Opens a dialog to select a folder."""
    root = tk.Tk()
    root.withdraw()
    folder_path = filedialog.askdirectory(title=title)
    root.destroy()
    if folder_path:
        logging.info(f"Folder selected: {folder_path}")
    else:
        logging.info("Folder selection cancelled.")
    return folder_path

if __name__ == '__main__':
    # Example usage for testing
    print("Testing file helpers...")
    # img_path = select_image_file()
    # print(f"Selected image: {img_path}")
    # icon_path = select_icon_file()
    # print(f"Selected icon: {icon_path}")
    # folder_path = select_folder()
    # print(f"Selected folder: {folder_path}")
    print("Testing complete (commented out to avoid GUI popups during automated runs).")
