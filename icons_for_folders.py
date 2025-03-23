import os
import platform
import tkinter as tk
from tkinter import filedialog, messagebox
import logging
import subprocess
import ctypes

# Configuración básica del logger
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filename='icono_carpeta.log',
                    filemode='w')

def is_admin():
    """Verifica si el script se está ejecutando con permisos de administrador."""
    try:
        if platform.system() == "Windows":
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            # En sistemas Unix, verifica si el UID es 0 (root)
            return os.geteuid() == 0
    except:
        return False

def cambiar_icono_carpeta(icono_path, carpeta_path):
    """
    Cambia el icono de una carpeta a un icono personalizado.
    """
    logging.info(f"Iniciando cambiar_icono_carpeta con icono_path: '{icono_path}', carpeta_path: '{carpeta_path}'")
    sistema_operativo = platform.system()
    logging.debug(f"Sistema operativo detectado: {sistema_operativo}")
    
    # Determinar la extensión permitida según el sistema operativo
    if sistema_operativo == "Windows":
        ext_icono_permitida = ".ico"
    elif sistema_operativo == "Darwin":  # macOS
        ext_icono_permitida = ".icns"
    elif sistema_operativo == "Linux":
        messagebox.showerror("Error", "Lo siento, cambiar iconos de carpeta de forma persistente en Linux no está soportado en este script.")
        logging.warning("Intento de cambiar icono en Linux, no soportado.")
        return False
    else:
        messagebox.showerror("Error", f"Sistema operativo no soportado: {sistema_operativo}")
        logging.error(f"Sistema operativo no soportado: {sistema_operativo}")
        return False

    # Validaciones de archivos y carpetas
    if not os.path.exists(icono_path):
        messagebox.showerror("Error", f"El archivo de icono '{icono_path}' no existe.")
        logging.error(f"Archivo de icono no existe: '{icono_path}'")
        return False
    if not os.path.exists(carpeta_path):
        messagebox.showerror("Error", f"La carpeta '{carpeta_path}' no existe.")
        logging.error(f"Carpeta no existe: '{carpeta_path}'")
        return False
    if not os.path.isfile(icono_path):
        messagebox.showerror("Error", f"'{icono_path}' no es un archivo válido.")
        logging.error(f"No es un archivo válido: '{icono_path}'")
        return False
    if not os.path.isdir(carpeta_path):
        messagebox.showerror("Error", f"'{carpeta_path}' no es una carpeta válida.")
        logging.error(f"No es una carpeta válida: '{carpeta_path}'")
        return False
    if not icono_path.lower().endswith(ext_icono_permitida):
        messagebox.showerror("Error", f"El archivo de icono debe tener la extensión '{ext_icono_permitida}' para este sistema operativo.")
        logging.error(f"Extensión de icono incorrecta: '{icono_path}', se esperaba '{ext_icono_permitida}'")
        return False

    try:
        # Proceso para Windows
        if sistema_operativo == "Windows":
            logging.debug("Procesando en Windows")
            
            # Comprobar permisos de administrador para operaciones críticas
            if not is_admin() and os.path.exists(os.path.join(carpeta_path, "desktop.ini")):
                # Si desktop.ini ya existe y no somos admin, puede que no podamos sobrescribirlo
                logging.warning("El script no tiene permisos de administrador y desktop.ini ya existe.")
                messagebox.showwarning("Advertencia", "El script no se está ejecutando como administrador. Algunos cambios podrían no aplicarse correctamente.")
            
            # Usar ruta absoluta para el icono
            icono_path_abs = os.path.abspath(icono_path)
            
            # Crear contenido del desktop.ini con la ruta absoluta del icono
            desktop_ini_content = f"""[.ShellClassInfo]
IconResource={icono_path_abs},0
[ViewState]
Mode=
Vid=
FolderType=Generic
"""
            desktop_ini_path = os.path.join(carpeta_path, "desktop.ini")
            logging.debug(f"Ruta de desktop.ini: '{desktop_ini_path}'")
            
            # Quitar atributos de sistema y oculto si desktop.ini ya existe
            if os.path.exists(desktop_ini_path):
                try:
                    subprocess.run(['attrib', '-s', '-h', desktop_ini_path], shell=True, check=True)
                    logging.debug(f'Atributos -s -h quitados de desktop.ini existente')
                except Exception as e:
                    logging.warning(f"No se pudieron quitar atributos de desktop.ini: {e}")
            
            # Escribir en desktop.ini
            try:
                with open(desktop_ini_path, "w", encoding="utf-8") as f:
                    f.write(desktop_ini_content)
                logging.debug("Archivo desktop.ini escrito correctamente")
            except Exception as e_file:
                messagebox.showerror("Error al escribir desktop.ini", f"No se pudo escribir en desktop.ini: {e_file}")
                logging.error(f"Error al escribir desktop.ini: {e_file}")
                return False

            # Aplicar atributos al desktop.ini
            try:
                subprocess.run(['attrib', '+s', '+h', desktop_ini_path], shell=True, check=True)
                logging.debug(f'Atributos +s +h aplicados a desktop.ini')
            except Exception as e_attrib_ini:
                messagebox.showerror("Error attrib desktop.ini", f"Error al establecer atributos de desktop.ini: {e_attrib_ini}")
                logging.error(f"Error al ejecutar attrib para desktop.ini: {e_attrib_ini}")
                return False

            # Aplicar atributo de sistema a la carpeta
            try:
                subprocess.run(['attrib', '+s', carpeta_path], shell=True, check=True)
                logging.debug(f'Atributo +s aplicado a la carpeta')
            except Exception as e_attrib_folder:
                messagebox.showerror("Error attrib carpeta", f"Error al establecer atributos de carpeta: {e_attrib_folder}")
                logging.error(f"Error al ejecutar attrib para carpeta: {e_attrib_folder}")
                return False

            messagebox.showinfo("Éxito", f"Icono personalizado establecido para la carpeta '{carpeta_path}'.\nPuede que necesites refrescar la vista de la carpeta (F5) para ver el cambio.")
            logging.info(f"Icono establecido con éxito en Windows para carpeta: '{carpeta_path}'")
            return True

        # Proceso para macOS
        elif sistema_operativo == "Darwin":
            logging.debug("Procesando en macOS")
            
            # Escapar rutas para evitar problemas con espacios
            icono_path_escaped = icono_path.replace('"', '\\"')
            carpeta_path_escaped = carpeta_path.replace('"', '\\"')
            
            osascript_command = f"""
tell application "Finder"
    set theFolder to POSIX file "{carpeta_path_escaped}"
    set theIconFile to POSIX file "{icono_path_escaped}"
    set icon of theFolder to theIconFile
end tell
"""
            logging.debug(f"Comando osascript preparado")
            
            process = subprocess.Popen(['osascript', '-e', osascript_command],
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            
            if stderr:
                error_msg = stderr.decode()
                messagebox.showerror("Error en macOS", f"Error al establecer el icono: {error_msg}")
                logging.error(f"Error en macOS al ejecutar osascript: {error_msg}")
                return False
            else:
                logging.debug(f"Salida de osascript: {stdout.decode() if stdout else 'Sin salida'}")
                # Limpiar caché de iconos en macOS
                try:
                    subprocess.run(['killall', 'Finder'], check=True)
                    logging.debug("Finder reiniciado para actualizar iconos")
                except Exception as e:
                    logging.warning(f"No se pudo reiniciar Finder: {e}")
                
                messagebox.showinfo("Éxito", f"Icono personalizado establecido para la carpeta '{carpeta_path}' en macOS.")
                logging.info(f"Icono establecido con éxito en macOS para carpeta: '{carpeta_path}'")
                return True

    except Exception as e_general:
        messagebox.showerror("Error Inesperado", f"Ocurrió un error inesperado: {e_general}\nPor favor, asegúrate de tener permisos para modificar la carpeta y el archivo de icono.")
        logging.exception("Error inesperado en cambiar_icono_carpeta")
        return False

def seleccionar_icono():
    sistema_operativo = platform.system()
    if sistema_operativo == "Windows":
        filetypes = (("Archivos de icono", "*.ico"), ("Todos los archivos", "*.*"))
    elif sistema_operativo == "Darwin":  # macOS
        filetypes = (("Archivos ICNS", "*.icns"), ("Todos los archivos", "*.*"))
    else:  # Linux u otro
        filetypes = (("Todos los archivos", "*.*"),)
    
    icono_path = filedialog.askopenfilename(title="Seleccionar archivo de icono", filetypes=filetypes)
    if icono_path:
        icono_path_var.set(icono_path)
        logging.debug(f"Archivo de icono seleccionado: '{icono_path}'")

def seleccionar_carpeta():
    carpeta_path = filedialog.askdirectory(title="Seleccionar carpeta")
    if carpeta_path:
        carpeta_path_var.set(carpeta_path)
        logging.debug(f"Carpeta seleccionada: '{carpeta_path}'")

def aplicar_icono():
    status_label.config(text="Procesando...", fg="blue")
    ventana.update()
    
    icono = icono_path_var.get()
    carpeta = carpeta_path_var.get()
    logging.info(f"Intentando aplicar icono: '{icono}', a carpeta: '{carpeta}'")
    
    if not icono:
        messagebox.showerror("Error", "Por favor, selecciona un archivo de icono.")
        logging.warning("No se seleccionó archivo de icono.")
        status_label.config(text="Error: No se seleccionó icono", fg="red")
        return
    
    if not carpeta:
        messagebox.showerror("Error", "Por favor, selecciona una carpeta.")
        logging.warning("No se seleccionó carpeta.")
        status_label.config(text="Error: No se seleccionó carpeta", fg="red")
        return

    if cambiar_icono_carpeta(icono, carpeta):
        status_label.config(text="Icono aplicado con éxito.", fg="green")
        logging.info("Icono aplicado exitosamente.")
    else:
        status_label.config(text="Error al aplicar el icono. Revisa el log para más detalles.", fg="red")
        logging.error("Fallo al aplicar el icono.")

# Configuración de la ventana principal
ventana = tk.Tk()
ventana.title("Cambiar Icono de Carpeta")
ventana.geometry("500x320")
icono_path_var = tk.StringVar()
carpeta_path_var = tk.StringVar()

# Crear un marco principal con padding
main_frame = tk.Frame(ventana, padx=10, pady=10)
main_frame.pack(fill=tk.BOTH, expand=True)

# Mostrar el sistema operativo detectado
so_label = tk.Label(main_frame, text=f"Sistema detectado: {platform.system()}", font=("Helvetica", 10, "italic"))
so_label.pack(pady=(0, 10), anchor="w")

# Sección de icono
icono_frame = tk.LabelFrame(main_frame, text="Archivo de Icono", padx=5, pady=5)
icono_frame.pack(fill=tk.X, pady=5)

icono_entry = tk.Entry(icono_frame, textvariable=icono_path_var, state='readonly', width=50)
icono_entry.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)

icono_boton = tk.Button(icono_frame, text="Seleccionar", command=seleccionar_icono)
icono_boton.pack(side=tk.RIGHT, padx=5, pady=5)

# Sección de carpeta
carpeta_frame = tk.LabelFrame(main_frame, text="Carpeta a modificar", padx=5, pady=5)
carpeta_frame.pack(fill=tk.X, pady=5)

carpeta_entry = tk.Entry(carpeta_frame, textvariable=carpeta_path_var, state='readonly', width=50)
carpeta_entry.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)

carpeta_boton = tk.Button(carpeta_frame, text="Seleccionar", command=seleccionar_carpeta)
carpeta_boton.pack(side=tk.RIGHT, padx=5, pady=5)

# Sección de aplicar
aplicar_frame = tk.Frame(main_frame)
aplicar_frame.pack(pady=10)

aplicar_boton = tk.Button(aplicar_frame, text="Aplicar Icono a Carpeta", command=aplicar_icono, 
                         bg="#4CAF50", fg="white", font=("Helvetica", 10, "bold"), 
                         width=20, height=2)
aplicar_boton.pack()

# Etiqueta de estado
status_frame = tk.Frame(main_frame)
status_frame.pack(fill=tk.X, pady=5)

status_label = tk.Label(status_frame, text="Listo para cambiar iconos de carpeta", fg="blue")
status_label.pack(pady=5)

# Información sobre permisos
if platform.system() == "Windows" and not is_admin():
    admin_label = tk.Label(main_frame, text="Nota: Para mejores resultados, ejecuta como administrador", 
                          fg="orange", font=("Helvetica", 8))
    admin_label.pack(pady=(5, 0))

# Centrar la ventana en la pantalla
ventana.eval('tk::PlaceWindow . center')
ventana.mainloop()