import tkinter as tk
from tkinter import ttk, messagebox
import os
import platform
import logging
from ..utils import file_helpers
from ..core import folder_icon_setter

class IconSetterTab:
    def __init__(self, master_frame):
        self.frame = master_frame
        self.icon_path = tk.StringVar()
        self.folder_path = tk.StringVar()
        self.status_var = tk.StringVar(value="Ready")
        self.admin_warning_var = tk.StringVar(value="") # For Windows admin warning

        # --- UI Elements ---
        # OS Info
        os_info_frame = ttk.Frame(self.frame)
        os_info_frame.pack(fill=tk.X, pady=(0, 10))
        os_label = ttk.Label(os_info_frame, text=f"Detected OS: {platform.system()}")
        os_label.pack(side=tk.LEFT)

        # Admin Status (Windows specific)
        if platform.system() == "Windows":
            if not folder_icon_setter.is_admin():
                self.admin_warning_var.set("Note: Run as administrator for best results if modifying system folders or existing icons.")
            admin_label = ttk.Label(os_info_frame, textvariable=self.admin_warning_var, foreground="orange", wraplength=400)
            admin_label.pack(side=tk.LEFT, padx=10)


        # Icon File Selection
        icon_frame = ttk.LabelFrame(self.frame, text="Icon File", padding="10")
        icon_frame.pack(fill=tk.X, pady=5)

        icon_entry = ttk.Entry(icon_frame, textvariable=self.icon_path, state='readonly', width=60)
        icon_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        icon_button = ttk.Button(icon_frame, text="Browse...", command=self.select_icon)
        icon_button.pack(side=tk.LEFT)

        # Folder Selection
        folder_frame = ttk.LabelFrame(self.frame, text="Target Folder", padding="10")
        folder_frame.pack(fill=tk.X, pady=5)

        folder_entry = ttk.Entry(folder_frame, textvariable=self.folder_path, state='readonly', width=60)
        folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        folder_button = ttk.Button(folder_frame, text="Browse...", command=self.select_folder)
        folder_button.pack(side=tk.LEFT)

        # Action Button
        action_frame = ttk.Frame(self.frame)
        action_frame.pack(fill=tk.X, pady=20)
        apply_button = ttk.Button(action_frame, text="Apply Icon to Folder", command=self.run_apply_icon)
        apply_button.pack()

        # Status Bar
        status_label = ttk.Label(self.frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_label.pack(side=tk.BOTTOM, fill=tk.X, ipady=2)

        # Disable functionality if OS is not supported by core logic
        if platform.system() not in ["Windows", "Darwin"]:
             apply_button.config(state='disabled')
             self.status_var.set(f"Icon setting not supported on {platform.system()}")


    def select_icon(self):
        path = file_helpers.select_icon_file() # Uses the OS-specific dialog
        if path:
            self.icon_path.set(path)
            self.status_var.set(f"Selected Icon: {os.path.basename(path)}")

    def select_folder(self):
        path = file_helpers.select_folder()
        if path:
            self.folder_path.set(path)
            self.status_var.set(f"Selected Folder: {os.path.basename(path)}")

    def run_apply_icon(self):
        icon_p = self.icon_path.get()
        folder_p = self.folder_path.get()

        if not icon_p:
            messagebox.showerror("Error", "Please select an icon file.", parent=self.frame)
            return
        if not folder_p:
            messagebox.showerror("Error", "Please select a target folder.", parent=self.frame)
            return

        self.status_var.set("Processing...")
        self.frame.update_idletasks()

        try:
            success, needs_admin_warning = folder_icon_setter.set_folder_icon(icon_p, folder_p)

            if success:
                self.status_var.set("Success! Icon applied. (May require folder refresh)")
                info_message = "Icon applied successfully!"
                if platform.system() == "Windows":
                     info_message += "\nYou might need to refresh the folder view (F5) or restart Explorer to see the change."
                elif platform.system() == "Darwin":
                     info_message += "\nFinder may have been restarted to apply changes."

                # Add admin warning if relevant on Windows
                if platform.system() == "Windows" and needs_admin_warning:
                     info_message += "\n\nWarning: Running without administrator rights might prevent changes if desktop.ini was already present."

                messagebox.showinfo("Success", info_message, parent=self.frame)
            else:
                 # This case might not be reached if errors raise exceptions
                 self.status_var.set("Failed. Unknown error.")
                 messagebox.showerror("Error", "Failed to set icon for an unknown reason.", parent=self.frame)

        except (FileNotFoundError, ValueError, folder_icon_setter.FolderIconError, NotImplementedError) as e:
             self.status_var.set(f"Error: {e}")
             messagebox.showerror("Error", str(e), parent=self.frame)
             logging.error(f"Icon setting failed: {e}")
        except Exception as e:
            self.status_var.set(f"Error: An unexpected error occurred.")
            messagebox.showerror("Error", f"An unexpected error occurred:\n{e}", parent=self.frame)
            logging.exception("Unexpected error during icon application.")


# Example usage for testing the tab independently
if __name__ == '__main__':
    root = tk.Tk()
    root.title("Icon Setter Tab Test")
    root.geometry("600x400")

    style = ttk.Style()
    style.theme_use('clam')

    main_frame = ttk.Frame(root, padding="10")
    main_frame.pack(expand=True, fill='both')

    icon_setter_tab = IconSetterTab(main_frame)

    root.mainloop()
