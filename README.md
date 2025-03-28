# Set-of-Tools

A personal repository for storing a set of practical tools, primarily focused on image processing and manipulation, and system utilities.

## Overview

This repository contains a collection of useful applications:

1. `image-to-svg.py`: A tool to convert raster images (PNG, JPG, etc.) to vector SVG format.
2. `remove-bg.py`: A tool to remove backgrounds from images using a deep learning model.
3. `icons_for_folders.py`: A utility to change folder icons to custom icons on Windows and macOS.
4. `image-format-converter.py`: A tool to convert images between various image formats.
5. `LLM_Crawl4AI.ipynb`: A Google Colab notebook for crawling websites based on sitemaps using `crawl4ai`, extracting content, and saving it as Markdown.

## Setup

### Prerequisites

* Python 3.7+
* pip (Python package installer)

### Installation

1. **Clone the repository:**

    ```bash
    git clone [repository_url]
    cd set-of-tools
    ```

2. **Create and activate a virtual environment:**

    ```bash
    py -m venv venv   # On Windows
    # python3 -m venv venv # On Linux or Mac
    ```

    **On Windows:**

    ```bash
    venv\Scripts\activate
    ```

    **On Linux/Mac:**

    ```bash
    source venv/bin/activate
    ```

3. **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Install PyTorch (for background remover):**

    ```bash
    pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cpu
    ```

## Usage

### Image to SVG Converter

1. Run `image-to-svg.py`:

    ```bash
    python image-to-svg.py
    ```

2. Use the GUI to load an image and adjust conversion parameters (number of colors, tolerance, etc.).
3. Click "Convert" to start the conversion.

### Background Remover

1. Run `remove-bg.py`:

    ```bash
    python remove-bg.py
    ```

2. Use the GUI to load an image.
3. Adjust parameters if needed, and then click "Process" to remove the background.
4. Save the modified image, if needed.

### Folder Icon Changer

1. Run `icons_for_folders.py`:

    ```bash
    python icons_for_folders.py
    ```

2. Use the GUI to select an icon file (.ico for Windows, .icns for macOS).
3. Select the target folder to apply the custom icon.
4. Click "Apply Icon to Folder".
   *Note: Folder icon customization on Linux is not persistently supported by this script.*

### Image Format Converter

1. Run `image-format-converter.py`:

    ```bash
    python image-format-converter.py
    ```

2. Use the GUI to load an image.
3. Select the desired output format from the dropdown menu.
4. Click "Convert" to start the conversion.
5. Choose the save location and filename for the converted image.

### Web Crawler (Google Colab Notebook)

1. Open `LLM_Crawl4AI.ipynb` in Google Colaboratory.
2. Run the first cell (`#@title Run this cell`) to install dependencies and import necessary libraries. This might take a moment.
3. Run the second cell (`#@title Configuration and functions`) to define the crawler class and helper functions.
4. Run the third cell (`#@title RUN`) to display the configuration UI.
5. Configure the crawler using the UI widgets:
    * Set the `Sitemap URL`.
    * Specify the `Output File` path (within the Colab environment, e.g., `/content/output.md`).
    * Adjust `Concurrency`, `Timeout`, `Min Words`, and `Pruning` density as needed.
    * Optionally change the `Log File` path.
6. Click the "Start Crawling" button.
7. Monitor the progress bar and status messages.
8. Once completed, the output Markdown file will be automatically downloaded by your browser (if successful and the file is not empty). The log file path will also be displayed.

## Project Structure

* `README.md`: This file.
* `requirements.txt`: Lists project dependencies for the Python scripts.
* `LLM_Crawl4AI.ipynb`: Google Colab notebook for web crawling.
* `image-to-svg.py`: Source code for the Image to SVG converter application.
* `remove-bg.py`: Source code for the Background Remover application.
* `icons_for_folders.py`: Source code for the Folder Icon Changer utility.
* `image-format-converter.py`: Source code for the Image Format Converter tool.
* `.gitignore`: Specifies intentionally untracked files that Git should ignore.
* `LICENSE`: Contains the license information for the project (Apache License 2.0).


## Detailed Description of Files

### `image-to-svg.py`

This file contains the source code for the image-to-SVG converter application. It leverages the tkinter library for the GUI.

* It has a class `ModernImageToSvgConverter` that handles most of the functionalities.
* It allows the user to select images with a GUI file browser, display the selected image on a canvas and has controls to configure parameters like `n_colors`, `tolerance`, `opacity`, and `simplify_tolerance`.
* It includes buttons to trigger different functions such as image selection and conversion, that can also be styled with a custom style.

### `remove-bg.py`

This file provides the source code for a background removal tool that uses a pre-trained deep-learning model.

* This file has the `ModernBackgroundRemover` class, that handles most of the app's logic
* The main purpose of this application is to remove the background of a given image using a pre-trained deep learning model based on the U-Net architecture.
* It uses PyTorch for the deep learning model and has functions to handle the pre-processing and post-processing of the image.
* It implements a basic GUI using tkinter, where users can load an image, process it to remove the background, crop it and save it.
* The deep learning model is composed of classes such as `REBNCONV`, `RSU7`, `RSU6`, `RSU5`, `RSU4`, and `U2NET` (defined in separate modules if modularized).

### `icons_for_folders.py`

This file implements a GUI application to change the icons of folders.

* It uses `tkinter` for the graphical interface, allowing users to select both an icon file and a target folder.
* Supports different icon formats based on the operating system: `.ico` for Windows and `.icns` for macOS.
* On Windows, it modifies the `desktop.ini` file within the target folder and uses `attrib` commands to set system and hidden attributes.
* On macOS, it utilizes AppleScript via `subprocess` to interact with Finder and set the folder icon.
* Provides error handling and user feedback through message boxes.

### `image-format-converter.py`

This script provides a GUI application for converting images between different formats.

* Built with `tkinter` for the user interface.
* Allows users to select an input image file and choose an output format from a dropdown list.
* Uses the Pillow (PIL) library to handle image loading and saving in various formats.
* Supports common image formats such as PNG, JPG, BMP, GIF, and TIFF, among others supported by Pillow.
* Provides a user-friendly interface for simple image format conversions.

### `LLM_Crawl4AI.ipynb`

This Jupyter Notebook is designed to run in Google Colaboratory and provides a web crawling utility.

* It utilizes the `crawl4ai` library to asynchronously crawl URLs found in a specified sitemap XML file.
* Uses `httpx` for asynchronous HTTP requests to fetch the sitemap and web pages.
* Employs `ipywidgets` to create an interactive UI within the Colab environment for configuring crawl parameters (sitemap URL, output file, concurrency, timeouts, content pruning settings).
* Leverages `playwright` (installed within Colab) for browser automation if needed by `crawl4ai` for JavaScript rendering.
* Processes the scraped HTML content, filters it based on word count and pruning density, and converts the relevant parts to Markdown format using `crawl4ai`'s built-in features.
* Includes detailed logging to a file within the Colab environment for debugging purposes.
* Manages the crawling process in a separate thread to keep the UI responsive.
* Provides real-time progress updates and status messages via the UI.
* Automatically triggers a file download in the browser upon successful completion.

### `requirements.txt`

This file lists all the Python dependencies required for running the Python script applications (`.py` files) in this repository. It includes libraries primarily for:

* Image processing: `Pillow`, `opencv-python`, `scikit-image`, `imageio`
* SVG manipulation: `svgwrite`, `svglib`
* Numerical computation: `numpy`, `scipy`
* Machine learning (for background removal): `torch`, `torchvision`, `torchaudio`
* User interface: `tkinter` (Note: `ttkthemes` might be used but isn't explicitly listed in the base `requirements.txt`)
* General utilities: `os`, `platform`, `logging`, etc. (implicitly used)

**Note:** The `LLM_Crawl4AI.ipynb` notebook has its own dependencies (`crawl4ai`, `httpx`, `ipywidgets`, `playwright`, etc.) which are installed directly within the Google Colab environment when running the notebook's setup cell. They are not listed in this `requirements.txt` file.

## Contributing

This is a personal project, but contributions and suggestions are welcome. Feel free to fork the repository, make changes, and submit pull requests.

## License

This project is licensed under the **Apache License 2.0**.
