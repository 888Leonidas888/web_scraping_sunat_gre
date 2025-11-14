# Automatización de Descarga de Guías de Remisión (SUNAT)

Este proyecto contiene un script de Python que automatiza el proceso de descarga masiva de Guías de Remisión Electrónicas (GRE) en formato XML desde el portal SOL de la SUNAT (Perú).

## Funcionalidades Principales

- **Inicio de Sesión Automático**: Ingresa al portal SOL de SUNAT con las credenciales proporcionadas.
- **Navegación Compleja**: Navega a través de los menús y submenús del portal hasta llegar a la sección de consulta de GRE.
- **Relleno de Formularios**: Completa automáticamente los filtros de búsqueda, como el rango de fechas y el tipo de comprobante.
- **Selección y Descarga**: Selecciona todos los resultados de la búsqueda y descarga los archivos XML correspondientes.
- **Gestión de Descargas**: Espera activamente a que los archivos se descarguen por completo antes de finalizar.
- **Cierre Automático**: Cierra el navegador de forma automática una vez que el proceso ha concluido.

---

## Requisitos

Para ejecutar este script, necesitas tener instalado lo siguiente:

- **Python 3.7+**
- **Google Chrome**: El script utiliza Chrome para la automatización.
- Las librerías de Python listadas en `requirements.txt`.

---

## ⚙️ Instalación

1.  **Clona o descarga este repositorio:**
    ```bash
    git clone <URL-DEL-REPOSITORIO>
    cd <NOMBRE-DEL-DIRECTORIO>
    ```

2.  **(Recomendado) Crea un entorno virtual:**
    ```bash
    python -m venv venv
    ```
    Y actívalo:
    - En Windows: `venv\Scripts\activate`
    - En macOS/Linux: `source venv/bin/activate`

3.  **Instala las dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

---

## 📝 Configuración

Antes de ejecutar el script, debes configurar tus credenciales de acceso a la SUNAT.

Abre el archivo `.env` y modifica las siguientes variables con tus datos:

```dotenv
RUC_SUNAT = 'TU_NUMERO_DE_RUC'
USUARIO_SUNAT = 'TU_USUARIO_SOL'
CONTRASENA_SUNAT = 'TU_CLAVE_SOL'
```

>[!NOTE]
> El archivo `.env` debe estar en la raiz del proyecto.

> **⚠️ Advertencia de Seguridad**
> No es una buena práctica mantener credenciales directamente en el código fuente, especialmente si planeas compartir el proyecto o subirlo a un repositorio público. Se recomienda utilizar variables de entorno.

---

## ▶️ Uso

Una vez configurado, simplemente ejecuta el script desde tu terminal:

```bash
python main.py -run
```

El script iniciará el navegador, realizará todo el proceso de forma automática y guardará los archivos XML descargados en una carpeta llamada `descargas_sunat` dentro del directorio del proyecto. Al finalizar, el navegador se cerrará solo.

---

## 📄 Estructura del Proyecto

```
├── descargas_sunat/  # Carpeta donde se guardan los XML (creada automáticamente)
├── src
├── .gitignore        # Archivos y carpetas ignorados por Git
├── main.py          # El script principal de automatización
├── README.md         # Este archivo
└── requirements.txt  # Lista de dependencias de Python
```

## 🤖 Crear ejecutable

Use el siguiente comando para crear un ejecutable:

```python
pyinstaller --windowed --add-data ".env;." --icon "src/assets/img/icon_xml_256_30060.ico" --name "SunatDownloader" main.py
```
---