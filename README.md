# Master-W

Master-W es una aplicación de masterización de audio basada en referencia, que utiliza la tecnología de Matchering para procesar archivos de audio. La aplicación permite masterizar una pista de audio para que coincida con las características sonoras de una pista de referencia.

## Características

- Interfaz gráfica intuitiva y profesional con tema oscuro
- Visualización en tiempo real de forma de onda y espectro
- Soporte para múltiples formatos de audio (WAV, MP3, FLAC, AIFF, OGG)
- Procesamiento de audio de alta calidad usando Matchering 2.0
- Visualización detallada de información de audio
- Log detallado del proceso de masterización
- Multiplataforma (Windows, Linux)

## Instalación

### Windows
Descargue e instale `Master-W-Setup.exe` desde la sección de [Releases](https://github.com/Wamphyre/Master-W/releases).

### ArchLinux
```bash
sudo pacman -U master-w-1.0.0-1-x86_64.pkg.tar.zst
```

### Desde el código fuente

1. Clone el repositorio:
```bash
git clone https://github.com/Wamphyre/Master-W.git
cd Master-W
```

2. Instale las dependencias:
```bash
pip install -r requirements.txt
```

## Uso

1. Ejecute la aplicación:
   - En Windows: Use el acceso directo creado por el instalador
   - En ArchLinux: Ejecute `master-w`
   - Desde el código fuente: `python main.py`

2. Flujo de trabajo:

   a. **Cargar Audio Original**:
   - Haga clic en "Cargar"
   - Seleccione el archivo de audio que desea masterizar
   - Los formatos soportados incluyen WAV, MP3, FLAC, AIFF y OGG

   b. **Cargar Audio de Referencia**:
   - Haga clic en "Cargar"
   - Seleccione el archivo de audio que servirá como referencia
   - Este debería ser una pista profesionalmente masterizada con el sonido que desea emular

   c. **Procesar**:
   - Haga clic en "Masterizar"
   - El proceso incluye:
     - Análisis de ambos archivos
     - Ajuste de niveles
     - Matching espectral
     - Corrección de niveles
     - Limitación final

   d. **Guardar**:
   - Una vez completado el proceso
   - Haga clic en "Guardar"
   - El resultado se guardará como un archivo WAV de 24 bits

## Visualización

La interfaz muestra dos gráficas principales:

1. **Forma de Onda**:
   - Muestra la amplitud del audio en el tiempo
   - Verde: Audio original
   - Azul: Audio de referencia
   - Amarillo: Audio masterizado

2. **Espectro de Frecuencias**:
   - Muestra la distribución de frecuencias
   - Escala logarítmica de 20Hz a 20kHz
   - Permite visualizar el balance tonal de cada audio

## Información Técnica

La aplicación muestra información detallada de cada archivo:
- Sample Rate
- Número de canales
- Duración
- Nivel Peak en dB
- Nivel RMS en dB

## Log de Proceso

Durante la masterización, se muestra información detallada sobre:
- Estado del proceso
- Análisis de niveles
- Ajustes realizados
- Correcciones aplicadas
- Errores o advertencias si los hay

## Limitaciones

- Los archivos de salida están limitados al formato WAV 24-bit
- El proceso puede tomar tiempo dependiendo del tamaño de los archivos
- Se recomienda que los archivos de entrada tengan calidad similar (mismo sample rate)

## Créditos

Esta aplicación utiliza:
- [Matchering](https://github.com/sergree/matchering) para el procesamiento de audio
- [matplotlib](https://matplotlib.org/) para la visualización
- [soundfile](https://python-soundfile.readthedocs.io/) para la gestión de audio
- [numpy](https://numpy.org/) y [scipy](https://scipy.org/) para procesamiento de señales

## Licencia

Este proyecto está licenciado bajo la Licencia BSD 3-Clause - vea el archivo [LICENSE](LICENSE) para más detalles.

## Autor

Desarrollado con ❤️ por [Wamphyre](https://github.com/Wamphyre)

Si te gusta este proyecto, puedes apoyar su desarrollo comprándome un café en https://ko-fi.com/wamphyre94078
