import tkinter as tk
from tkinter import ttk
import logging
import sys
from audio_processor import AudioProcessor
from master_w_gui import MasterWGUI
import os

def configure_styles():
    """Configura los estilos globales de la aplicación."""
    style = ttk.Style()
    
    # Configurar tema oscuro
    style.configure('.',
        background='#1e1e1e',
        foreground='white',
        fieldbackground='#2d2d2d',
        troughcolor='#2d2d2d',
        selectbackground='#404040',
        selectforeground='white'
    )
    
    # Configurar estilo de la barra de progreso
    style.configure('Green.Horizontal.TProgressbar',
        troughcolor='#2d2d2d',
        background='#00ff00'
    )

def setup_logging():
    """Configura el sistema de logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

def main():
    # Configurar logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Crear ventana principal
        root = tk.Tk()
        root.title("Master-W")
        
        # Configurar ventana
        root.configure(bg='#1e1e1e')
        root.minsize(1200, 800)
        root.geometry("1200x800")
        
        # Hacer que la ventana sea redimensionable
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)
        
        # Configurar estilos
        configure_styles()
        
        # Configurar icono
        try:
            if os.path.exists('icon.ico'):
                root.iconbitmap('icon.ico')
        except Exception as e:
            logger.warning(f"No se pudo cargar el icono: {e}")
        
        # Crear procesador e interfaz
        processor = AudioProcessor()
        app = MasterWGUI(root, processor)
        
        # Centrar la ventana
        window_width = 1200
        window_height = 800
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        center_x = int((screen_width - window_width) / 2)
        center_y = int((screen_height - window_height) / 2)
        root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        
        # Iniciar aplicación
        logger.info("Iniciando Master-W")
        root.mainloop()
        
    except Exception as e:
        logger.error(f"Error al iniciar la aplicación: {str(e)}")
        raise

if __name__ == "__main__":
    main()