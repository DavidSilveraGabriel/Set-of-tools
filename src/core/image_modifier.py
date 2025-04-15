import os
from PIL import Image, UnidentifiedImageError
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def resize_image(input_path: str, output_path: str, width: int = None, height: int = None, keep_aspect_ratio: bool = True):
    """
    Resizes an image to the specified dimensions.

    Args:
        input_path: Path to the input image.
        output_path: Path to save the resized image.
        width: Target width in pixels. If None, calculated from height if keep_aspect_ratio is True.
        height: Target height in pixels. If None, calculated from width if keep_aspect_ratio is True.
        keep_aspect_ratio: If True, maintains the original aspect ratio. One dimension (width or height) must be provided.
                           If False, stretches the image to the exact width and height. Both must be provided.

    Returns:
        The output path if successful, None otherwise.

    Raises:
        FileNotFoundError: If the input file does not exist.
        ValueError: If parameters are invalid (e.g., no dimensions, invalid dimensions).
        UnidentifiedImageError: If the input file is not a valid image.
        Exception: For other image processing errors.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    if not width and not height:
        raise ValueError("At least one dimension (width or height) must be provided for resizing.")
    if not keep_aspect_ratio and (not width or not height):
        raise ValueError("Both width and height must be provided when keep_aspect_ratio is False.")
    if (width is not None and width <= 0) or (height is not None and height <= 0):
        raise ValueError("Width and height must be positive integers.")

    try:
        with Image.open(input_path) as img:
            original_width, original_height = img.size
            target_width = width
            target_height = height

            if keep_aspect_ratio:
                aspect_ratio = original_width / original_height
                if width and not height:
                    target_height = max(1, int(width / aspect_ratio))
                elif height and not width:
                    target_width = max(1, int(height * aspect_ratio))
                elif width and height: # Both provided, use the dimension that results in a smaller image to fit within bounds
                    ratio_w = width / original_width
                    ratio_h = height / original_height
                    if ratio_w < ratio_h:
                        target_width = width
                        target_height = max(1, int(width / aspect_ratio))
                    else:
                        target_height = height
                        target_width = max(1, int(height * aspect_ratio))
            else:
                # Use exact dimensions provided when not keeping aspect ratio
                target_width = width
                target_height = height


            logging.info(f"Resizing '{input_path}' from {original_width}x{original_height} to {target_width}x{target_height}")
            resized_img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)

            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            resized_img.save(output_path)
            logging.info(f"Resized image saved to '{output_path}'")
            return output_path

    except UnidentifiedImageError:
        logging.error(f"Cannot identify image file: {input_path}")
        raise UnidentifiedImageError(f"Invalid or unsupported image file: {input_path}")
    except Exception as e:
        logging.error(f"Error resizing image {input_path}: {e}", exc_info=True)
        raise Exception(f"Failed to resize image: {e}")


def crop_image(input_path: str, output_path: str, x: int, y: int, width: int, height: int):
    """
    Crops an image to the specified bounding box.

    Args:
        input_path: Path to the input image.
        output_path: Path to save the cropped image.
        x: The left coordinate (x) of the crop box.
        y: The top coordinate (y) of the crop box.
        width: The width of the crop box.
        height: The height of the crop box.

    Returns:
        The output path if successful, None otherwise.

    Raises:
        FileNotFoundError: If the input file does not exist.
        ValueError: If crop coordinates or dimensions are invalid.
        UnidentifiedImageError: If the input file is not a valid image.
        Exception: For other image processing errors.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    if width <= 0 or height <= 0:
        raise ValueError("Crop width and height must be positive.")
    if x < 0 or y < 0:
        raise ValueError("Crop coordinates (x, y) cannot be negative.")

    try:
        with Image.open(input_path) as img:
            original_width, original_height = img.size

            # Define the crop box (left, upper, right, lower)
            box_left = x
            box_upper = y
            box_right = x + width
            box_lower = y + height

            # Validate crop box boundaries
            if box_right > original_width or box_lower > original_height:
                raise ValueError(f"Crop area ({box_left},{box_upper},{box_right},{box_lower}) exceeds image dimensions ({original_width}x{original_height}).")

            logging.info(f"Cropping '{input_path}' to box ({box_left}, {box_upper}, {box_right}, {box_lower})")
            cropped_img = img.crop((box_left, box_upper, box_right, box_lower))

            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            cropped_img.save(output_path)
            logging.info(f"Cropped image saved to '{output_path}'")
            return output_path

    except UnidentifiedImageError:
        logging.error(f"Cannot identify image file: {input_path}")
        raise UnidentifiedImageError(f"Invalid or unsupported image file: {input_path}")
    except Exception as e:
        logging.error(f"Error cropping image {input_path}: {e}", exc_info=True)
        raise Exception(f"Failed to crop image: {e}")
