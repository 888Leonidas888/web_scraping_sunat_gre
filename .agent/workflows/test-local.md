---
description: Levantar el proyecto en modo de prueba local y ejecutar tests unitarios
---

Este flujo de trabajo permite ejecutar la automatización localmente y verificar el estado del código mediante pruebas unitarias.

### 1. Sincronizar Dependencias
// turbo
`.dev/Scripts/python -m pip install -r requirements.txt`

### 2. Ejecutar Pruebas Unitarias (Pytest)
// turbo
`.dev/Scripts/python -m pytest tests/`

### 3. Ejecutar Automatización en Local (Modo Visible)
// turbo
`.dev/Scripts/python main.py -run`

### 4. Ejecutar Automatización en Local (Modo Headless)
// turbo
`.dev/Scripts/python main.py -run -headless`
