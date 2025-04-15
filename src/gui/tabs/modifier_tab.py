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
        self.original_image_size = None # Store original (width, height)
        self.preview_scale_factor = 1.0
        self.preview_offset_x = 0
        self.preview_offset_y = 0
        self.image_on_canvas_id = None
        self.crop_rect_id = None
        self.start_x = None
        self.start_y = None

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

        # Preview Area (Left) - Now using Canvas
        preview_frame = ttk.LabelFrame(main_area, text="Preview (Click and drag to select crop area)", padding="10")
        preview_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Use a standard tk.Canvas for drawing
        self.preview_canvas = tk.Canvas(preview_frame, bg='gray80', relief=tk.SUNKEN, borderwidth=1)
        self.preview_canvas.pack(fill=tk.BOTH, expand=True)
        self.preview_canvas.update_idletasks() # Ensure dimensions are calculated before getting size
        self._preview_max_width = self.preview_canvas.winfo_width() if self.preview_canvas.winfo_width() > 1 else 300
        self._preview_max_height = self.preview_canvas.winfo_height() if self.preview_canvas.winfo_height() > 1 else 300

        # Bind mouse events for cropping selection
        self.preview_canvas.bind("<ButtonPress-1>", self.on_canvas_press)
        self.preview_canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.preview_canvas.bind("<ButtonRelease-1>", self.on_canvas_release)

        # Placeholder text
        self._placeholder_text_id = self.preview_canvas.create_text(
            self._preview_max_width / 2, self._preview_max_height / 2,
            text="Select an image to preview", fill="gray50", anchor=tk.CENTER
        )

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
        """Loads an image, resizes it for preview, displays it on the canvas, and stores scaling info."""
        try:
            # Clear previous state
            self.clear_preview()
            self.preview_canvas.delete(self._placeholder_text_id) # Remove placeholder text

            img = Image.open(image_path)
            self.original_image_size = img.size
            original_width, original_height = self.original_image_size

            # Calculate scaling to fit canvas while maintaining aspect ratio
            canvas_width = self._preview_max_width
            canvas_height = self._preview_max_height
            scale_w = canvas_width / original_width
            scale_h = canvas_height / original_height
            self.preview_scale_factor = min(scale_w, scale_h)

            # Calculate preview dimensions and resize
            preview_width = int(original_width * self.preview_scale_factor)
            preview_height = int(original_height * self.preview_scale_factor)
            # Ensure dimensions are at least 1 pixel
            preview_width = max(1, preview_width)
            preview_height = max(1, preview_height)

            resized_img = img.resize((preview_width, preview_height), Image.Resampling.LANCZOS)
            self.preview_image_tk = ImageTk.PhotoImage(resized_img) # Keep reference

            # Calculate offset to center the image on the canvas
            self.preview_offset_x = (canvas_width - preview_width) // 2
            self.preview_offset_y = (canvas_height - preview_height) // 2

            # Draw image on canvas
            self.image_on_canvas_id = self.preview_canvas.create_image(
                self.preview_offset_x, self.preview_offset_y,
                anchor=tk.NW, image=self.preview_image_tk
            )

            # Reset crop selection
            self.crop_x.set("0")
            self.crop_y.set("0")
            self.crop_width.set(str(original_width))
            self.crop_height.set(str(original_height))


        except FileNotFoundError:
            self.status_var.set("Error: Preview file not found.")
            self.clear_preview()
        except Exception as e:
            self.status_var.set(f"Error loading preview: {e}")
            logging.warning(f"Could not load preview for {image_path}: {e}", exc_info=True)
            self.clear_preview()
            # Show error on canvas
            self.preview_canvas.create_text(
                 self._preview_max_width / 2, self._preview_max_height / 2,
                 text=f"Error loading preview:\n{e}", fill="red", anchor=tk.CENTER
            )

    def clear_preview(self):
        """Clears the preview canvas and resets related variables."""
        if self.crop_rect_id:
            self.preview_canvas.delete(self.crop_rect_id)
            self.crop_rect_id = None
        if self.image_on_canvas_id:
             self.preview_canvas.delete(self.image_on_canvas_id)
             self.image_on_canvas_id = None

        self.preview_image_tk = None # Allow garbage collection
        self.original_image_size = None
        self.preview_scale_factor = 1.0
        self.preview_offset_x = 0
        self.preview_offset_y = 0
        self.start_x = None
        self.start_y = None
        # Optionally redraw placeholder if needed, but load_and_display handles it


    # --- Canvas Mouse Event Handlers for Cropping ---

    def on_canvas_press(self, event):
        """Handles mouse button press on the canvas."""
        if not self.image_on_canvas_id: # Only allow if image is loaded
            return

        self.start_x = self.preview_canvas.canvasx(event.x)
        self.start_y = self.preview_canvas.canvasy(event.y)

        # Delete previous rectangle if it exists
        if self.crop_rect_id:
            self.preview_canvas.delete(self.crop_rect_id)

        # Create a new rectangle (initially a point)
        self.crop_rect_id = self.preview_canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline='red', dash=(4, 2) # Dashed red outline
        )

    def on_canvas_drag(self, event):
        """Handles mouse drag on the canvas."""
        if not self.crop_rect_id: # Only if selection started
            return

        current_x = self.preview_canvas.canvasx(event.x)
        current_y = self.preview_canvas.canvasy(event.y)

        # Update the rectangle coordinates
        self.preview_canvas.coords(self.crop_rect_id, self.start_x, self.start_y, current_x, current_y)

    def on_canvas_release(self, event):
        """Handles mouse button release on the canvas."""
        if not self.crop_rect_id or not self.original_image_size:
            return

        end_x = self.preview_canvas.canvasx(event.x)
        end_y = self.preview_canvas.canvasy(event.y)

        # Ensure start coordinates are top-left and end coordinates are bottom-right
        canvas_x1 = min(self.start_x, end_x)
        canvas_y1 = min(self.start_y, end_y)
        canvas_x2 = max(self.start_x, end_x)
        canvas_y2 = max(self.start_y, end_y)

        # Convert canvas coordinates back to original image coordinates
        orig_width, orig_height = self.original_image_size

        # Adjust for canvas offset and scale
        orig_x1 = (canvas_x1 - self.preview_offset_x) / self.preview_scale_factor
        orig_y1 = (canvas_y1 - self.preview_offset_y) / self.preview_scale_factor
        orig_x2 = (canvas_x2 - self.preview_offset_x) / self.preview_scale_factor
        orig_y2 = (canvas_y2 - self.preview_offset_y) / self.preview_scale_factor

        # Clamp coordinates to be within the original image bounds [0, max_dim]
        orig_x1 = max(0, orig_x1)
        orig_y1 = max(0, orig_y1)
        orig_x2 = min(orig_width, orig_x2)
        orig_y2 = min(orig_height, orig_y2)

        # Calculate original crop width and height, ensuring minimum of 1
        crop_w = max(1, int(orig_x2 - orig_x1))
        crop_h = max(1, int(orig_y2 - orig_y1))
        crop_x_final = int(orig_x1)
        crop_y_final = int(orig_y1)

        # Ensure calculated crop area doesn't exceed original bounds due to rounding
        if crop_x_final + crop_w > orig_width:
             crop_w = orig_width - crop_x_final
        if crop_y_final + crop_h > orig_height:
             crop_h = orig_height - crop_y_final

        # Update the entry fields
        self.crop_x.set(str(crop_x_final))
        self.crop_y.set(str(crop_y_final))
        self.crop_width.set(str(max(1, crop_w))) # Ensure width/height are at least 1
        self.crop_height.set(str(max(1, crop_h)))

        self.status_var.set(f"Crop area selected: X={crop_x_final}, Y={crop_y_final}, W={crop_w}, H={crop_h}")

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
