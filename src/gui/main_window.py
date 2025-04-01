import tkinter as tk
from tkinter import ttk
# Import tab modules later when they are created
# from .tabs.converter_tab import ConverterTab
# from .tabs.icon_setter_tab import IconSetterTab
# from .tabs.svg_tab import SvgTab

class MainWindow:
    def __init__(self, master):
        self.master = master
        master.title("Multi-Tool Suite")
        master.geometry("800x600") # Adjust size as needed

        # Configure style (optional, can be refined later)
        style = ttk.Style()
        # Example theme, can be changed
        style.theme_use('clam') 

        # Create the Notebook (tabbed interface)
        self.notebook = ttk.Notebook(master)
        self.notebook.pack(pady=10, padx=10, expand=True, fill='both')

        # --- Create Tab Frames ---
        # These frames will hold the content for each tool
        self.converter_frame = ttk.Frame(self.notebook, padding="10")
        self.icon_setter_frame = ttk.Frame(self.notebook, padding="10")
        self.svg_frame = ttk.Frame(self.notebook, padding="10")

        # --- Add Tabs to Notebook ---
        self.notebook.add(self.converter_frame, text='Format Converter')
        self.notebook.add(self.icon_setter_frame, text='Folder Icon Setter')
        self.notebook.add(self.svg_frame, text='Image to SVG')

        # --- Populate Tabs ---
        # This will be done by instantiating the tab classes later
        # ConverterTab(self.converter_frame)
        # IconSetterTab(self.icon_setter_frame)
        # SvgTab(self.svg_frame)

        print("Main window initialized.") # Placeholder

if __name__ == '__main__':
    # This allows testing the main window structure independently
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()
