import os
import platform
import subprocess
import ctypes
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FolderIconError(Exception):
    """Custom exception for folder icon setting errors."""
    pass

def is_admin():
    """Checks if the script is running with administrator privileges."""
    try:
        if platform.system() == "Windows":
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        elif platform.system() == "Darwin" or platform.system() == "Linux":
            # On Unix-like systems, check if effective user ID is 0 (root)
            return os.geteuid() == 0
        else:
            return False # Assume not admin on unsupported systems
    except AttributeError:
         # Handle systems without geteuid (like some Windows environments without ctypes)
         return False
    except Exception as e:
        logging.warning(f"Could not determine admin status: {e}")
        return False

def set_folder_icon(icon_path, folder_path):
    """
    Sets a custom icon for a specified folder, handling OS differences.

    Args:
        icon_path (str): Path to the icon file (.ico for Windows, .icns for macOS).
        folder_path (str): Path to the target folder.

    Returns:
        bool: True if the icon was set successfully, False otherwise.

    Raises:
        FileNotFoundError: If the icon or folder path does not exist.
        ValueError: If paths are not valid files/folders or icon extension is wrong.
        FolderIconError: For OS-specific errors during the process (e.g., permissions, command failures).
        NotImplementedError: If run on an unsupported OS (like Linux in this context).
    """
    logging.info(f"Attempting to set icon '{icon_path}' for folder '{folder_path}'")
    system = platform.system()
    logging.debug(f"Detected OS: {system}")

    # --- Validations ---
    if not os.path.isfile(icon_path):
        raise FileNotFoundError(f"Icon file not found or is not a file: '{icon_path}'")
    if not os.path.isdir(folder_path):
        raise FileNotFoundError(f"Folder path not found or is not a directory: '{folder_path}'")

    # --- OS Specific Logic ---
    if system == "Windows":
        ext_expected = ".ico"
        if not icon_path.lower().endswith(ext_expected):
            raise ValueError(f"Invalid icon extension for Windows. Expected '{ext_expected}', got '{os.path.splitext(icon_path)[1]}'")
        return _set_icon_windows(icon_path, folder_path)

    elif system == "Darwin": # macOS
        ext_expected = ".icns"
        if not icon_path.lower().endswith(ext_expected):
             # macOS can sometimes use other image types, but .icns is standard for folder icons via script
             logging.warning(f"Icon file '{icon_path}' is not a standard .icns file. Proceeding, but might not work as expected.")
             # raise ValueError(f"Invalid icon extension for macOS. Expected '{ext_expected}', got '{os.path.splitext(icon_path)[1]}'")
        return _set_icon_macos(icon_path, folder_path)

    elif system == "Linux":
        raise NotImplementedError("Setting persistent folder icons via this script is not supported on Linux.")
    else:
        raise NotImplementedError(f"Unsupported operating system: {system}")


def _set_icon_windows(icon_path, folder_path):
    """Sets folder icon on Windows using desktop.ini and attrib."""
    logging.debug("Executing Windows icon setting logic.")
    desktop_ini_path = os.path.join(folder_path, "desktop.ini")
    icon_path_abs = os.path.abspath(icon_path) # Use absolute path in desktop.ini

    # Check for admin rights if desktop.ini exists (might need overwrite)
    needs_admin_warning = False
    if os.path.exists(desktop_ini_path) and not is_admin():
        logging.warning("desktop.ini exists and not running as admin. Overwrite might fail.")
        needs_admin_warning = True # GUI can use this info

    # Content for desktop.ini
    desktop_ini_content = f"""[.ShellClassInfo]
IconResource={icon_path_abs},0
[ViewState]
Mode=
Vid=
FolderType=Generic
"""
    try:
        # Ensure desktop.ini is writable (remove read-only, system, hidden first)
        if os.path.exists(desktop_ini_path):
            logging.debug(f"Removing attributes from existing: {desktop_ini_path}")
            subprocess.run(['attrib', '-s', '-h', '-r', desktop_ini_path], check=False, shell=True) # Use check=False, handle errors below

        # Write the new desktop.ini
        logging.debug(f"Writing desktop.ini content to {desktop_ini_path}")
        with open(desktop_ini_path, "w", encoding="utf-8") as f:
            f.write(desktop_ini_content)

        # Set attributes for desktop.ini (System, Hidden)
        logging.debug(f"Setting attributes +s +h for {desktop_ini_path}")
        result_ini = subprocess.run(['attrib', '+s', '+h', desktop_ini_path], check=True, shell=True, capture_output=True, text=True)
        logging.debug(f"Attrib desktop.ini result: {result_ini.stdout or result_ini.stderr}")


        # Set attribute for the folder itself (System or Read-only usually triggers icon refresh)
        # Using +s (System) is common practice for custom folder icons
        logging.debug(f"Setting attribute +s for folder {folder_path}")
        result_folder = subprocess.run(['attrib', '+s', folder_path], check=True, shell=True, capture_output=True, text=True)
        logging.debug(f"Attrib folder result: {result_folder.stdout or result_folder.stderr}")

        logging.info(f"Windows icon set successfully for {folder_path}")
        # Return success and whether an admin warning might be relevant
        return True, needs_admin_warning

    except FileNotFoundError as e: # e.g., attrib command not found
         logging.error(f"Command not found during Windows icon setting: {e}")
         raise FolderIconError(f"Required command 'attrib' not found or failed: {e}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Attrib command failed: {e.stderr}")
        raise FolderIconError(f"Failed to set attributes: {e.stderr}")
    except IOError as e:
        logging.error(f"Failed to write desktop.ini: {e}")
        raise FolderIconError(f"Could not write to {desktop_ini_path}. Check permissions. Error: {e}")
    except Exception as e:
        logging.exception("Unexpected error during Windows icon setting.")
        raise FolderIconError(f"An unexpected error occurred on Windows: {e}")


def _set_icon_macos(icon_path, folder_path):
    """Sets folder icon on macOS using osascript."""
    logging.debug("Executing macOS icon setting logic.")

    # Escape paths for shell command
    icon_path_escaped = icon_path.replace('"', '\\"')
    folder_path_escaped = folder_path.replace('"', '\\"')

    # AppleScript command
    osascript_command = f"""
    set theFolder to POSIX file "{folder_path_escaped}"
    set theIconFile to POSIX file "{icon_path_escaped}"
    try
        tell application "Finder"
            set icon of item theFolder to image file theIconFile
        end tell
        return "Success"
    on error errMsg number errorNumber
        return "Error: " & errMsg & " (" & errorNumber & ")"
    end try
    """
    logging.debug("Running osascript command...")
    try:
        process = subprocess.Popen(['osascript', '-e', osascript_command],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   text=True)
        stdout, stderr = process.communicate(timeout=15) # Add timeout

        if process.returncode != 0 or "Error:" in stdout or stderr:
            error_msg = stdout.strip() if "Error:" in stdout else stderr.strip()
            logging.error(f"osascript failed: {error_msg}")
            raise FolderIconError(f"Failed to set icon on macOS: {error_msg}")
        else:
            logging.info(f"osascript successful: {stdout.strip()}")
            # Optionally try to refresh Finder (might require permissions or fail silently)
            try:
                logging.debug("Attempting to restart Finder to refresh icons...")
                subprocess.run(['killall', 'Finder'], check=False, timeout=5)
            except Exception as e:
                logging.warning(f"Could not restart Finder (this is often optional): {e}")
            return True, False # Success, no admin warning relevant here

    except FileNotFoundError:
        logging.error("osascript command not found.")
        raise FolderIconError("osascript command not found. Ensure macOS development tools are installed.")
    except subprocess.TimeoutExpired:
         logging.error("osascript command timed out.")
         raise FolderIconError("Setting icon on macOS timed out.")
    except Exception as e:
        logging.exception("Unexpected error during macOS icon setting.")
        raise FolderIconError(f"An unexpected error occurred on macOS: {e}")


if __name__ == '__main__':
    # Example usage for testing the core function
    print("Testing folder icon setter core function...")
    test_icon = "test.ico" # Replace with actual .ico/.icns path
    test_folder = "test_folder" # Replace with actual folder path

    if not os.path.exists(test_folder):
        os.makedirs(test_folder, exist_ok=True)
        print(f"Created test folder: {test_folder}")

    if not os.path.exists(test_icon):
        print(f"Test icon '{test_icon}' not found. Skipping tests.")
    else:
        try:
            print(f"\n--- Test Case: Set icon for '{test_folder}' ---")
            success, warning = set_folder_icon(test_icon, test_folder)
            print(f"Result: Success={success}, Admin Warning Needed={warning}")
            if success:
                 print(f"Icon for '{test_folder}' should be set (may require manual refresh).")
            else:
                 print("Icon setting failed.")

        except (FileNotFoundError, ValueError, FolderIconError, NotImplementedError) as e:
            print(f"Caught expected error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred during testing: {e}")
