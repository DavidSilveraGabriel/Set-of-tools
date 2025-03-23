import tkinter as tk
from tkinter import filedialog
from PIL import Image
import os

def select_file():
    """Abre un diálogo para seleccionar el archivo de imagen."""
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Selecciona una imagen",
        filetypes=[
            ("Imágenes", "*.png *.jpg *.jpeg *.bmp *.gif *.ico *.webp *.tiff"),
            ("Todos los archivos", "*.*")
        ]
    )
    return file_path

def convert_image():
    # Seleccionar archivo de entrada
    input_path = select_file()
    if not input_path:
        print("No se seleccionó ningún archivo.")
        return

    try:
        # Abrir la imagen
        image = Image.open(input_path)
        original_format = image.format
        print(f"\nInformación de la imagen:")
        print(f"Formato actual: {original_format}")
        print(f"Tamaño actual: {image.size}")
        
        # Opciones de formato disponibles
        formats = {
            '1': ('PNG', '.png'),
            '2': ('JPEG', '.jpg'),
            '3': ('ICO', '.ico'),
            '4': ('BMP', '.bmp'),
            '5': ('WEBP', '.webp'),
            '6': ('TIFF', '.tiff')
        }

        # Preguntar por el tipo de redimensionamiento
        while True:
            print("\nOpciones de redimensionamiento:")
            print("1. Mantener tamaño original")
            print("2. Especificar nuevo ancho y alto")
            print("3. Escalar por porcentaje")
            print("4. Ajustar a ancho específico (mantener proporción)")
            print("5. Ajustar a alto específico (mantener proporción)")
            
            resize_option = input("Selecciona una opción (1-5): ")
            
            if resize_option in ['1', '2', '3', '4', '5']:
                break
            print("Por favor, selecciona una opción válida.")

        # Procesar redimensionamiento
        if resize_option == '2':
            width = int(input("Ingresa el nuevo ancho en píxeles: "))
            height = int(input("Ingresa el nuevo alto en píxeles: "))
            image = image.resize((width, height), Image.Resampling.LANCZOS)
        elif resize_option == '3':
            scale = float(input("Ingresa el porcentaje (ej: 50 para reducir a la mitad): ")) / 100
            new_width = int(image.width * scale)
            new_height = int(image.height * scale)
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        elif resize_option == '4':
            width = int(input("Ingresa el nuevo ancho en píxeles: "))
            ratio = width / image.width
            height = int(image.height * ratio)
            image = image.resize((width, height), Image.Resampling.LANCZOS)
        elif resize_option == '5':
            height = int(input("Ingresa el nuevo alto en píxeles: "))
            ratio = height / image.height
            width = int(image.width * ratio)
            image = image.resize((width, height), Image.Resampling.LANCZOS)

        # Mostrar formatos disponibles
        print("\nFormatos disponibles:")
        for key, (format_name, _) in formats.items():
            print(f"{key}. {format_name}")
        
        # Seleccionar formato de salida
        while True:
            format_choice = input("\nSelecciona el formato de salida (1-6): ")
            if format_choice in formats:
                break
            print("Por favor, selecciona un formato válido.")

        output_format, extension = formats[format_choice]
        
        # Generar nombre del archivo de salida
        output_path = os.path.splitext(input_path)[0] + "_convertido" + extension
        
        # Guardar imagen
        if output_format == 'JPEG':
            image = image.convert('RGB')  # Convertir a RGB si es necesario
            image.save(output_path, format=output_format, quality=95)
        else:
            image.save(output_path, format=output_format)
        
        print(f"\nImagen convertida exitosamente y guardada en:\n{output_path}")
        print(f"Tamaño final: {image.size}")

    except Exception as e:
        print(f"Ocurrió un error: {str(e)}")

if __name__ == "__main__":
    print("=== Conversor de Formatos de Imagen ===")
    print("Este programa permite convertir imágenes entre diferentes formatos y redimensionarlas")
    
    while True:
        convert_image()
        
        while True:
            continuar = input("\n¿Deseas convertir otra imagen? (s/n): ").lower()
            if continuar in ['s', 'n']:
                break
            print("Por favor, responde 's' o 'n'")
            
        if continuar == 'n':
            break

    print("\n¡Gracias por usar el conversor!")