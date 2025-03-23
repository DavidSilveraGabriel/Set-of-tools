import numpy as np
from skimage import io, color, morphology, measure
import svgwrite
import os
from sklearn.cluster import KMeans
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk

class ModernImageToSvgConverter:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Convertidor de Imagen a SVG")
        self.window.geometry("1200x800")
        self.window.configure(bg='#1a1a1a')
        
        # Variables de control para optimización
        self.n_colors = tk.IntVar(value=5)
        self.tolerance = tk.DoubleVar(value=0.2)
        self.opacity = tk.DoubleVar(value=0.9)
        self.simplify_tolerance = tk.DoubleVar(value=0.5)
        
        # Frame principal dividido en dos
        self.main_container = ttk.Frame(self.window, style='Modern.TFrame')
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Frame izquierdo para la imagen
        self.left_frame = ttk.Frame(self.main_container, style='Modern.TFrame')
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Frame derecho para opciones
        self.right_frame = ttk.Frame(self.main_container, style='Modern.TFrame')
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(20,0))
        
        self.setup_left_frame()
        self.setup_right_frame()
        
        # Variables de control
        self.current_image_path = None
        self.photo = None
        
        # Vincular evento de redimensionamiento
        self.window.bind('<Configure>', self.on_window_resize)

    def setup_left_frame(self):
        # Título
        self.title_label = tk.Label(
            self.left_frame,
            text="Convertidor de Imagen a SVG",
            font=('Helvetica', 16, 'bold'),
            fg='#00bf63',
            bg='#1a1a1a'
        )
        self.title_label.pack(pady=(0, 20))
        
        # Frame para la imagen
        self.image_frame = ttk.Frame(self.left_frame, style='Canvas.TFrame')
        self.image_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Canvas para mostrar la imagen
        self.canvas = tk.Canvas(
            self.image_frame,
            bg='#262626',
            highlightthickness=1,
            highlightbackground='#00bf63'
        )
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Label para instrucciones
        self.instruction_label = tk.Label(
            self.left_frame,
            text="Ninguna imagen seleccionada",
            font=('Helvetica', 10),
            fg='#808080',
            bg='#1a1a1a'
        )
        self.instruction_label.pack(pady=10)
        
        # Botones
        self.button_frame = ttk.Frame(self.left_frame, style='Modern.TFrame')
        self.button_frame.pack(fill=tk.X, pady=20)
        
        self.create_custom_button("Seleccionar Imagen", self.select_image, self.button_frame)
        self.create_custom_button("Convertir a SVG", self.convert_image, self.button_frame)

    def setup_right_frame(self):
        # Título de opciones
        options_title = tk.Label(
            self.right_frame,
            text="Opciones de Optimización",
            font=('Helvetica', 14, 'bold'),
            fg='#00bf63',
            bg='#1a1a1a'
        )
        options_title.pack(pady=(0, 20))
        
        # Frame para los controles
        controls_frame = ttk.Frame(self.right_frame, style='Modern.TFrame')
        controls_frame.pack(fill=tk.BOTH, expand=True)
        
        # Estilo para los sliders
        self.style = ttk.Style()
        self.style.configure("Modern.Horizontal.TScale", background='#1a1a1a')
        
        # Colores dominantes
        self.create_option_control(
            controls_frame,
            "Colores dominantes:",
            self.n_colors,
            2, 10,
            1
        )
        
        # Tolerancia de color
        self.create_option_control(
            controls_frame,
            "Tolerancia de color:",
            self.tolerance,
            0.1, 0.5,
            0.05
        )
        
        # Opacidad
        self.create_option_control(
            controls_frame,
            "Opacidad:",
            self.opacity,
            0.1, 1.0,
            0.1
        )
        
        # Tolerancia de simplificación
        self.create_option_control(
            controls_frame,
            "Simplificación de contornos:",
            self.simplify_tolerance,
            0.1, 1.0,
            0.1
        )
        
        # Botón de reset
        self.create_custom_button(
            "Restaurar valores por defecto",
            self.reset_values,
            controls_frame
        )

    def create_option_control(self, parent, label_text, variable, min_val, max_val, step):
        frame = ttk.Frame(parent, style='Modern.TFrame')
        frame.pack(fill=tk.X, pady=10, padx=10)
        
        # Label
        label = tk.Label(
            frame,
            text=label_text,
            font=('Helvetica', 10),
            fg='#ffffff',
            bg='#1a1a1a'
        )
        label.pack(fill=tk.X)
        
        # Slider
        slider = ttk.Scale(
            frame,
            from_=min_val,
            to=max_val,
            variable=variable,
            orient=tk.HORIZONTAL,
            style="Modern.Horizontal.TScale"
        )
        slider.pack(fill=tk.X)
        
        # Valor actual
        value_label = tk.Label(
            frame,
            textvariable=variable,
            font=('Helvetica', 9),
            fg='#00bf63',
            bg='#1a1a1a'
        )
        value_label.pack()

    def reset_values(self):
        self.n_colors.set(5)
        self.tolerance.set(0.2)
        self.opacity.set(0.9)
        self.simplify_tolerance.set(0.5)

    def create_custom_button(self, text, command, parent):
        button = tk.Button(
            parent,
            text=text,
            command=command,
            bg='#00bf63',
            fg='black',
            font=('Helvetica', 10, 'bold'),
            relief=tk.FLAT,
            padx=20,
            pady=10,
            activebackground='#00a854',
            activeforeground='white'
        )
        button.pack(side=tk.LEFT, padx=10, pady=5)
        
        button.bind('<Enter>', lambda e: button.configure(bg='#00a854', fg='white'))
        button.bind('<Leave>', lambda e: button.configure(bg='#00bf63', fg='black'))
        
        return button

    def on_window_resize(self, event):
        if self.current_image_path:
            self.display_image(self.current_image_path)

    def select_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.bmp *.gif")]
        )
        if file_path:
            self.current_image_path = file_path
            self.display_image(file_path)
            self.instruction_label.config(
                text=f"Imagen seleccionada: {os.path.basename(file_path)}"
            )

    def display_image(self, image_path):
        self.canvas.delete("all")
        image = Image.open(image_path)
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        img_width, img_height = image.size
        ratio = min(canvas_width/img_width, canvas_height/img_height)
        new_width = int(img_width * ratio * 0.9)
        new_height = int(img_height * ratio * 0.9)
        
        image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        self.photo = ImageTk.PhotoImage(image)
        
        x = (canvas_width - new_width) // 2
        y = (canvas_height - new_height) // 2
        
        self.canvas.create_image(x, y, image=self.photo, anchor=tk.NW)

    def convert_image(self):
        if not self.current_image_path:
            messagebox.showerror(
                "Error",
                "Por favor seleccione una imagen primero",
                parent=self.window
            )
            return
        
        options = {
            'n_colors': self.n_colors.get(),
            'tolerance': self.tolerance.get(),
            'opacity': self.opacity.get(),
            'simplify_tolerance': self.simplify_tolerance.get()
        }
        
        if image_to_svg(self.current_image_path, options):
            messagebox.showinfo(
                "Éxito",
                "Imagen convertida exitosamente a SVG",
                parent=self.window
            )
        else:
            messagebox.showerror(
                "Error",
                "No se pudo convertir la imagen",
                parent=self.window
            )

    def run(self):
        self.window.mainloop()

def image_to_svg(image_path, options):
    """Convierte una imagen a SVG usando técnicas avanzadas."""
    try:
        # Preprocesar imagen
        img, img_smooth, img_hsv, img_lab = preprocess_image(image_path)
        height, width = img.shape[:2]
        
        # Obtener colores dominantes usando las opciones
        colors = get_dominant_colors(img_smooth, options['n_colors'])
        
        # Crear máscaras de color con la tolerancia especificada
        color_masks = create_color_masks(img_hsv, colors, options['tolerance'])
        
        # Generar SVG
        output_path = os.path.splitext(image_path)[0] + "_advanced_favicon.svg"
        dwg = svgwrite.Drawing(output_path, profile='tiny', size=(width, height))
        dwg.viewbox(0, 0, width, height)

        # Procesar cada máscara de color
        for mask, color in color_masks:
            contours = get_advanced_contours(mask, options['simplify_tolerance'])
            for contour in contours:
                path = dwg.path(
                    d=contour_to_bezier(contour),
                    fill=rgb_to_hex(color),
                    fill_opacity=options['opacity']
                )
                dwg.add(path)
        
        # Guardar SVG
        dwg.save()
        return True

    except Exception as e:
        print(f"Ocurrió un error: {str(e)}")
        return False

def preprocess_image(image_path):
    """Preprocesa la imagen para su posterior uso."""
    img = io.imread(image_path)
    img_smooth = img
    img_hsv = color.rgb2hsv(img) if img.ndim == 3 else color.gray2hsv(img)
    img_lab = color.rgb2lab(img) if img.ndim == 3 else color.gray2lab(img)
    return img, img_smooth, img_hsv, img_lab

def get_dominant_colors(img, n_colors):
    """Obtiene los colores dominantes de la imagen usando k-means."""
    if img.ndim == 3:
        pixels = img.reshape(-1, 3)
    else:
        pixels = img.reshape(-1, 1)
    kmeans = KMeans(n_clusters=n_colors, random_state=0, n_init=10)
    kmeans.fit(pixels)
    
    if img.ndim == 3:
        return kmeans.cluster_centers_.astype(int)
    else:
        return [int(c[0]) for c in kmeans.cluster_centers_]

def create_color_masks(img_hsv, colors, tolerance):
    """Crea máscaras binarias para cada color dominante."""
    masks = []
    for color in colors:
        if img_hsv.ndim == 3:
            hsv_color = color / 255.0
            lower_bound = np.clip(hsv_color - tolerance, 0, 1)
            upper_bound = np.clip(hsv_color + tolerance, 0, 1)
            mask = np.all((img_hsv >= lower_bound) & (img_hsv <= upper_bound), axis=2)
        else:
            lower_bound = np.clip((color/255) - tolerance, 0, 1)
            upper_bound = np.clip((color/255) + tolerance, 0, 1)
            mask = (img_hsv >= lower_bound) & (img_hsv <= upper_bound)
        masks.append((mask, color))
    return masks

def get_advanced_contours(mask, simplify_tolerance):
    """Obtiene contornos avanzados de una máscara binaria."""
    contours = measure.find_contours(mask.astype(float), simplify_tolerance)
    return contours

def contour_to_bezier(contour):
    """Convierte un contorno a una cadena de path para SVG."""
    return "M" + "L".join(f"{x},{y}" for y, x in contour) + "Z"

def rgb_to_hex(color):
    """Convierte color RGB a formato hexadecimal."""
    if isinstance(color, (list, np.ndarray)):
        return '#{:02x}{:02x}{:02x}'.format(*map(int, color))
    return '#{:02x}{:02x}{:02x}'.format(color, color, color)

if __name__ == '__main__':
    app = ModernImageToSvgConverter()
    app.run()