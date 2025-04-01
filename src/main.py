# import tkinter as tk # Replaced by ThemedTk
from ttkthemes import ThemedTk # Import ThemedTk
from gui.main_window import MainWindow

if __name__ == "__main__":
    # Use ThemedTk to apply a theme globally at startup
    root = ThemedTk(theme="equilux") # Apply 'equilux' theme
    app = MainWindow(root)
    root.mainloop()
