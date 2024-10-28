import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import logging
import queue
import os
from datetime import datetime

# Configuración de colores y estilos
THEME = {
    'bg_dark': '#1A1A1A',
    'bg_medium': '#2D2D2D',
    'bg_light': '#383838',
    'accent': '#00CC66',
    'accent_hover': '#00FF80',
    'text': '#FFFFFF',
    'text_secondary': '#CCCCCC',
    'warning': '#FFB300',
    'error': '#FF4444',
    'success': '#00CC66',
    
    # Fuentes
    'font_main': ('Segoe UI', 10),
    'font_title': ('Segoe UI', 24, 'bold'),
    'font_subtitle': ('Segoe UI', 12),
    'font_header': ('Segoe UI', 12, 'bold'),
    'font_mono': ('Consolas', 9),
    
    # Padding y márgenes
    'padding_small': 5,
    'padding_medium': 10,
    'padding_large': 20,
}

class QueueHandler(logging.Handler):
    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record):
        self.log_queue.put(record)

class MasterWGUI:
    def __init__(self, root, processor):
        # Variables base
        self.root = root
        self.processor = processor
        self.log_queue = queue.Queue()
        
        # Variables de estado
        self.is_processing = False
        self.target_file = None
        self.reference_file = None
        self.last_directory = os.path.expanduser("~")
        
        # Inicialización del sistema
        self.setup_logging()
        self.create_styles()
        
        # Configuración de la ventana principal
        self.setup_main_window()
        
        # Crear interfaz
        self.create_gui()
        self.process_logs()

    def setup_logging(self):
        """Configura el sistema de logging."""
        self.logger = logging.getLogger('MasterW')
        self.logger.setLevel(logging.INFO)
        
        # Crear y configurar el handler
        queue_handler = QueueHandler(self.log_queue)
        self.log_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        queue_handler.setFormatter(self.log_formatter)
        
        # Limpiar handlers existentes y añadir el nuevo
        self.logger.handlers.clear()
        self.logger.addHandler(queue_handler)

    def setup_main_window(self):
        """Configura la ventana principal."""
        # Configurar grid principal
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Frame principal con padding
        self.main_frame = ttk.Frame(self.root, style='Main.TFrame')
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        # Configurar grid del frame principal
        self.main_frame.grid_columnconfigure(0, weight=1)
        for i in range(3):  # 3 filas principales
            weight = 1 if i == 1 else 0  # La fila del visualizador tiene peso 1
            self.main_frame.grid_rowconfigure(i, weight=weight)

    def create_styles(self):
        """Crea los estilos personalizados de la interfaz."""
        style = ttk.Style()
        
        # Frame principal
        style.configure('Main.TFrame',
            background=THEME['bg_dark'])
            
        # Frame secundario
        style.configure('Sub.TFrame',
            background=THEME['bg_medium'])
            
        # Labels
        style.configure('Header.TLabel',
            background=THEME['bg_medium'],
            foreground=THEME['accent'],
            font=THEME['font_header'])
            
        style.configure('Info.TLabel',
            background=THEME['bg_medium'],
            foreground=THEME['text'],
            font=THEME['font_main'])
            
        # Botón de acción (cargar archivos)
        style.configure('Action.TButton',
            font=THEME['font_main'],
            background=THEME['accent'],
            foreground=THEME['bg_dark'],
            padding=(THEME['padding_medium'], THEME['padding_small']))
            
        # Botón primario (masterizar)
        style.configure('Primary.TButton',
            font=('Segoe UI', 11, 'bold'),
            background=THEME['accent'],
            foreground=THEME['bg_dark'],
            padding=(THEME['padding_large'], THEME['padding_medium']))
            
        # Barra de progreso
        style.configure('Progress.Horizontal.TProgressbar',
            background=THEME['accent'],
            troughcolor=THEME['bg_medium'])
            
        # Mapeos para estados de botones
        style.map('Action.TButton',
            background=[
                ('active', THEME['accent_hover']),
                ('disabled', THEME['bg_medium'])
            ],
            foreground=[
                ('active', THEME['bg_dark']),
                ('disabled', THEME['text_secondary'])
            ]
        )
                       
        style.map('Primary.TButton',
            background=[
                ('active', THEME['accent_hover']),
                ('disabled', THEME['bg_medium'])
            ],
            foreground=[
                ('active', THEME['bg_dark']),
                ('disabled', THEME['text_secondary'])
            ]
        )

    def create_gui(self):
        """Crea la interfaz gráfica completa."""
        self.create_audio_controls()
        self.create_visualization()
        self.create_bottom_section()

    def create_audio_controls(self):
        """Crea la sección de controles de audio."""
        controls_frame = ttk.Frame(self.main_frame, style='Main.TFrame')
        controls_frame.grid(row=0, column=0, sticky='ew', pady=(0, THEME['padding_large']))
        controls_frame.grid_columnconfigure(0, weight=1)
        controls_frame.grid_columnconfigure(2, weight=1)
        
        # Panel izquierdo - Audio original
        self.create_audio_panel(
            controls_frame, 
            0, 
            "Audio Original", 
            "Cargar Original", 
            self.load_target
        )
        
        # Separador vertical
        separator = ttk.Separator(controls_frame, orient='vertical')
        separator.grid(row=0, column=1, sticky='ns', padx=THEME['padding_large'])
        
        # Panel derecho - Audio referencia
        self.create_audio_panel(
            controls_frame, 
            2, 
            "Audio de Referencia", 
            "Cargar Referencia", 
            self.load_reference
        )

    def create_audio_panel(self, parent, column, title, button_text, command):
        """Crea un panel de control de audio."""
        panel = ttk.Frame(parent, style='Sub.TFrame')
        panel.grid(row=0, column=column, sticky='nsew', padx=THEME['padding_medium'])
        panel.grid_columnconfigure(0, weight=1)
        
        # Añadir padding interno
        content_frame = ttk.Frame(panel, style='Sub.TFrame', padding=THEME['padding_medium'])
        content_frame.grid(row=0, column=0, sticky='nsew')
        content_frame.grid_columnconfigure(0, weight=1)
        
        # Título del panel
        header = ttk.Label(content_frame, text=title, style='Header.TLabel')
        header.grid(row=0, column=0, sticky='w', pady=(0, THEME['padding_medium']))
        
        # Marco para información
        info_frame = ttk.Frame(content_frame, style='Sub.TFrame')
        info_frame.grid(row=1, column=0, sticky='nsew', pady=(0, THEME['padding_medium']))
        
        # Labels de información
        if "Original" in title:
            self.target_info = ttk.Label(
                info_frame,
                text="No se ha cargado archivo",
                style='Info.TLabel',
                justify='left'
            )
            self.target_info.grid(row=0, column=0, sticky='w')
        else:
            self.reference_info = ttk.Label(
                info_frame,
                text="No se ha cargado archivo",
                style='Info.TLabel',
                justify='left'
            )
            self.reference_info.grid(row=0, column=0, sticky='w')
        
        # Botón con estilo actualizado
        if "Original" in title:
            self.load_target_btn = ttk.Button(
                content_frame,
                text=button_text,
                style='Action.TButton',
                command=command
            )
            self.load_target_btn.grid(row=2, column=0, sticky='w')
        else:
            self.load_reference_btn = ttk.Button(
                content_frame,
                text=button_text,
                style='Action.TButton',
                command=command
            )
            self.load_reference_btn.grid(row=2, column=0, sticky='w')
        
        return panel

    def create_visualization(self):
        """Crea la sección de visualización de audio."""
        viz_frame = ttk.Frame(self.main_frame, style='Sub.TFrame')
        viz_frame.grid(row=1, column=0, sticky='nsew', pady=THEME['padding_medium'])
        viz_frame.grid_columnconfigure(0, weight=1)
        viz_frame.grid_rowconfigure(0, weight=1)
        
        # Configurar figura
        self.figure = Figure(figsize=(8, 6), dpi=100, facecolor=THEME['bg_medium'])
        self.canvas = FigureCanvasTkAgg(self.figure, master=viz_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew', padx=1, pady=1)
        
        # Configurar subplots con GridSpec
        gs = self.figure.add_gridspec(2, 1, height_ratios=[1, 1], hspace=0.3)
        self.waveform_ax = self.figure.add_subplot(gs[0])
        self.spectrum_ax = self.figure.add_subplot(gs[1])
        
        # Configurar estilo inicial
        self._setup_plot_style()
        
        # Ajustar márgenes
        self.figure.subplots_adjust(
            left=0.08,    # Margen izquierdo
            right=0.92,   # Margen derecho
            top=0.92,     # Margen superior
            bottom=0.1    # Margen inferior
        )

    def create_bottom_section(self):
        """Crea la sección inferior con controles y log."""
        bottom_frame = ttk.Frame(self.main_frame, style='Main.TFrame')
        bottom_frame.grid(row=2, column=0, sticky='ew', pady=(THEME['padding_large'], 0))
        bottom_frame.grid_columnconfigure(0, weight=1)
        
        # Frame para log
        log_frame = ttk.Frame(bottom_frame, style='Sub.TFrame', padding=1)
        log_frame.grid(row=0, column=0, sticky='ew', pady=(0, THEME['padding_medium']))
        log_frame.grid_columnconfigure(0, weight=1)
        
        # Log con estilo mejorado
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=6,
            bg=THEME['bg_dark'],
            fg=THEME['accent'],
            font=THEME['font_mono'],
            wrap=tk.WORD
        )
        self.log_text.grid(row=0, column=0, sticky='ew')
        
        # Frame para controles
        controls = ttk.Frame(bottom_frame, style='Main.TFrame')
        controls.grid(row=1, column=0, sticky='ew')
        controls.grid_columnconfigure(1, weight=1)
        
        # Botón de proceso
        self.process_button = ttk.Button(
            controls,
            text="Masterizar",
            style='Primary.TButton',
            command=self.process_audio
        )
        self.process_button.grid(row=0, column=0, padx=(0, THEME['padding_medium']))
        
        # Barra de progreso
        self.progress = ttk.Progressbar(
            controls,
            mode='determinate',
            style='Progress.Horizontal.TProgressbar'
        )
        self.progress.grid(row=0, column=1, sticky='ew', padx=THEME['padding_medium'])
        
        # Botón de guardado
        self.save_button = ttk.Button(
            controls,
            text="Guardar",
            style='Action.TButton',
            command=self.save_result
        )
        self.save_button.grid(row=0, column=2)

    def _setup_plot_style(self):
        """Configura el estilo de los gráficos."""
        for ax in [self.waveform_ax, self.spectrum_ax]:
            ax.set_facecolor(THEME['bg_dark'])
            ax.grid(True, color=THEME['bg_light'], linestyle='--', alpha=0.3)
            ax.tick_params(
                colors=THEME['text_secondary'],
                labelsize=8,
                direction='out',
                length=4,
                width=1
            )
            for spine in ax.spines.values():
                spine.set_color(THEME['bg_light'])
        
        # Configurar títulos y etiquetas
        self.waveform_ax.set_title(
            'Forma de Onda',
            color=THEME['text'],
            pad=10,
            fontsize=10,
            fontweight='bold'
        )
        self.spectrum_ax.set_title(
            'Espectro de Frecuencias',
            color=THEME['text'],
            pad=10,
            fontsize=10,
            fontweight='bold'
        )
        
        # Etiquetas de ejes
        self.waveform_ax.set_xlabel(
            'Tiempo (s)',
            color=THEME['text_secondary'],
            fontsize=8
        )
        self.waveform_ax.set_ylabel(
            'Amplitud',
            color=THEME['text_secondary'],
            fontsize=8
        )
        
        self.spectrum_ax.set_xlabel(
            'Frecuencia (Hz)',
            color=THEME['text_secondary'],
            fontsize=8
        )
        self.spectrum_ax.set_ylabel(
            'Magnitud (dB)',
            color=THEME['text_secondary'],
            fontsize=8
        )

    def update_audio_display(self):
        """Actualiza la visualización de audio."""
        if not self.root.winfo_exists():
            return

        try:
            self.waveform_ax.clear()
            self.spectrum_ax.clear()
            self._setup_plot_style()

            # Colores para cada tipo de audio
            colors = {
                'target': {'color': '#00CC66', 'label': 'Original'},
                'reference': {'color': '#FF6B6B', 'label': 'Referencia'},
                'result': {'color': '#4ECDC4', 'label': 'Masterizado'}
            }

            # Dibujar las formas de onda
            self._draw_waveforms(colors)
            
            # Dibujar los espectros
            self._draw_spectrums(colors)

            # Actualizar visualización
            self.canvas.draw()

        except Exception as e:
            self.logger.error(f"Error al actualizar visualización: {str(e)}")

    def _draw_waveforms(self, colors):
        """Dibuja las formas de onda de todos los audios."""
        max_duration = 0
        
        # Dibujar cada tipo de audio
        audio_data = self._get_audio_data()
        for audio_type, audio in audio_data.items():
            if audio is not None and isinstance(audio, np.ndarray):  # Verificación adicional
                time = np.arange(len(audio)) / self._get_sample_rate(audio_type)
                max_duration = max(max_duration, time[-1])
                
                self.waveform_ax.plot(
                    time, 
                    audio,
                    color=colors[audio_type]['color'],
                    label=colors[audio_type]['label'],
                    alpha=0.7,
                    linewidth=0.5
                )

        # Configurar ejes
        self.waveform_ax.set_ylim([-1.1, 1.1])
        if max_duration > 0:  # Verificación adicional
            self.waveform_ax.set_xlim([0, max_duration])
        
        # Añadir líneas de referencia
        for level in [-1, -0.5, 0, 0.5, 1]:
            self.waveform_ax.axhline(
                y=level,
                color=THEME['bg_light'],
                linestyle=':',
                alpha=0.3
            )

        # Leyenda
        if self.waveform_ax.get_legend_handles_labels()[0]:  # Verificar si hay elementos para la leyenda
            legend = self.waveform_ax.legend(
                loc='upper right',
                fancybox=True,
                framealpha=0.8,
                fontsize=8
            )
            legend.get_frame().set_facecolor(THEME['bg_medium'])
            for text in legend.get_texts():
                text.set_color(THEME['text'])

    def _draw_spectrums(self, colors):
        """Dibuja los espectros de frecuencia de todos los audios."""
        window_size = 8192
        ref_max = -120
        
        # Dibujar cada tipo de audio
        audio_data = self._get_audio_data()
        for audio_type, audio in audio_data.items():
            if audio is not None and isinstance(audio, np.ndarray):  # Verificación adicional
                # Calcular espectro
                try:
                    spectrum, freqs = self._calculate_spectrum(audio, window_size)
                    magnitude_db = 20 * np.log10(np.maximum(spectrum, 1e-10))
                    ref_max = max(ref_max, np.max(magnitude_db))
                    
                    # Dibujar espectro
                    self.spectrum_ax.semilogx(
                        freqs[1:],
                        magnitude_db[1:],
                        color=colors[audio_type]['color'],
                        label=colors[audio_type]['label'],
                        alpha=0.7,
                        linewidth=0.8
                    )
                except Exception as e:
                    self.logger.error(f"Error al calcular espectro para {audio_type}: {str(e)}")
                    continue

        # Configurar ejes
        self.spectrum_ax.set_xlim([20, 20000])
        self.spectrum_ax.set_ylim([ref_max - 60, ref_max + 5])
        
        # Añadir marcadores de frecuencia
        freq_bands = {
            '20Hz': 20,
            '50Hz': 50,
            '100Hz': 100,
            '200Hz': 200,
            '500Hz': 500,
            '1kHz': 1000,
            '2kHz': 2000,
            '5kHz': 5000,
            '10kHz': 10000,
            '20kHz': 20000
        }
        
        for label, freq in freq_bands.items():
            self.spectrum_ax.axvline(
                x=freq,
                color=THEME['bg_light'],
                linestyle=':',
                alpha=0.2
            )
            if freq in [100, 1000, 10000]:
                self.spectrum_ax.text(
                    freq,
                    ref_max - 55,
                    label,
                    color=THEME['text_secondary'],
                    ha='center',
                    va='top',
                    fontsize=7
                )

        # Añadir líneas de referencia de dB
        for db in range(int(ref_max - 60), int(ref_max + 5), 12):
            self.spectrum_ax.axhline(
                y=db,
                color=THEME['bg_light'],
                linestyle=':',
                alpha=0.2
            )
            self.spectrum_ax.text(
                25,
                db,
                f'{db}dB',
                color=THEME['text_secondary'],
                va='center',
                fontsize=7
            )

        # Leyenda
        if self.spectrum_ax.get_legend_handles_labels()[0]:  # Verificar si hay elementos para la leyenda
            legend = self.spectrum_ax.legend(
                loc='upper right',
                fancybox=True,
                framealpha=0.8,
                fontsize=8
            )
            legend.get_frame().set_facecolor(THEME['bg_medium'])
            for text in legend.get_texts():
                text.set_color(THEME['text'])

    def _calculate_spectrum(self, audio_data, window_size):
        """Calcula el espectro de frecuencias usando ventana Hann."""
        try:
            window = np.hanning(window_size)
            hop_size = window_size // 2
            
            # Calcular número de segmentos
            num_segments = (len(audio_data) - window_size) // hop_size + 1
            
            # Inicializar array para el espectro
            spectrum = np.zeros(window_size // 2 + 1)
            
            # Calcular FFT por segmentos y promediar
            for i in range(num_segments):
                start = i * hop_size
                segment = audio_data[start:start + window_size]
                if len(segment) == window_size:
                    fft = np.fft.rfft(segment * window)
                    spectrum += np.abs(fft)
            
            spectrum /= max(num_segments, 1)  # Evitar división por cero
            freqs = np.fft.rfftfreq(window_size, 1/self.processor.sample_rate)
            
            return spectrum, freqs
            
        except Exception as e:
            self.logger.error(f"Error en cálculo de espectro: {str(e)}")
            raise

    def _get_audio_data(self):
        """Obtiene los datos de audio normalizados para visualización."""
        audio_data = {}
        
        try:
            # Procesar audio objetivo
            if self.processor.target_audio is not None:
                audio_data['target'] = self._normalize_audio(self.processor.target_audio)
                
            # Procesar audio de referencia
            if self.processor.reference_audio is not None:
                audio_data['reference'] = self._normalize_audio(self.processor.reference_audio)
                
            # Procesar resultado
            if self.processor.result_audio is not None:
                audio_data['result'] = self._normalize_audio(self.processor.result_audio)
                
        except Exception as e:
            self.logger.error(f"Error al obtener datos de audio: {str(e)}")
            
        return audio_data

    def _normalize_audio(self, audio):
        """Normaliza el audio para visualización."""
        try:
            # Verificar que el audio es un array válido
            if not isinstance(audio, np.ndarray):
                return None
                
            # Convertir a mono si es estéreo
            if len(audio.shape) > 1:
                audio = np.mean(audio, axis=1)
                
            # Normalizar a [-1, 1]
            max_val = np.max(np.abs(audio))
            if max_val > 0:
                audio = audio / max_val
                
            return audio
            
        except Exception as e:
            self.logger.error(f"Error al normalizar audio: {str(e)}")
            return None

    def _get_sample_rate(self, audio_type):
        """Obtiene el sample rate del tipo de audio especificado."""
        try:
            if audio_type == 'target':
                return self.processor.target_sr
            elif audio_type == 'reference':
                return self.processor.reference_sr
            else:
                return self.processor.result_sr
        except Exception as e:
            self.logger.error(f"Error al obtener sample rate: {str(e)}")
            return 44100  # Valor por defecto

    def process_logs(self):
        """Procesa los mensajes de log en cola."""
        if not self.root.winfo_exists():
            return
            
        try:
            while True:
                try:
                    record = self.log_queue.get_nowait()
                    msg = self.log_formatter.format(record)
                    self.log_text.insert(tk.END, msg + '\n')
                    
                    # Aplicar colores según el tipo de mensaje
                    if record.levelname == "WARNING":
                        self.log_text.tag_add("warning", "end-2c linestart", "end-1c")
                        self.log_text.tag_config("warning", foreground=THEME['warning'])
                    elif record.levelname == "ERROR":
                        self.log_text.tag_add("error", "end-2c linestart", "end-1c")
                        self.log_text.tag_config("error", foreground=THEME['error'])
                    elif record.levelname == "INFO":
                        self.log_text.tag_add("info", "end-2c linestart", "end-1c")
                        self.log_text.tag_config("info", foreground=THEME['accent'])
                    
                    self.log_text.see(tk.END)
                except queue.Empty:
                    break
        except tk.TclError:
            return
            
        if self.root.winfo_exists():
            self.root.after(100, self.process_logs)

    def update_progress(self, value):
        """Actualiza la barra de progreso."""
        if self.root.winfo_exists():
            self.progress['value'] = value
            self.root.update_idletasks()

    def update_file_info(self, file_type):
        """Actualiza la información del archivo."""
        try:
            info = self.processor.get_audio_info(file_type)
            if info:
                info_text = (
                    f"Sample Rate: {info['sample_rate']} Hz\n"
                    f"Canales: {info['channels']}\n"
                    f"Duración: {info['duration']:.2f} s\n"
                    f"Peak: {info['peak']:.1f} dB\n"
                    f"RMS: {info['rms']:.1f} dB"
                )
                
                if file_type == 'target':
                    self.target_info.configure(text=info_text)
                elif file_type == 'reference':
                    self.reference_info.configure(text=info_text)
        except Exception as e:
            self.logger.error(f"Error al actualizar información del archivo: {str(e)}")

    def process_audio(self):
        """Procesa el audio usando matchering."""
        if not self.target_file or not self.reference_file:
            self._show_error(
                "Error",
                "Debe cargar tanto el audio original como el de referencia"
            )
            return
        
        if self.is_processing:
            return
        
        self.is_processing = True
        self.disable_controls()
        self.progress['value'] = 0
        
        # Limpiar el log
        self.log_text.delete(1.0, tk.END)
        
        def process_thread():
            try:
                processing_success = self.processor.process_audio(self.update_progress)
                
                def update_gui():
                    try:
                        # Verificar el procesamiento y el resultado
                        has_result = (hasattr(self.processor, 'result_audio') and 
                                    self.processor.result_audio is not None and 
                                    isinstance(self.processor.result_audio, np.ndarray) and 
                                    self.processor.result_audio.size > 0)
                        
                        if processing_success and has_result:
                            try:
                                self.update_audio_display()
                                self._show_success(
                                    "Masterización Completada",
                                    "El proceso de masterización ha finalizado exitosamente.\n"
                                    "Puede guardar el resultado cuando lo desee."
                                )
                            except Exception as visual_error:
                                self.logger.error(f"Error en visualización: {str(visual_error)}")
                                self._show_error(
                                    "Error de Visualización",
                                    "La masterización se completó pero hubo un error al mostrar el resultado.\n"
                                    "El archivo aún puede ser guardado correctamente."
                                )
                        else:
                            self._show_error(
                                "Error de Procesamiento",
                                "Ocurrió un error durante el proceso de masterización.\n"
                                "Revise el log para más detalles."
                            )
                    except Exception as gui_error:
                        self.logger.error(f"Error en actualización de GUI: {str(gui_error)}")
                    finally:
                        self.enable_controls()
                        self.is_processing = False
                
                self.root.after(0, update_gui)
                
            except Exception as e:
                self.logger.error(f"Error inesperado en procesamiento: {str(e)}")
                def show_error():
                    self._show_error(
                        "Error Inesperado",
                        "Ocurrió un error durante la masterización.\n"
                        "Revise el log para más detalles."
                    )
                    self.enable_controls()
                    self.is_processing = False
                self.root.after(0, show_error)
        
        threading.Thread(target=process_thread, daemon=True).start()

    def load_target(self):
        """Carga el archivo de audio objetivo."""
        file_types = [
            ("Archivos de audio", "*.wav;*.mp3;*.flac;*.aiff;*.ogg"),
            ("Archivo WAV", "*.wav"),
            ("Archivo MP3", "*.mp3"),
            ("Archivo FLAC", "*.flac"),
            ("Archivo AIFF", "*.aiff"),
            ("Archivo OGG", "*.ogg"),
            ("Todos los archivos", "*.*")
        ]
        
        try:
            file_path = filedialog.askopenfilename(
                title="Seleccionar audio original",
                filetypes=file_types,
                initialdir=self._get_last_directory()
            )
            
            if file_path:
                self._save_last_directory(file_path)
                self.disable_controls()
                
                def load_thread():
                    try:
                        if self.processor.load_target(file_path):
                            self.target_file = file_path
                            self.root.after(0, lambda: self.update_file_info('target'))
                            self.root.after(0, self.update_audio_display)
                        else:
                            self.root.after(0, lambda: self._show_error(
                                "Error al cargar archivo",
                                "No se pudo cargar el archivo de audio original.\n"
                                "Verifique que el archivo esté en un formato soportado y no esté dañado."
                            ))
                    except Exception as e:
                        self.logger.error(f"Error inesperado al cargar archivo: {str(e)}")
                        self.root.after(0, lambda: self._show_error(
                            "Error",
                            f"Error al cargar el archivo:\n{str(e)}"
                        ))
                    finally:
                        self.root.after(0, self.enable_controls)
                
                threading.Thread(target=load_thread, daemon=True).start()
                
        except Exception as e:
            self.logger.error(f"Error al abrir diálogo de archivo: {str(e)}")
            self._show_error(
                "Error",
                "No se pudo abrir el diálogo de selección de archivo."
            )

    def load_reference(self):
        """Carga el archivo de audio de referencia."""
        file_types = [
            ("Archivos de audio", "*.wav;*.mp3;*.flac;*.aiff;*.ogg"),
            ("Archivo WAV", "*.wav"),
            ("Archivo MP3", "*.mp3"),
            ("Archivo FLAC", "*.flac"),
            ("Archivo AIFF", "*.aiff"),
            ("Archivo OGG", "*.ogg"),
            ("Todos los archivos", "*.*")
        ]
        
        try:
            file_path = filedialog.askopenfilename(
                title="Seleccionar audio de referencia",
                filetypes=file_types,
                initialdir=self._get_last_directory()
            )
            
            if file_path:
                self._save_last_directory(file_path)
                self.disable_controls()
                
                def load_thread():
                    try:
                        if self.processor.load_reference(file_path):
                            self.reference_file = file_path
                            self.root.after(0, lambda: self.update_file_info('reference'))
                            self.root.after(0, self.update_audio_display)
                        else:
                            self.root.after(0, lambda: self._show_error(
                                "Error al cargar archivo",
                                "No se pudo cargar el archivo de referencia.\n"
                                "Verifique que el archivo esté en un formato soportado y no esté dañado."
                            ))
                    except Exception as e:
                        self.logger.error(f"Error inesperado al cargar archivo: {str(e)}")
                        self.root.after(0, lambda: self._show_error(
                            "Error",
                            f"Error al cargar el archivo:\n{str(e)}"
                        ))
                    finally:
                        self.root.after(0, self.enable_controls)
                
                threading.Thread(target=load_thread, daemon=True).start()
                
        except Exception as e:
            self.logger.error(f"Error al abrir diálogo de archivo: {str(e)}")
            self._show_error(
                "Error",
                "No se pudo abrir el diálogo de selección de archivo."
            )

    def save_result(self):
        """Guarda el resultado del procesamiento."""
        if not hasattr(self.processor, 'result_audio') or self.processor.result_audio is None:
            self._show_error(
                "Error",
                "No hay resultado para guardar.\n"
                "Debe procesar el audio primero."
            )
            return
        
        try:
            # Generar nombre por defecto
            default_name = self._generate_output_filename()
            
            file_path = filedialog.asksaveasfilename(
                title="Guardar audio masterizado",
                defaultextension=".wav",
                initialfile=default_name,
                filetypes=[("Archivo WAV", "*.wav")],
                initialdir=self._get_last_directory()
            )
            
            if file_path:
                self._save_last_directory(file_path)
                self.disable_controls()
                
                def save_thread():
                    try:
                        if self.processor.save_result(file_path):
                            self.logger.info(f"Resultado guardado en: {file_path}")
                            self.root.after(0, lambda: self._show_success(
                                "Guardado Exitoso",
                                "El archivo se ha guardado correctamente."
                            ))
                        else:
                            self.root.after(0, lambda: self._show_error(
                                "Error al Guardar",
                                "No se pudo guardar el archivo.\n"
                                "Verifique que tenga permisos de escritura en la ubicación seleccionada."
                            ))
                    except Exception as e:
                        self.logger.error(f"Error al guardar: {str(e)}")
                        self.root.after(0, lambda: self._show_error(
                            "Error",
                            f"Error al guardar el archivo:\n{str(e)}"
                        ))
                    finally:
                        self.root.after(0, self.enable_controls)
                
                threading.Thread(target=save_thread, daemon=True).start()
                
        except Exception as e:
            self.logger.error(f"Error al abrir diálogo de guardado: {str(e)}")
            self._show_error(
                "Error",
                "No se pudo abrir el diálogo de guardado de archivo."
            )

    def _generate_output_filename(self):
        """Genera un nombre para el archivo de salida."""
        try:
            if self.target_file:
                base_name = os.path.splitext(os.path.basename(self.target_file))[0]
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                return f"{base_name}_masterizado_{timestamp}.wav"
            return "audio_masterizado.wav"
        except Exception as e:
            self.logger.error(f"Error al generar nombre de archivo: {str(e)}")
            return "audio_masterizado.wav"

    def _get_last_directory(self):
        """Obtiene el último directorio usado."""
        return self.last_directory if hasattr(self, 'last_directory') else os.path.expanduser("~")

    def _save_last_directory(self, file_path):
        """Guarda el último directorio usado."""
        try:
            self.last_directory = os.path.dirname(file_path)
        except Exception as e:
            self.logger.error(f"Error al guardar último directorio: {str(e)}")

    def _show_error(self, title, message):
        """Muestra un mensaje de error."""
        messagebox.showerror(title, message)

    def _show_success(self, title, message):
        """Muestra un mensaje de éxito."""
        messagebox.showinfo(title, message)

    def disable_controls(self):
        """Deshabilita los controles durante el procesamiento."""
        for widget in [self.load_target_btn, self.load_reference_btn,
                      self.process_button, self.save_button]:
            if hasattr(widget, 'state'):
                widget.state(['disabled'])

    def enable_controls(self):
        """Habilita los controles después del procesamiento."""
        for widget in [self.load_target_btn, self.load_reference_btn,
                      self.process_button, self.save_button]:
            if hasattr(widget, 'state'):
                widget.state(['!disabled'])