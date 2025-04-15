import tkinter as tk
from tkinter import ttk, messagebox
import os
import logging
from PIL import Image, ImageTk
from utils import file_helpers
from core import image_modifier

class ModifierTab:
    def __init__(self, master_frame):
        self.frame = master_frame
        self.input_path = tk.StringVar()
        self.status_var = tk.StringVar(value="Ready")
        self.preview_image_tk = None

        # Resize parameters
        self.resize_width = tk.StringVar()
        self.resize_height = tk.StringVar()
        self.keep_aspect = tk.BooleanVar(value=True)

        # Crop parameters
        self.crop_x = tk.StringVar(value="0")
        self.crop_y = tk.StringVar(value="0")
        self.crop_width = tk.StringVar()
        self.crop_height = tk.StringVar()

        # --- Layout ---
        # Top frame for file selection
        input_frame = ttk.LabelFrame(self.frame, text="Input Image", padding="10")
        input_frame.pack(fill=tk.X, pady=5)

        input_entry = ttk.Entry(input_frame, textvariable=self.input_path, state='readonly', width=60)
        input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        input_button = ttk.Button(input_frame, text="Browse...", command=self.select_input_file)
        input_button.pack(side=tk.LEFT)

        # Main area split: Preview on left, Controls on right
        main_area = ttk.Frame(self.frame)
        main_area.pack(fill=tk.BOTH, expand=True, pady=5)

        # Preview Area (Left)
        preview_frame = ttk.LabelFrame(main_area, text="Preview", padding="10")
        preview_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        self.preview_label = ttk.Label(preview_frame, text="Select an image to preview", anchor=tk.CENTER)
        self.preview_label.pack(fill=tk.BOTH, expand=True)
        preview_frame.update_idletasks()
        self._preview_max_width = preview_frame.winfo_width() if preview_frame.winfo_width() > 1 else 300
        self._preview_max_height = preview_frame.winfo_height() if preview_frame.winfo_height() > 1 else 300

        # Controls Area (Right)
        controls_frame = ttk.Frame(main_area)
        controls_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # Resize Controls
        resize_frame = ttk.LabelFrame(controls_frame, text="Resize", padding="10")
        resize_frame.pack(fill=tk.X, pady=5)

        ttk.Label(resize_frame, text="Width:").grid(row=0, column=0, padx=5, pady=2, sticky=tk.W)
        ttk.Entry(resize_frame, textvariable=self.resize_width, width=7).grid(row=0, column=1, padx=5, pady=2)
        ttk.Label(resize_frame, text="Height:").grid(row=1, column=0, padx=5, pady=2, sticky=tk.W)
        ttk.Entry(resize_frame, textvariable=self.resize_height, width=7).grid(row=1, column=1, padx=5, pady=2)
        ttk.Checkbutton(resize_frame, text="Keep Aspect Ratio", variable=self.keep_aspect).grid(row=2, column=0, columnspan=2, pady=5)
        resize_button = ttk.Button(resize_frame, text="Resize Image", command=self.run_resize)
        resize_button.grid(row=3, column=0, columnspan=2, pady=10)

        # Crop Controls
        crop_frame = ttk.LabelFrame(controls_frame, text="Crop", padding="10")
        crop_frame.pack(fill=tk.X, pady=5)

        ttk.Label(crop_frame, text="X:").grid(row=0, column=0, padx=5, pady=2, sticky=tk.W)
        ttk.Entry(crop_frame, textvariable=self.crop_x, width=7).grid(row=0, column=1, padx=5, pady=2)
        ttk.Label(crop_frame, text="Y:").grid(row=1, column=0, padx=5, pady=2, sticky=tk.W)
        ttk.Entry(crop_frame, textvariable=self.crop_y, width=7).grid(row=1, column=1, padx=5, pady=2)
        ttk.Label(crop_frame, text="Width:").grid(row=2, column=0, padx=5, pady=2, sticky=tk.W)
        ttk.Entry(crop_frame, textvariable=self.crop_width, width=7).grid(row=2, column=1, padx=5, pady=2)
        ttk.Label(crop_frame, text="Height:").grid(row=3, column=0, padx=5, pady=2, sticky=tk.W)
        ttk.Entry(crop_frame, textvariable=self.crop_height, width=7).grid(row=3, column=1, padx=5, pady=2)
        crop_button = ttk.Button(crop_frame, text="Crop Image", command=self.run_crop)
        crop_button.grid(row=4, column=0, columnspan=2, pady=10)

        # Status Bar
        status_label = ttk.Label(self.frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_label.pack(side=tk.BOTTOM, fill=tk.X, ipady=2, pady=(10,0))

    def select_input_file(self):
        path = file_helpers.select_image_file()
        if path:
            self.input_path.set(path)
            self.status_var.set(f"Selected: {os.path.basename(path)}")
            self.load_and_display_preview(path)
            # Populate crop dimensions based on image size
            try:
                with Image.open(path) as img:
                    width, height = img.size
                    self.crop_width.set(str(width))
                    self.crop_height.set(str(height))
                    self.resize_width.set(str(width)) # Also set initial resize values
                    self.resize_height.set(str(height))
            except Exception as e:
                logging.warning(f"Could not read image dimensions for defaults: {e}")
                self.crop_width.set("")
                self.crop_height.set("")
                self.resize_width.set("")
                self.resize_height.set("")


    def load_and_display_preview(self, image_path):
        """Loads an image, resizes it for preview, and displays it."""
        try:
            max_width = self._preview_max_width
            max_height = self._preview_max_height

            img = Image.open(image_path)
            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

            self.preview_image_tk = ImageTk.PhotoImage(img) # Keep reference

            self.preview_label.config(image=self.preview_image_tk, text="") # Display image, clear text
            self.preview_label.image = self.preview_image_tk # Keep reference for label too

        except FileNotFoundError:
            self.status_var.set("Error: Preview file not found.")
            self.clear_preview()
        except Exception as e:
            self.status_var.set(f"Error loading preview: {e}")
            logging.warning(f"Could not load preview for {image_path}: {e}", exc_info=True)
            self.clear_preview()

    def clear_preview(self):
        """Clears the preview area."""
        self.preview_label.config(image='', text="Select an image to preview")
        self.preview_label.image = None
        self.preview_image_tk = None

    def _get_output_path(self, suffix):
        """Generates an output path based on input path and suffix."""
        in_path = self.input_path.get()
        if not in_path:
            return None
        directory, filename = os.path.split(in_path)
        name, ext = os.path.splitext(filename)
        # Use the same directory as input, add suffix
        return os.path.join(directory, f"{name}_{suffix}{ext}")

    def run_resize(self):
        in_path = self.input_path.get()
        if not in_path:
            messagebox.showerror("Error", "Please select an input image.", parent=self.frame)
            return

        try:
            width_str = self.resize_width.get()
            height_str = self.resize_height.get()
            width = int(width_str) if width_str else None
            height = int(height_str) if height_str else None
            keep_aspect = self.keep_aspect.get()

            if width is None and height is None:
                 messagebox.showerror("Error", "Please enter at least Width or Height for resizing.", parent=self.frame)
                 return

            output_path = self._get_output_path("resized")
            if not output_path: return # Should not happen if in_path is set

            self.status_var.set("Resizing...")
            self.frame.update_idletasks()

            result_path = image_modifier.resize_image(
                input_path=in_path,
                output_path=output_path,
                width=width,
                height=height,
                keep_aspect_ratio=keep_aspect
            )

            if result_path:
                self.status_var.set(f"Success! Resized image saved as: {os.path.basename(result_path)}")
                messagebox.showinfo("Success", f"Image resized successfully!\nSaved to: {result_path}", parent=self.frame)
            # Errors are raised as exceptions by the core function

        except ValueError as e:
            self.status_var.set(f"Error: {e}")
            messagebox.showerror("Input Error", str(e), parent=self.frame)
        except Exception as e:
            self.status_var.set(f"Error: {e}")
            messagebox.showerror("Resize Error", f"An unexpected error occurred:\n{e}", parent=self.frame)
            logging.error(f"Resize failed: {e}", exc_info=True)
        finally:
             # Re-enable button or indicate completion if needed
             pass


    def run_crop(self):
        in_path = self.input_path.get()
        if not in_path:
            messagebox.showerror("Error", "Please select an input image.", parent=self.frame)
            return

        try:
            x = int(self.crop_x.get())
            y = int(self.crop_y.get())
            width = int(self.crop_width.get())
            height = int(self.crop_height.get())

            output_path = self._get_output_path("cropped")
            if not output_path: return

            self.status_var.set("Cropping...")
            self.frame.update_idletasks()

            result_path = image_modifier.crop_image(
                input_path=in_path,
                output_path=output_path,
                x=x,
                y=y,
                width=width,
                height=height
            )

            if result_path:
                self.status_var.set(f"Success! Cropped image saved as: {os.path.basename(result_path)}")
                messagebox.showinfo("Success", f"Image cropped successfully!\nSaved to: {result_path}", parent=self.frame)
            # Errors are raised as exceptions

        except ValueError as e:
            self.status_var.set(f"Error: {e}")
            messagebox.showerror("Input Error", str(e), parent=self.frame)
        except Exception as e:
            self.status_var.set(f"Error: {e}")
            messagebox.showerror("Crop Error", f"An unexpected error occurred:\n{e}", parent=self.frame)
            logging.error(f"Crop failed: {e}", exc_info=True)
        finally:
            # Re-enable button or indicate completion if needed
            pass


# Example usage for testing the tab independently
if __name__ == '__main__':
    # Use ThemedTk for consistency if available
    try:
        from ttkthemes import ThemedTk
        root = ThemedTk(theme="equilux") # Or your preferred theme
    except ImportError:
        root = tk.Tk()

    root.title("Modifier Tab Test")
    root.geometry("800x600") # Adjust size as needed

    main_frame = ttk.Frame(root, padding="10")
    main_frame.pack(expand=True, fill='both')

    modifier_tab = ModifierTab(main_frame)

    root.mainloop()
