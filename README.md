# Set-of-Tools

A personal repository for storing a set of practical tools, primarily focused on image processing and manipulation.

## Overview

This repository contains two main applications:

1. `image-to-svg.py`: A tool to convert raster images (PNG, JPG, etc.) to vector SVG format.
2. `remove-bg.py`: A tool to remove backgrounds from images using a deep learning model.

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

4. **Install PyTorch:**

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

## Project Structure

* `README.md`: This file.
* `requirements.txt`: Lists project dependencies.
* `image-to-svg.py`: Source code for the Image to SVG converter application.
* `remove-bg.py`: Source code for the Background Remover application.

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
* The deep learning model is composed of classes such as `REBNCONV`, `RSU7`, `RSU6`, `RSU5`, `RSU4`, and `U2NET`.

### `requirements.txt`

This file lists all the Python dependencies required for running the application. It includes libraries for image processing, numerical computation, machine learning, and UI functionalities.

## Contributing

This is a personal project, but contributions and suggestions are welcome. Feel free to fork the repository, make changes, and submit pull requests.

## License

This project is licensed under the **Apache License 2.0**.
