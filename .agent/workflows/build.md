---
description: Generar el ejecutable de Windows (.exe) usando PyInstaller
---

Este flujo de trabajo automatiza la compilación del proyecto siguiendo los estándares de `GEMINI.md`.

### 1. Preparación de Dependencias
// turbo
`.dev/Scripts/python -m pip install -r requirements.txt`

### 2. Generación del Ejecutable (.exe)
// turbo
`.dev/Scripts/pyinstaller --clean --windowed --add-data ".env;." --icon "src/assets/img/icon_xml_256_30060.ico" --name "SunatDownloader" main.py`

### 3. Limpieza Automática de Residuos
// turbo
`rm -rf build`
// turbo
`rm -f SunatDownloader.spec`
