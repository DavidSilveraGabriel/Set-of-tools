# Set-of-Tools

A personal repository for storing a set of practical tools, primarily focused on image processing and manipulation, and system utilities, now refactored into a unified GUI application.

## Overview

This repository contains a collection of useful applications integrated into a single interface:

1.  **Image Format Converter:** Converts images between various formats (PNG, JPEG, WEBP, etc.) and allows resizing.
2.  **Folder Icon Setter:** Changes folder icons to custom icons on Windows (.ico) and macOS (.icns).
3.  **Image to SVG Converter:** Converts raster images (PNG, JPG, etc.) to vector SVG format using color quantization and contour tracing.

Additionally, it includes:

4.  `notebooks/LLM_Crawl4AI.ipynb`: A Google Colab notebook for crawling websites based on sitemaps using `crawl4ai`, extracting content, and saving it as Markdown.

*(Note: The previous background removal tool has been removed).*

## Setup

### Prerequisites

*   Python 3.7+ (Tested with Python 3.x)
*   pip (Python package installer)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone [repository_url]
    cd set-of-tools
    ```

2.  **Create and activate a virtual environment (Recommended):**
    ```bash
    # Windows
    python -m venv .venv
    .venv\Scripts\activate

    # macOS/Linux
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: The PyTorch installation step is no longer required).*

## Usage

### Main Application (Image Tools)

1.  Ensure your virtual environment is activated and dependencies are installed.
2.  Run the main application from the project root directory:
    ```bash
    python src/main.py
    ```
3.  The application window will open with tabs for each tool:
    *   **Format Converter:** Select an input image, choose the desired output format and resizing options, then click "Convert Image".
    *   **Folder Icon Setter:** Select an icon file (.ico/.icns) and a target folder, then click "Apply Icon to Folder". Note OS-specific requirements and potential need for admin rights on Windows.
    *   **Image to SVG:** Select an input image, adjust conversion parameters (colors, tolerance, opacity, simplification) as needed, then click "Convert to SVG".

### Web Crawler (Google Colab Notebook)

1.  Open `notebooks/LLM_Crawl4AI.ipynb` in Google Colaboratory.
2.  Follow the instructions within the notebook cells to install dependencies, configure, and run the crawler.

## Project Structure

```
set-of-tools/
├── src/                     # Source code for the GUI application
│   ├── core/                # Core processing logic (no GUI elements)
│   │   ├── __init__.py
│   │   ├── image_converter.py
│   │   ├── folder_icon_setter.py
│   │   └── svg_converter.py
│   ├── gui/                 # GUI components (Tkinter)
│   │   ├── __init__.py
│   │   ├── main_window.py     # Main application window (Notebook layout)
│   │   └── tabs/              # Modules for each tool's GUI tab
│   │       ├── __init__.py
│   │       ├── converter_tab.py
│   │       ├── icon_setter_tab.py
│   │       └── svg_tab.py
│   ├── utils/               # Utility functions
│   │   ├── __init__.py
│   │   └── file_helpers.py    # File/folder dialog helpers
│   └── main.py              # Main application entry point
├── notebooks/               # Jupyter/Colab notebooks
│   └── LLM_Crawl4AI.ipynb
├── .gitignore
├── LICENSE
├── README.md                # This file
└── requirements.txt         # Python dependencies for the src application
```

## Detailed Description of Components

### `src/` Directory

This directory contains the source code for the unified GUI application.

*   **`main.py`**: The entry point to launch the application. It initializes the Tkinter root window and the `MainWindow`.
*   **`core/`**: Contains modules with the core backend logic for each tool, separated from the UI. These modules handle the actual processing (image conversion, icon setting, SVG generation).
*   **`gui/`**: Contains the user interface code built with Tkinter and ttk.
    *   `main_window.py`: Defines the main application window structure, primarily the `ttk.Notebook` that holds the different tool tabs.
    *   `tabs/`: Each file in this subdirectory defines the layout and widgets for a specific tab in the main window, connecting UI elements to the functions in the `core/` modules.
*   **`utils/`**: Contains shared utility functions used across the application, such as standardized file/folder selection dialogs (`file_helpers.py`).

### `notebooks/` Directory

*   **`LLM_Crawl4AI.ipynb`**: A Jupyter Notebook designed for Google Colab to crawl websites using `crawl4ai`. See the "Usage" section and comments within the notebook for details.

### `requirements.txt`

This file lists the Python dependencies required specifically for running the GUI application (`src/main.py`). Key dependencies include:

*   `Pillow`: For image loading, manipulation, and saving.
*   `numpy`: For numerical operations, especially in image processing.
*   `scikit-image`: Used for image processing tasks like contour finding in the SVG converter.
*   `scikit-learn`: Used for KMeans color clustering in the SVG converter.
*   `svgwrite`: For generating SVG files.

**Note:** The `LLM_Crawl4AI.ipynb` notebook has its own dependencies (`crawl4ai`, `httpx`, `ipywidgets`, etc.) which are installed directly within the Google Colab environment when running the notebook's setup cell. They are not listed in this `requirements.txt` file.

## Contributing

This is a personal project, but contributions and suggestions are welcome. Feel free to fork the repository, make changes, and submit pull requests.

## License

This project is licensed under the **Apache License 2.0**.
