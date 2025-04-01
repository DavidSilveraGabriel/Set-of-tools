import tkinter as tk
from tkinter import ttk, messagebox
import os
import logging
from PIL import Image, ImageTk
import threading # To run conversion in background

from ..utils import file_helpers
from ..core import svg_converter

class SvgTab:
    def __init__(self, master_frame):
        self.frame = master_frame
        self.current_image_path = tk.StringVar()
        self.status_var = tk.StringVar(value="Ready")
        self.photo = None # To keep a reference to the PhotoImage

        # Conversion Options
        self.n_colors = tk.IntVar(value=5)
        self.tolerance = tk.DoubleVar(value=0.2)
        self.opacity = tk.DoubleVar(value=1.0) # Default to 1.0
        self.simplify_tolerance = tk.DoubleVar(value=0.5)

        # --- Layout ---
        # Main container split left (preview/buttons) and right (options)
        main_container = ttk.Frame(self.frame)
        main_container.pack(fill=tk.BOTH, expand=True)

        left_frame = ttk.Frame(main_container)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        right_frame = ttk.Frame(main_container)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)

        self.setup_left_frame(left_frame)
        self.setup_right_frame(right_frame)

        # Bind resize event to redraw image
        self.canvas.bind('<Configure>', self.on_canvas_resize)


    def setup_left_frame(self, parent):
        # Image Preview Area
        image_frame = ttk.LabelFrame(parent, text="Image Preview", padding="10")
        image_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.canvas = tk.Canvas(image_frame, bg='gray80', relief=tk.SUNKEN, borderwidth=1)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        # Placeholder text on canvas
        self.canvas_text_id = self.canvas.create_text(10, 10, anchor=tk.NW, text="Select an image to preview", fill="gray50")


        # File Selection and Action Buttons Frame
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=10)

        select_button = ttk.Button(button_frame, text="Select Image", command=self.select_image)
        select_button.pack(side=tk.LEFT, padx=(0, 10))

        self.convert_button = ttk.Button(button_frame, text="Convert to SVG", command=self.run_conversion)
        self.convert_button.pack(side=tk.LEFT)
        self.convert_button.config(state='disabled') # Disable until image is selected

        # Status Bar (at the bottom of the parent frame)
        status_label = ttk.Label(parent, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_label.pack(side=tk.BOTTOM, fill=tk.X, ipady=2, pady=(10,0))


    def setup_right_frame(self, parent):
        options_frame = ttk.LabelFrame(parent, text="Conversion Options", padding="10")
        options_frame.pack(fill=tk.BOTH, expand=True)

        # Helper to create slider controls
        def create_option_control(label_text, variable, min_val, max_val, resolution):
            f = ttk.Frame(options_frame)
            f.pack(fill=tk.X, pady=5)
            lbl = ttk.Label(f, text=f"{label_text}:")
            lbl.pack(side=tk.LEFT)
            val_lbl = ttk.Label(f, textvariable=variable, width=4) # Show current value
            val_lbl.pack(side=tk.RIGHT, padx=(5,0))
            scale = ttk.Scale(f, from_=min_val, to=max_val, variable=variable, orient=tk.HORIZONTAL, resolution=resolution)
            scale.pack(fill=tk.X, expand=True, side=tk.RIGHT)

        create_option_control("Num Colors", self.n_colors, 2, 16, 1)
        create_option_control("Color Tolerance", self.tolerance, 0.01, 0.5, 0.01)
        create_option_control("Opacity", self.opacity, 0.1, 1.0, 0.05)
        create_option_control("Simplify Tolerance", self.simplify_tolerance, 0.1, 2.0, 0.1)

        reset_button = ttk.Button(options_frame, text="Reset Defaults", command=self.reset_options)
        reset_button.pack(pady=15)

    def reset_options(self):
        self.n_colors.set(5)
        self.tolerance.set(0.2)
        self.opacity.set(1.0)
        self.simplify_tolerance.set(0.5)
        self.status_var.set("Options reset to defaults.")

    def select_image(self):
        path = file_helpers.select_image_file()
        if path:
            self.current_image_path.set(path)
            self.display_image(path)
            self.status_var.set(f"Selected: {os.path.basename(path)}")
            self.convert_button.config(state='normal') # Enable convert button

    def display_image(self, image_path):
        try:
            # Clear previous image and text
            self.canvas.delete("all")

            image = Image.open(image_path)
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()

            # Prevent division by zero if canvas not yet rendered
            if canvas_width <= 1 or canvas_height <= 1:
                 canvas_width = 300 # Default size
                 canvas_height = 300

            img_width, img_height = image.size
            if img_width <= 0 or img_height <= 0:
                 raise ValueError("Invalid image dimensions")

            # Calculate aspect ratio preserving size
            ratio = min(canvas_width / img_width, canvas_height / img_height)
            new_width = max(1, int(img_width * ratio * 0.95)) # Ensure positive size, add padding
            new_height = max(1, int(img_height * ratio * 0.95))

            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.photo = ImageTk.PhotoImage(image) # Keep reference

            # Center image on canvas
            x = (canvas_width - new_width) // 2
            y = (canvas_height - new_height) // 2
            self.canvas.create_image(x, y, image=self.photo, anchor=tk.NW)

        except Exception as e:
            self.status_var.set(f"Error displaying image: {e}")
            messagebox.showerror("Image Display Error", f"Could not display image:\n{e}", parent=self.frame)
            logging.error(f"Failed to display image {image_path}: {e}", exc_info=True)
            self.canvas.delete("all") # Clear canvas on error
            self.canvas_text_id = self.canvas.create_text(10, 10, anchor=tk.NW, text="Error loading preview", fill="red")


    def on_canvas_resize(self, event):
        # Rescale and redraw image when canvas size changes
        path = self.current_image_path.get()
        if path and os.path.exists(path):
            # Debounce or delay might be needed for rapid resizing
            self.display_image(path)
        elif self.canvas_text_id:
             # Re-center placeholder text if no image
             try:
                  self.canvas.coords(self.canvas_text_id, event.width // 2, event.height // 2)
                  self.canvas.itemconfig(self.canvas_text_id, anchor=tk.CENTER)
             except tk.TclError: # Handle case where canvas/text item might be destroyed
                  pass


    def _conversion_thread_task(self, in_path, options):
        """Task to run in a separate thread."""
        try:
            output_path = svg_converter.convert_image_to_svg(
                image_path=in_path,
                options=options
            )
            self.frame.after(0, self._on_conversion_success, output_path) # Schedule GUI update in main thread
        except Exception as e:
            self.frame.after(0, self._on_conversion_error, e) # Schedule GUI update in main thread

    def _on_conversion_success(self, output_path):
        """Callback for successful conversion (runs in main thread)."""
        self.status_var.set(f"Success! Saved as: {os.path.basename(output_path)}")
        messagebox.showinfo("Success", f"Image converted successfully!\nSaved to: {output_path}", parent=self.frame)
        self.convert_button.config(state='normal') # Re-enable button

    def _on_conversion_error(self, error):
        """Callback for failed conversion (runs in main thread)."""
        self.status_var.set(f"Error: {error}")
        messagebox.showerror("Conversion Error", f"Failed to convert image:\n{error}", parent=self.frame)
        logging.error(f"SVG Conversion failed: {error}", exc_info=True)
        self.convert_button.config(state='normal') # Re-enable button


    def run_conversion(self):
        in_path = self.current_image_path.get()
        if not in_path:
            messagebox.showerror("Error", "Please select an input image first.", parent=self.frame)
            return

        options = {
            'n_colors': self.n_colors.get(),
            'tolerance': self.tolerance.get(),
            'opacity': self.opacity.get(),
            'simplify_tolerance': self.simplify_tolerance.get()
        }

        self.status_var.set("Processing SVG...")
        self.convert_button.config(state='disabled') # Disable button during processing
        self.frame.update_idletasks()

        # Run conversion in a separate thread to avoid freezing the GUI
        thread = threading.Thread(target=self._conversion_thread_task, args=(in_path, options))
        thread.daemon = True # Allow program to exit even if thread is running
        thread.start()


# Example usage for testing the tab independently
if __name__ == '__main__':
    root = tk.Tk()
    root.title("SVG Converter Tab Test")
    root.geometry("800x600")

    style = ttk.Style()
    style.theme_use('clam')

    main_frame = ttk.Frame(root, padding="10")
    main_frame.pack(expand=True, fill='both')

    svg_tab = SvgTab(main_frame)

    root.mainloop()
