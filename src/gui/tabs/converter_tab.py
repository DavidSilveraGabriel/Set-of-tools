import tkinter as tk
from tkinter import ttk, messagebox
import os
import logging
from ..utils import file_helpers
from ..core import image_converter

class ConverterTab:
    def __init__(self, master_frame):
        self.frame = master_frame
        self.input_path = tk.StringVar()
        self.output_format = tk.StringVar()
        self.resize_option = tk.StringVar(value='none') # Default to no resize
        self.resize_width = tk.StringVar()
        self.resize_height = tk.StringVar()
        self.resize_scale = tk.StringVar()
        self.jpeg_quality = tk.IntVar(value=95)
        self.status_var = tk.StringVar(value="Ready")

        # --- UI Elements ---
        # Input File Selection
        input_frame = ttk.LabelFrame(self.frame, text="Input Image", padding="10")
        input_frame.pack(fill=tk.X, pady=5)

        input_entry = ttk.Entry(input_frame, textvariable=self.input_path, state='readonly', width=60)
        input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        input_button = ttk.Button(input_frame, text="Browse...", command=self.select_input_file)
        input_button.pack(side=tk.LEFT)

        # Output Format Selection
        format_frame = ttk.LabelFrame(self.frame, text="Output Format", padding="10")
        format_frame.pack(fill=tk.X, pady=5)

        format_label = ttk.Label(format_frame, text="Select format:")
        format_label.pack(side=tk.LEFT, padx=(0, 5))
        format_options = list(image_converter.SUPPORTED_FORMATS.keys())
        format_dropdown = ttk.Combobox(format_frame, textvariable=self.output_format, values=format_options, state='readonly')
        format_dropdown.pack(side=tk.LEFT, padx=5)
        format_dropdown.set(format_options[0] if format_options else '') # Default to first option

        # JPEG Quality (conditional visibility can be added later if needed)
        quality_label = ttk.Label(format_frame, text="JPEG Quality (1-100):")
        quality_label.pack(side=tk.LEFT, padx=(15, 5))
        quality_spinbox = ttk.Spinbox(format_frame, from_=1, to=100, textvariable=self.jpeg_quality, width=5)
        quality_spinbox.pack(side=tk.LEFT)


        # Resizing Options
        resize_main_frame = ttk.LabelFrame(self.frame, text="Resizing Options", padding="10")
        resize_main_frame.pack(fill=tk.X, pady=5)

        # Radio buttons for resize type
        resize_options_frame = ttk.Frame(resize_main_frame)
        resize_options_frame.pack(fill=tk.X)

        ttk.Radiobutton(resize_options_frame, text="None", variable=self.resize_option, value='none', command=self.update_resize_fields).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(resize_options_frame, text="Absolute (W x H)", variable=self.resize_option, value='absolute', command=self.update_resize_fields).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(resize_options_frame, text="Percentage", variable=self.resize_option, value='percent', command=self.update_resize_fields).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(resize_options_frame, text="Fit Width", variable=self.resize_option, value='fit_width', command=self.update_resize_fields).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(resize_options_frame, text="Fit Height", variable=self.resize_option, value='fit_height', command=self.update_resize_fields).pack(side=tk.LEFT, padx=5)

        # Input fields for resize parameters (initially disabled)
        self.resize_params_frame = ttk.Frame(resize_main_frame)
        self.resize_params_frame.pack(fill=tk.X, pady=(10, 0))

        self.width_label = ttk.Label(self.resize_params_frame, text="Width:")
        self.width_entry = ttk.Entry(self.resize_params_frame, textvariable=self.resize_width, width=7, state='disabled')
        self.height_label = ttk.Label(self.resize_params_frame, text="Height:")
        self.height_entry = ttk.Entry(self.resize_params_frame, textvariable=self.resize_height, width=7, state='disabled')
        self.scale_label = ttk.Label(self.resize_params_frame, text="Scale (%):")
        self.scale_entry = ttk.Entry(self.resize_params_frame, textvariable=self.resize_scale, width=7, state='disabled')

        # Pack the parameter fields (they will be shown/hidden by update_resize_fields)
        self.width_label.pack(side=tk.LEFT, padx=(0, 2))
        self.width_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.height_label.pack(side=tk.LEFT, padx=(0, 2))
        self.height_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.scale_label.pack(side=tk.LEFT, padx=(0, 2))
        self.scale_entry.pack(side=tk.LEFT, padx=(0, 10))

        # Initially hide all parameter fields
        self.width_label.pack_forget()
        self.width_entry.pack_forget()
        self.height_label.pack_forget()
        self.height_entry.pack_forget()
        self.scale_label.pack_forget()
        self.scale_entry.pack_forget()


        # Action Button
        action_frame = ttk.Frame(self.frame)
        action_frame.pack(fill=tk.X, pady=20)
        convert_button = ttk.Button(action_frame, text="Convert Image", command=self.run_conversion)
        convert_button.pack()

        # Status Bar
        status_label = ttk.Label(self.frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_label.pack(side=tk.BOTTOM, fill=tk.X, ipady=2)

    def select_input_file(self):
        path = file_helpers.select_image_file()
        if path:
            self.input_path.set(path)
            self.status_var.set(f"Selected: {os.path.basename(path)}")

    def update_resize_fields(self):
        """Enable/disable resize parameter fields based on selected option."""
        option = self.resize_option.get()

        # Hide all first
        self.width_label.pack_forget()
        self.width_entry.pack_forget()
        self.height_label.pack_forget()
        self.height_entry.pack_forget()
        self.scale_label.pack_forget()
        self.scale_entry.pack_forget()

        # Disable all entries
        self.width_entry.config(state='disabled')
        self.height_entry.config(state='disabled')
        self.scale_entry.config(state='disabled')

        # Show and enable relevant fields
        if option == 'absolute':
            self.width_label.pack(side=tk.LEFT, padx=(0, 2))
            self.width_entry.pack(side=tk.LEFT, padx=(0, 10))
            self.height_label.pack(side=tk.LEFT, padx=(0, 2))
            self.height_entry.pack(side=tk.LEFT, padx=(0, 10))
            self.width_entry.config(state='normal')
            self.height_entry.config(state='normal')
        elif option == 'percent':
            self.scale_label.pack(side=tk.LEFT, padx=(0, 2))
            self.scale_entry.pack(side=tk.LEFT, padx=(0, 10))
            self.scale_entry.config(state='normal')
        elif option == 'fit_width':
            self.width_label.pack(side=tk.LEFT, padx=(0, 2))
            self.width_entry.pack(side=tk.LEFT, padx=(0, 10))
            self.width_entry.config(state='normal')
        elif option == 'fit_height':
            self.height_label.pack(side=tk.LEFT, padx=(0, 2))
            self.height_entry.pack(side=tk.LEFT, padx=(0, 10))
            self.height_entry.config(state='normal')
        # 'none' requires no fields

    def run_conversion(self):
        in_path = self.input_path.get()
        out_format = self.output_format.get()
        resize_opt = self.resize_option.get()
        quality = self.jpeg_quality.get()

        if not in_path:
            messagebox.showerror("Error", "Please select an input image.", parent=self.frame)
            return
        if not out_format:
            messagebox.showerror("Error", "Please select an output format.", parent=self.frame)
            return

        resize_params = {}
        try:
            if resize_opt == 'absolute':
                resize_params['width'] = int(self.resize_width.get())
                resize_params['height'] = int(self.resize_height.get())
            elif resize_opt == 'percent':
                resize_params['scale'] = float(self.resize_scale.get())
            elif resize_opt == 'fit_width':
                resize_params['width'] = int(self.resize_width.get())
            elif resize_opt == 'fit_height':
                resize_params['height'] = int(self.resize_height.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid resize parameter. Please enter numbers.", parent=self.frame)
            return

        self.status_var.set("Processing...")
        self.frame.update_idletasks() # Update GUI to show status

        try:
            output_path = image_converter.convert_and_resize_image(
                input_path=in_path,
                output_format=out_format,
                resize_option=resize_opt,
                resize_params=resize_params,
                quality=quality
            )
            if output_path:
                self.status_var.set(f"Success! Saved as: {os.path.basename(output_path)}")
                messagebox.showinfo("Success", f"Image converted successfully!\nSaved to: {output_path}", parent=self.frame)
            else:
                # Should not happen if exceptions are raised correctly
                self.status_var.set("Failed. Unknown error.")
                messagebox.showerror("Error", "Conversion failed for an unknown reason.", parent=self.frame)

        except FileNotFoundError as e:
             self.status_var.set(f"Error: Input file not found.")
             messagebox.showerror("Error", str(e), parent=self.frame)
        except ValueError as e:
             self.status_var.set(f"Error: Invalid parameter.")
             messagebox.showerror("Error", str(e), parent=self.frame)
        except Exception as e:
            self.status_var.set(f"Error: {e}")
            messagebox.showerror("Error", f"An unexpected error occurred:\n{e}", parent=self.frame)
            logging.error(f"Conversion failed: {e}", exc_info=True)

# Example usage for testing the tab independently
if __name__ == '__main__':
    root = tk.Tk()
    root.title("Converter Tab Test")
    root.geometry("600x400")
    
    style = ttk.Style()
    style.theme_use('clam') 

    main_frame = ttk.Frame(root, padding="10")
    main_frame.pack(expand=True, fill='both')
    
    converter_tab = ConverterTab(main_frame)
    
    root.mainloop()
