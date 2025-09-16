# Sistema de Renombrado de PDFs - Biblioteca Banxico

Este sistema automatiza el renombrado de los archivos PDF de los boletines mensuales de la Biblioteca del Banco de México, convirtiéndolos de nombres ininteligibles con GUIDs a nombres legibles y organizados.

## 🔄 Funcionamiento

### Problema Original
Los archivos se descargan con nombres como:
```
202411_{A112FDD6-F25B-79C5-292F-20CC98B97308}.pdf
202412_{265D8120-B130-97EF-74CF-541CBB6A2EE9}.pdf
```

### Solución Implementada
Se renombran automáticamente a:
```
2024-11_Boletin_Biblioteca_Banxico_Noviembre_2024.pdf
2024-08_Boletin_Biblioteca_Banxico_Agosto_2024.pdf
```

## 📋 Scripts Disponibles

### `auto_rename_library_pdfs.py`
- **Función**: Renombrado automático y seguro
- **Uso**: Se ejecuta automáticamente en GitHub Actions
- **Características**:
  - ✅ Detecta archivos ya renombrados (no los procesa dos veces)
  - ✅ Extrae fecha del contenido del PDF (primera página)
  - ✅ Maneja patrones en español (enero, febrero, marzo, etc.)
  - ✅ Logging completo del proceso
  - ✅ Manejo de errores robusto

### `rename_library_pdfs.py`
- **Función**: Versión interactiva con dry-run
- **Uso**: Para pruebas manuales y validación
- **Características**:
  - 🔮 Modo dry-run para previsualizar cambios
  - 🤝 Interacción con el usuario
  - 📊 Reportes detallados

### `analyze_pdf_structure.py`
- **Función**: Análisis de estructura de PDFs
- **Uso**: Para debugging y comprensión del formato
- **Características**:
  - 🔍 Extrae texto de la primera página
  - 📅 Identifica patrones de fecha
  - 📊 Reporta información del documento

## 🚀 Integración con GitHub Actions

El renombrado se ejecuta automáticamente después de cada descarga de biblioteca:

```yaml
- name: Run Library Updates
  run: python scripts/library_updates-monthly.py

- name: Rename Library PDFs  
  run: python auto_rename_library_pdfs.py
```

## 🔧 Algoritmo de Detección

### 1. Extracción de Fecha
- Lee la primera página del PDF
- Busca patrón: `MONTH YYYY` (ej: "JUNIO 2025")
- Convierte mes español a número (junio → 06)

### 2. Detección de Archivos Procesados
```python
def is_already_renamed(filename):
    # Si empieza con YYYY-MM, ya está renombrado
    if re.match(r'^\d{4}-\d{2}', filename):
        return True
    
    # Si solo contiene GUIDs, necesita renombrado
    if re.match(r'^[{]?[0-9A-F-]+[}]?$', core_name):
        return False
```

### 3. Generación de Nombres
```python
def generate_new_filename(date_str):
    # Formato: YYYY-MM_Boletin_Biblioteca_Banxico_MesNombre_YYYY.pdf
    return f"{date_str}_Boletin_Biblioteca_Banxico_{month_name}_{year}.pdf"
```

## 📊 Ejemplo de Ejecución

```
🚀 Starting Banxico Library PDF renaming process
Found 48 PDF files to process

🔍 Processing: 202509_{90149836-DC70-4FFB-6056-601714FE2F2E}.pdf
✅ Renamed: 202509_{90149836-DC70-4FFB-6056-601714FE2F2E}.pdf → 2025-06_Boletin_Biblioteca_Banxico_Junio_2025.pdf

⏭️  Skipping 2024-08_Boletin_Biblioteca_Banxico_Agosto_2024.pdf - Already renamed

📊 SUMMARY - Renamed: 22, Skipped: 26, Errors: 0
```

## 🔒 Características de Seguridad

- **Idempotente**: Seguro ejecutar múltiples veces
- **No destructivo**: Preserva archivos originales si hay conflictos
- **Logging completo**: Rastrea todos los cambios
- **Validación**: Verifica existencia de archivos de destino

## 🛠️ Dependencias

```txt
pdfplumber  # Lectura de PDFs
pypdf       # Procesamiento de PDFs  
python-dateutil  # Manejo de fechas
```

## 📈 Resultados

Después del procesamiento, los archivos quedan organizados cronológicamente:

```
2023-12_Boletin_Biblioteca_Banxico_Diciembre_2023.pdf
2024-01_Boletin_Biblioteca_Banxico_Enero_2024.pdf
2024-02_Boletin_Biblioteca_Banxico_Febrero_2024.pdf
...
2025-09_Boletin_Biblioteca_Banxico_Septiembre_2025.pdf
```

Esto facilita:
- 📅 Ordenamiento cronológico natural
- 🔍 Búsqueda por año/mes específico
- 📊 Análisis y procesamiento automatizado
- 🗂️ Organización lógica del archivo
