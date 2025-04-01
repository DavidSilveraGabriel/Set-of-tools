import os
import logging
import numpy as np
from skimage import io, color, measure
import svgwrite
from sklearn.cluster import KMeans
from PIL import Image # For reading image dimensions if needed

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SvgConversionError(Exception):
    """Custom exception for SVG conversion errors."""
    pass

def _preprocess_image(image_path):
    """Loads and preprocesses the image."""
    try:
        # Use Pillow to open first to handle more formats reliably and get info
        with Image.open(image_path) as pil_img:
             img_format = pil_img.format
             img_mode = pil_img.mode
             logging.info(f"Opened with Pillow: format={img_format}, mode={img_mode}")
        
        # Use skimage.io for numerical processing
        img = io.imread(image_path)
        if img is None:
             raise SvgConversionError(f"skimage.io failed to read image: {image_path}")

        # Handle different image types (grayscale, RGB, RGBA)
        if img.ndim == 3 and img.shape[2] == 4:
            logging.info("Image has alpha channel, converting to RGB.")
            img = color.rgba2rgb(img) # Convert RGBA to RGB
        elif img.ndim == 2:
            logging.info("Image is grayscale.")
            # Keep as grayscale for processing, handle color conversion later if needed
            pass # img = color.gray2rgb(img) # Optionally convert to RGB
        elif img.ndim == 3 and img.shape[2] == 3:
            logging.info("Image is RGB.")
        else:
            raise SvgConversionError(f"Unsupported image format/dimensions: shape={img.shape}")

        # Ensure image data is in the expected range [0, 1] for skimage color functions
        if img.dtype == np.uint8:
            img = img.astype(np.float64) / 255.0
        elif img.dtype == np.uint16:
             img = img.astype(np.float64) / 65535.0
        elif img.dtype == np.float32 or img.dtype == np.float64:
             # Assume already in [0, 1] range, but clip just in case
             img = np.clip(img, 0, 1)
        else:
             raise SvgConversionError(f"Unsupported image data type: {img.dtype}")


        # Smoothing (optional, consider making it a parameter)
        # img_smooth = filters.gaussian(img, sigma=0.5, channel_axis=-1 if img.ndim == 3 else None)
        img_smooth = img # No smoothing for now, keep original detail

        # Color space conversions (handle grayscale)
        if img.ndim == 3:
             img_hsv = color.rgb2hsv(img)
             # img_lab = color.rgb2lab(img) # LAB might be better for color distance, but HSV used in original
        else: # Grayscale
             img_hsv = img # Keep as single channel for mask creation based on intensity
             # img_lab = color.gray2lab(img)

        return img, img_smooth, img_hsv # Return necessary processed images

    except FileNotFoundError:
        logging.error(f"Image file not found: {image_path}")
        raise
    except Exception as e:
        logging.error(f"Error preprocessing image {image_path}: {e}", exc_info=True)
        raise SvgConversionError(f"Failed to preprocess image: {e}")


def _get_dominant_colors(img, n_colors):
    """Gets dominant colors using k-means."""
    try:
        # Reshape based on dimensions (RGB or Grayscale)
        if img.ndim == 3:
            pixels = img.reshape(-1, 3)
        else: # Grayscale
            pixels = img.reshape(-1, 1)

        # Ensure n_colors is not more than unique colors (or pixels)
        unique_pixels = np.unique(pixels, axis=0)
        actual_n_colors = min(n_colors, len(unique_pixels))
        if actual_n_colors < n_colors:
             logging.warning(f"Reduced n_colors from {n_colors} to {actual_n_colors} (number of unique colors/pixels)")
        if actual_n_colors < 1:
             raise SvgConversionError("Image appears to have no unique colors.")


        kmeans = KMeans(n_clusters=actual_n_colors, random_state=0, n_init=10) # n_init='auto' in newer sklearn
        kmeans.fit(pixels)
        dominant_colors = kmeans.cluster_centers_

        # Convert back to original scale if needed (assuming input was [0,1])
        # dominant_colors_uint8 = (dominant_colors * 255).astype(np.uint8)

        logging.info(f"Found {len(dominant_colors)} dominant colors.")
        return dominant_colors # Return colors in the [0, 1] range

    except Exception as e:
        logging.error(f"Error finding dominant colors: {e}", exc_info=True)
        raise SvgConversionError(f"Failed to find dominant colors: {e}")


def _create_color_masks(img_hsv, dominant_colors, tolerance):
    """Creates binary masks for each dominant color based on tolerance in HSV space (or intensity for grayscale)."""
    masks = []
    is_grayscale = img_hsv.ndim == 2

    for color_val in dominant_colors:
        try:
            if is_grayscale:
                # For grayscale, color_val is a single intensity value [0, 1]
                center_intensity = color_val[0]
                lower_bound = np.clip(center_intensity - tolerance, 0, 1)
                upper_bound = np.clip(center_intensity + tolerance, 0, 1)
                mask = (img_hsv >= lower_bound) & (img_hsv <= upper_bound)
                # Represent grayscale color as RGB for SVG fill
                rgb_color = (np.array([center_intensity, center_intensity, center_intensity]) * 255).astype(np.uint8)

            else: # RGB -> HSV processing
                # color_val is [h, s, v] in [0, 1] range
                # Tolerance is applied more carefully in HSV space
                # Simple approach: apply tolerance to each channel (like original script)
                # More complex: consider hue wrap-around and perceptual distance
                hsv_center = color_val
                lower_bound = np.clip(hsv_center - tolerance, 0, 1)
                upper_bound = np.clip(hsv_center + tolerance, 0, 1)

                # Handle Hue wrap-around (less critical with small tolerance, but good practice)
                # If tolerance crosses 0/1 boundary for Hue, split into two ranges
                # Simplified: just apply bounds for now, like original script
                mask = np.all((img_hsv >= lower_bound) & (img_hsv <= upper_bound), axis=2)

                # Convert the dominant HSV color back to RGB for SVG fill
                rgb_color = (color.hsv2rgb(hsv_center.reshape(1, 1, 3)).flatten() * 255).astype(np.uint8)

            if np.any(mask): # Only add if the mask is not empty
                masks.append((mask, rgb_color))
            else:
                 logging.debug(f"Skipping empty mask for color {rgb_color}")

        except Exception as e:
            logging.warning(f"Could not create mask for color {color_val}: {e}", exc_info=True)
            continue # Skip this color if mask creation fails

    logging.info(f"Created {len(masks)} non-empty color masks.")
    return masks


def _get_contours(mask, simplify_tolerance):
    """Finds contours in a binary mask."""
    # Pad mask to ensure contours on edges are closed
    padded_mask = np.pad(mask, pad_width=1, mode='constant', constant_values=0)
    # Find contours using marching squares algorithm
    contours = measure.find_contours(padded_mask.astype(float), level=0.5, fully_connected='low') # level=0.5 for binary

    simplified_contours = []
    for contour in contours:
        # Subtract padding offset
        contour -= 1
        # Simplify contour using Douglas-Peucker algorithm
        simplified = measure.approximate_polygon(contour, tolerance=simplify_tolerance)
        if len(simplified) > 2: # Need at least 3 points for a polygon
            simplified_contours.append(simplified)

    logging.debug(f"Found {len(contours)} contours, simplified to {len(simplified_contours)}.")
    return simplified_contours


def _contour_to_svg_path(contour):
    """Converts a contour (list of [row, col] points) to an SVG path string."""
    if len(contour) < 2:
        return ""
    # SVG uses (x, y) which corresponds to (col, row)
    path_data = "M " + " L ".join(f"{point[1]:.2f},{point[0]:.2f}" for point in contour)
    # Close the path if it's likely a closed contour
    if np.allclose(contour[0], contour[-1]):
         path_data += " Z" # Close path command
    return path_data


def _rgb_to_hex(rgb_color):
    """Converts an RGB tuple/list/array (0-255) to hex string."""
    return '#{:02x}{:02x}{:02x}'.format(*map(int, rgb_color))


def convert_image_to_svg(image_path, output_path=None, options=None):
    """
    Converts a raster image to an SVG file by vectorizing color regions.

    Args:
        image_path (str): Path to the input raster image.
        output_path (str, optional): Path to save the output SVG file.
            If None, defaults to '<image_name>_converted.svg'.
        options (dict, optional): Conversion parameters:
            'n_colors' (int): Number of dominant colors to find (default: 5).
            'tolerance' (float): Tolerance for grouping colors (HSV/intensity space, default: 0.2).
            'opacity' (float): Fill opacity for SVG paths (0.0-1.0, default: 1.0).
            'simplify_tolerance' (float): Tolerance for simplifying contours (default: 0.5).

    Returns:
        str: The path to the saved SVG file on success.

    Raises:
        FileNotFoundError: If the input image is not found.
        SvgConversionError: For errors during the conversion process.
        Exception: For other unexpected errors.
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Input image not found: {image_path}")

    # Default options
    default_options = {
        'n_colors': 5,
        'tolerance': 0.2,
        'opacity': 1.0, # Default to full opacity
        'simplify_tolerance': 0.5
    }
    if options:
        default_options.update(options)
    
    opts = default_options
    logging.info(f"Starting SVG conversion for '{image_path}' with options: {opts}")

    try:
        # 1. Preprocess Image
        img, img_smooth, img_hsv = _preprocess_image(image_path)
        height, width = img.shape[:2]
        logging.info(f"Image dimensions: {width}x{height}")

        # 2. Get Dominant Colors
        dominant_colors = _get_dominant_colors(img_smooth, opts['n_colors'])

        # 3. Create Color Masks
        color_masks = _create_color_masks(img_hsv, dominant_colors, opts['tolerance'])
        if not color_masks:
             raise SvgConversionError("No color regions found after masking. Try adjusting tolerance or n_colors.")

        # 4. Setup SVG Drawing
        if output_path is None:
            base_name = os.path.splitext(image_path)[0]
            output_path = f"{base_name}_converted.svg"
            # Handle potential duplicate output filenames
            counter = 1
            while os.path.exists(output_path):
                 output_path = f"{base_name}_converted_{counter}.svg"
                 counter += 1

        dwg = svgwrite.Drawing(output_path, profile='tiny', size=(f"{width}px", f"{height}px"))
        dwg.viewbox(0, 0, width, height)
        # Optional: Add background rectangle if needed
        # dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), fill='white'))

        # 5. Process Masks and Create SVG Paths
        total_paths = 0
        for mask, rgb_color in color_masks:
            contours = _get_contours(mask, opts['simplify_tolerance'])
            hex_color = _rgb_to_hex(rgb_color)
            logging.debug(f"Processing color {hex_color}, found {len(contours)} contours.")

            for contour in contours:
                path_data = _contour_to_svg_path(contour)
                if path_data:
                    dwg.add(dwg.path(
                        d=path_data,
                        fill=hex_color,
                        fill_opacity=opts['opacity'],
                        stroke='none' # No stroke by default
                    ))
                    total_paths += 1

        if total_paths == 0:
             raise SvgConversionError("No valid contours found to generate SVG paths.")

        # 6. Save SVG
        dwg.save(pretty=True) # Use pretty=True for readable output
        logging.info(f"SVG conversion successful. Saved {total_paths} paths to: {output_path}")
        return output_path

    except (FileNotFoundError, SvgConversionError) as e:
        logging.error(f"SVG conversion failed: {e}")
        raise # Re-raise specific errors
    except Exception as e:
        logging.error(f"An unexpected error occurred during SVG conversion: {e}", exc_info=True)
        raise Exception(f"SVG conversion failed unexpectedly: {e}") # Raise generic exception


if __name__ == '__main__':
    # Example usage for testing the core function
    print("Testing SVG converter core function...")
    test_image_path = "test_image.png" # Replace with a real image path for actual testing
    if not os.path.exists(test_image_path):
         try:
              print(f"Creating dummy test image: {test_image_path}")
              img = Image.new('RGB', (60, 30), color = 'blue')
              # Add another color block
              img.paste('red', (30,0,60,30))
              img.save(test_image_path)
         except Exception as e:
              print(f"Could not create dummy test image: {e}. Please provide a real image.")
              test_image_path = None

    if test_image_path:
        try:
            print("\n--- Test Case 1: Default options ---")
            options1 = {}
            out_path1 = convert_image_to_svg(test_image_path, options=options1)
            print(f"Output SVG (default): {out_path1}")

            print("\n--- Test Case 2: More colors, different tolerance ---")
            options2 = {'n_colors': 8, 'tolerance': 0.1, 'simplify_tolerance': 1.0, 'opacity': 0.8}
            out_path2 = convert_image_to_svg(test_image_path, output_path="test_image_custom.svg", options=options2)
            print(f"Output SVG (custom): {out_path2}")

        except Exception as e:
            print(f"An error occurred during testing: {e}")
    else:
        print("Skipping tests as no test image is available.")
