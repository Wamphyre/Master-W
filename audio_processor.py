import numpy as np
import soundfile as sf
import logging
from datetime import datetime
import os
import matchering as mg

class AudioProcessor:
    def __init__(self):
        self.logger = logging.getLogger('MasterW')
        self.target_audio = None
        self.target_sr = None
        self.reference_audio = None
        self.reference_sr = None
        self.result_audio = None
        self.result_sr = None
        
        # Configuraciones de Matchering
        self.results_folder = "resultados"
        self.sample_rate = 44100  # Sample rate objetivo
        
        # Asegurar que existe el directorio de resultados
        if not os.path.exists(self.results_folder):
            os.makedirs(self.results_folder)

    def load_target(self, file_path):
        """Carga el archivo de audio objetivo."""
        try:
            self.target_audio, self.target_sr = sf.read(file_path)
            
            # Convertir a float32 si es necesario
            if self.target_audio.dtype != np.float32:
                self.target_audio = self.target_audio.astype(np.float32)
            
            # Normalizar si es necesario
            max_val = np.max(np.abs(self.target_audio))
            if max_val > 1.0:
                self.target_audio = self.target_audio / max_val
                
            self.logger.info(f"Audio objetivo cargado: {os.path.basename(file_path)}")
            return True
        except Exception as e:
            self.logger.error(f"Error al cargar audio objetivo: {str(e)}")
            return False

    def load_reference(self, file_path):
        """Carga el archivo de audio de referencia."""
        try:
            self.reference_audio, self.reference_sr = sf.read(file_path)
            
            # Convertir a float32 si es necesario
            if self.reference_audio.dtype != np.float32:
                self.reference_audio = self.reference_audio.astype(np.float32)
            
            # Normalizar si es necesario
            max_val = np.max(np.abs(self.reference_audio))
            if max_val > 1.0:
                self.reference_audio = self.reference_audio / max_val
            
            self.logger.info(f"Audio de referencia cargado: {os.path.basename(file_path)}")
            return True
        except Exception as e:
            self.logger.error(f"Error al cargar audio de referencia: {str(e)}")
            return False

    def process_audio(self, progress_callback=None):
        """Procesa el audio usando matchering."""
        if self.target_audio is None or self.reference_audio is None:
            self.logger.error("Se necesitan tanto el audio objetivo como el de referencia")
            return False

        try:
            # Crear nombres de archivo temporales
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            temp_target = os.path.join(self.results_folder, f"temp_target_{timestamp}.wav")
            temp_reference = os.path.join(self.results_folder, f"temp_reference_{timestamp}.wav")
            result_path = os.path.join(self.results_folder, f"resultado_{timestamp}.wav")

            try:
                # Guardar archivos temporales
                if progress_callback:
                    progress_callback(10)
                
                # Guardar como WAV de 32 bits float
                sf.write(temp_target, self.target_audio, self.target_sr, subtype='FLOAT')
                sf.write(temp_reference, self.reference_audio, self.reference_sr, subtype='FLOAT')

                if progress_callback:
                    progress_callback(30)
                
                self.logger.info("Iniciando proceso de masterización...")
                self.logger.info(f"Procesando archivo objetivo: {temp_target}")
                self.logger.info(f"Usando referencia: {temp_reference}")
                
                # Configurar el logging de matchering
                mg.log(self.logger.info)
                
                # Procesar usando matchering 2.0
                mg.process(
                    target=temp_target,
                    reference=temp_reference,
                    results=[
                        mg.pcm24(result_path)
                    ]
                )
                
                if progress_callback:
                    progress_callback(90)

                # Verificar y cargar resultado
                if os.path.exists(result_path):
                    # Cargar el resultado y verificar que sea válido
                    result_data, result_sr = sf.read(result_path)
                    if result_data is not None and isinstance(result_data, np.ndarray) and result_data.size > 0:
                        self.result_audio = result_data
                        self.result_sr = result_sr
                        self.logger.info("Masterización completada exitosamente")
                        
                        if progress_callback:
                            progress_callback(100)
                        return True
                    else:
                        raise Exception("El archivo de resultado no contiene datos válidos")
                else:
                    raise Exception("No se generó el archivo de resultado")

            except Exception as e:
                self.logger.error(f"Error detallado en matchering: {str(e)}")
                raise

        except Exception as e:
            self.logger.error(f"Error en el proceso de masterización: {str(e)}")
            # Limpiar resultado en caso de error
            self.result_audio = None
            self.result_sr = None
            return False

        finally:
            # Limpieza de archivos temporales
            for temp_file in [temp_target, temp_reference]:
                if os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                    except Exception as e:
                        self.logger.warning(f"No se pudo eliminar archivo temporal {temp_file}: {str(e)}")
            
            # Si hubo error, intentar limpiar el resultado temporal
            if not hasattr(self, 'result_audio') or self.result_audio is None:
                if os.path.exists(result_path):
                    try:
                        os.remove(result_path)
                    except Exception as e:
                        self.logger.warning(f"No se pudo eliminar archivo resultado {result_path}: {str(e)}")

    def save_result(self, file_path):
        """Guarda el resultado del procesamiento."""
        if not hasattr(self, 'result_audio') or self.result_audio is None:
            self.logger.error("No hay resultado para guardar")
            return False

        try:
            sf.write(file_path, self.result_audio, self.result_sr)
            self.logger.info(f"Resultado guardado en: {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error al guardar el resultado: {str(e)}")
            return False

    def get_audio_info(self, audio_type='target'):
        """Obtiene información del audio (target/reference/result)."""
        audio_data = None
        sr = None
        
        if audio_type == 'target' and hasattr(self, 'target_audio'):
            audio_data = self.target_audio
            sr = self.target_sr
        elif audio_type == 'reference' and hasattr(self, 'reference_audio'):
            audio_data = self.reference_audio
            sr = self.reference_sr
        elif audio_type == 'result' and hasattr(self, 'result_audio'):
            audio_data = self.result_audio
            sr = self.result_sr
        
        if audio_data is None or not isinstance(audio_data, np.ndarray) or audio_data.size == 0:
            return None
            
        try:
            # Calcular RMS y convertirlo a dB
            rms = np.sqrt(np.mean(audio_data**2))
            rms_db = 20 * np.log10(rms) if rms > 0 else -100
            
            # Calcular peak y convertirlo a dB
            peak = np.max(np.abs(audio_data))
            peak_db = 20 * np.log10(peak) if peak > 0 else -100
                
            return {
                'duration': len(audio_data) / sr,
                'channels': 2 if len(audio_data.shape) > 1 else 1,
                'sample_rate': sr,
                'peak': peak_db,
                'rms': rms_db
            }
        except Exception as e:
            self.logger.error(f"Error al obtener información de audio: {str(e)}")
            return None