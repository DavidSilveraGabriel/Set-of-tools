import os
from PIL import Image
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define supported formats and their extensions
SUPPORTED_FORMATS = {
    'PNG': '.png',
    'JPEG': '.jpg',
    'ICO': '.ico',
    'BMP': '.bmp',
    'WEBP': '.webp',
    'TIFF': '.tiff'
}

def convert_and_resize_image(input_path, output_format, resize_option='none', resize_params=None, quality=95):
    """
    Converts an image to a specified format and optionally resizes it.

    Args:
        input_path (str): Path to the input image file.
        output_format (str): The desired output format (e.g., 'PNG', 'JPEG').
        resize_option (str): Type of resizing ('none', 'absolute', 'percent', 
                               'fit_width', 'fit_height'). Defaults to 'none'.
        resize_params (dict, optional): Parameters for resizing based on resize_option.
            - 'absolute': {'width': int, 'height': int}
            - 'percent': {'scale': float} (e.g., 50 for 50%)
            - 'fit_width': {'width': int}
            - 'fit_height': {'height': int}
            Defaults to None.
        quality (int): Quality setting for JPEG format (1-100). Defaults to 95.

    Returns:
        str: The path to the saved output file on success.
        None: On failure.

    Raises:
        FileNotFoundError: If the input file does not exist.
        ValueError: If parameters are invalid (e.g., format, resize options).
        Exception: For other image processing errors.
    """
    if not os.path.exists(input_path):
        logging.error(f"Input file not found: {input_path}")
        raise FileNotFoundError(f"Input file not found: {input_path}")

    if output_format.upper() not in SUPPORTED_FORMATS:
        logging.error(f"Unsupported output format: {output_format}")
        raise ValueError(f"Unsupported output format: {output_format}. Supported formats: {list(SUPPORTED_FORMATS.keys())}")

    if resize_params is None:
        resize_params = {}

    try:
        logging.info(f"Opening image: {input_path}")
        image = Image.open(input_path)
        original_size = image.size
        logging.info(f"Original format: {image.format}, Original size: {original_size}")

        # --- Image Resizing ---
        new_size = original_size
        if resize_option != 'none':
            logging.info(f"Applying resize option: {resize_option} with params: {resize_params}")
            if resize_option == 'absolute':
                if 'width' not in resize_params or 'height' not in resize_params:
                    raise ValueError("Resize option 'absolute' requires 'width' and 'height' in resize_params.")
                new_size = (int(resize_params['width']), int(resize_params['height']))
            elif resize_option == 'percent':
                if 'scale' not in resize_params:
                    raise ValueError("Resize option 'percent' requires 'scale' in resize_params.")
                scale = float(resize_params['scale']) / 100.0
                if scale <= 0:
                    raise ValueError("Scale percentage must be positive.")
                new_size = (int(original_size[0] * scale), int(original_size[1] * scale))
            elif resize_option == 'fit_width':
                if 'width' not in resize_params:
                    raise ValueError("Resize option 'fit_width' requires 'width' in resize_params.")
                width = int(resize_params['width'])
                if width <= 0:
                     raise ValueError("Target width must be positive.")
                ratio = width / original_size[0]
                new_size = (width, int(original_size[1] * ratio))
            elif resize_option == 'fit_height':
                if 'height' not in resize_params:
                    raise ValueError("Resize option 'fit_height' requires 'height' in resize_params.")
                height = int(resize_params['height'])
                if height <= 0:
                     raise ValueError("Target height must be positive.")
                ratio = height / original_size[1]
                new_size = (int(original_size[0] * ratio), height)
            else:
                raise ValueError(f"Invalid resize_option: {resize_option}")

            # Ensure size dimensions are positive
            if new_size[0] <= 0 or new_size[1] <= 0:
                 raise ValueError(f"Calculated new size {new_size} has non-positive dimensions.")

            logging.info(f"Resizing image from {original_size} to {new_size}")
            # Use LANCZOS for high-quality downsampling
            image = image.resize(new_size, Image.Resampling.LANCZOS)
            logging.info(f"Image resized to: {image.size}")


        # --- Image Saving ---
        output_format_upper = output_format.upper()
        extension = SUPPORTED_FORMATS[output_format_upper]
        base_name = os.path.splitext(input_path)[0]
        output_path = f"{base_name}_converted{extension}"
        
        # Handle potential duplicate output filenames (simple increment)
        counter = 1
        while os.path.exists(output_path):
             output_path = f"{base_name}_converted_{counter}{extension}"
             counter += 1

        logging.info(f"Saving image to: {output_path} in format {output_format_upper}")

        save_kwargs = {'format': output_format_upper}
        if output_format_upper == 'JPEG':
            # Ensure image is in RGB mode for JPEG saving
            if image.mode == 'RGBA' or image.mode == 'P':
                 logging.info("Converting image to RGB for JPEG saving.")
                 image = image.convert('RGB')
            save_kwargs['quality'] = quality
            save_kwargs['optimize'] = True # Optional: try to optimize file size
        elif output_format_upper == 'ICO':
             # ICO saving might have specific size requirements or limitations
             # Pillow handles basic ICO saving. For multi-size icons, more complex logic needed.
             logging.warning("Basic ICO saving. For multi-resolution icons, advanced handling is required.")
             # Optionally force a common size like 32x32 if needed, but let Pillow handle default for now
             # image = image.resize((32, 32), Image.Resampling.LANCZOS)

        image.save(output_path, **save_kwargs)
        logging.info(f"Image successfully saved to {output_path}")
        return output_path

    except FileNotFoundError as e:
        logging.error(f"File not found during conversion: {e}")
        raise # Re-raise specific error
    except ValueError as e:
        logging.error(f"Value error during conversion: {e}")
        raise # Re-raise specific error
    except Exception as e:
        logging.error(f"An unexpected error occurred during image conversion: {e}", exc_info=True)
        raise Exception(f"Image processing failed: {e}") # Raise generic exception

if __name__ == '__main__':
    # Example usage for testing the core function
    print("Testing image converter core function...")
    # Create a dummy image for testing if needed, or use an existing one
    test_image_path = "test_image.png" # Replace with a real image path for actual testing
    if not os.path.exists(test_image_path):
         try:
              print(f"Creating dummy test image: {test_image_path}")
              img = Image.new('RGB', (60, 30), color = 'red')
              img.save(test_image_path)
         except Exception as e:
              print(f"Could not create dummy test image: {e}. Please provide a real image.")
              test_image_path = None

    if test_image_path:
        try:
            print("\n--- Test Case 1: Convert to JPEG, no resize ---")
            out_path = convert_and_resize_image(test_image_path, 'JPEG')
            print(f"Output: {out_path}")

            print("\n--- Test Case 2: Convert to PNG, resize absolute ---")
            out_path = convert_and_resize_image(test_image_path, 'PNG', resize_option='absolute', resize_params={'width': 100, 'height': 50})
            print(f"Output: {out_path}")

            print("\n--- Test Case 3: Convert to WEBP, resize percentage ---")
            out_path = convert_and_resize_image(test_image_path, 'WEBP', resize_option='percent', resize_params={'scale': 50})
            print(f"Output: {out_path}")

            # print("\n--- Test Case 4: Convert to ICO ---")
            # out_path = convert_and_resize_image(test_image_path, 'ICO')
            # print(f"Output: {out_path}")

            print("\n--- Test Case 5: Invalid Format ---")
            try:
                convert_and_resize_image(test_image_path, 'GIFX')
            except ValueError as e:
                print(f"Caught expected error: {e}")

        except Exception as e:
            print(f"An error occurred during testing: {e}")
    else:
        print("Skipping tests as no test image is available.")
