# 🚀 SunatDownloader - Híbrido RPA/BPA para Descarga de Detracciones (SPOT)

Este proyecto es una solución híbrida de **RPA (Robotic Process Automation)** y **BPA (Business Process Automation)** diseñada para automatizar la descarga masiva de Constancias de Pago de Detracciones desde el portal SOL de la SUNAT.

Ante la inestabilidad de la plataforma SUNAT (que frecuentemente devuelve errores HTTP 500 al intentar descargar los PDFs de las constancias), este proyecto implementa un innovador mecanismo de redundancia ("Modo Tanque") que reconstruye visualmente el documento a partir de los datos crudos extraídos de las APIs internas.

## ✨ Funcionalidades Principales

- **Orquestación Híbrida**: 
  - **RPA**: Navegación web mediante Selenium para evadir barreras de seguridad, resolver desafíos e interceptar el token transaccional (`Idcache`).
  - **BPA**: Consumo intensivo y en lote de las APIs internas de SUNAT para listar y consultar los datos financieros (reduciendo el tiempo y evitando la navegación click-a-click).
- **Mecanismo de Rescate (Fallback)**: Si el portal SUNAT falla al entregar el HTML/PDF original (Error 500), el sistema toma el JSON de la declaración y utiliza una plantilla inyectada localmente para regenerar el PDF.
- **Aprendizaje Activo en Base de Datos (SQLite)**: El API a veces retorna únicamente los códigos numéricos para "Tipos de Operación", "Bienes/Servicios" y "Tipos de Comprobante". El sistema usa una DB de SQLite para traducir estos códigos, y se "auto-alimenta" leyendo las descripciones reales a partir de los documentos exitosos que sí logró descargar la SUNAT original.
- **Arquitectura Limpia**: Separación estricta entre modelos de datos, flujos de scraping, servicios y base de datos local.
- **Extracción Nativa PDF**: Impresión a PDF utilizando los drivers CDP internos de Chrome (headless) sin dependencias adicionales de sistema.

---

## 📋 Requisitos

- **Python 3.12+**
- **Google Chrome**: Necesario para el componente RPA.
- **Librerías clave**: Pydantic, Selenium-wire, Requests.

---

## 🚀 Instalación

Sigue estos pasos para preparar tu entorno de desarrollo:

1. **Clonar el repositorio**:
   ```bash
   git clone <URL_DEL_REPO>
   cd web_scraping_sunat_gre
   ```

2. **Crear y activar un entorno virtual**:
   ```bash
   python -m venv .dev
   # En Windows:
   .dev\Scripts\activate
   ```

3. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

---

## 🧪 Pruebas Unitarias

El proyecto cuenta con una suite de pruebas automatizadas con `pytest`:

```bash
# Ejecutar todas las pruebas
pytest

# Ejecutar con reporte de verbosidad
pytest -v
```

Las pruebas cubren validaciones de modelos Pydantic, utilitarios de limpieza de nombres y operaciones de base de datos.

---

## ⚙️ Configuración del Entorno (.env)

Crea un archivo `.env` en la raíz del proyecto basándote en la siguiente estructura:

```dotenv
# URLs y Credenciales SUNAT
URL_SUNAT = 'https://www.sunat.gob.pe/ol-ti-itpwconsudet/consultar.do'
RUC_SUNAT = '20XXXXXXXXX'
USUARIO_SUNAT = 'TU_USUARIO'
CONTRASENA_SUNAT = 'TU_CLAVE'
```

> [!IMPORTANT]
> Nunca compartas ni subas el archivo `.env` al repositorio de código fuente.

---

## 🗄️ Configuración de Base de Datos

El sistema utiliza una base de datos **SQLite** (`sunat_mappings.db`) para gestionar los mapeos de bienes y servicios.

1. **Verificación Inicial**: Asegúrate de que el archivo `sunat_mappings.db` exista en la raíz.
2. **Poblar la Base de Datos**: Si es la primera vez que instalas el proyecto o si la base de datos está vacía, debes ejecutar el script de población:
   ```bash
   python src/utils/populate_db.py
   ```
   *Este paso garantiza que los códigos de SUNAT se traduzcan correctamente a descripciones humanamente legibles.*

---

## ▶️ Uso de la Herramienta

El script se ejecuta mediante comandos en la terminal posibilitando su integración con orquestadores empresariales.

```bash
# Ejemplo: Descarga masiva del año 2026 hacia el disco local
python main.py -run --path "C:\SUNAT_Descargas" --year 2026

# Ejemplo: Descarga de un mes específico (abril) en modo invisible hacia una unidad de red
python main.py -run -headless --path "\\Servidor\Contabilidad\Detracciones" --year 2026 --month 4
```

### Argumentos del CLI
- `-run`: Bandera que habilita el proceso de ejecución.
- `-headless`: Ejecuta el motor RPA sin interfaz gráfica (modo servidor).
- `--path`: Ruta raíz (Local o UNC) donde se estructurarán las descargas por Año/Mes y Proveedor.
- `--year`: Año para la consulta masiva.
- `--month`: (Opcional) Un mes en específico (1-12). Si se omite, recorrerá los 12 meses.

---

## 🧱 Arquitectura del Código (`src/`)

- `src/models/`: Modelos de validación con **Pydantic** que formalizan la estructura JSON del API de SUNAT.
- `src/scraping/`: Aislamiento del manejador `selenium-wire` y scripts de navegación (login, clics en menús, captura de red).
- `src/core/`: Consumos HTTP independientes (`requests`) al Portal y operaciones CRUD con SQLite.
- `src/service/`: Lógica de negocio (reconstrucción de plantilla, orquestación de iteraciones y visualización gráfica vía consola).
- `src/utils/`: Control temporal, parseo y validación de nombres de directorios.

---

## 📦 Compilación y Distribución

Para generar un ejecutable independiente (`.exe`) que pueda ser distribuido sin necesidad de instalar Python en la máquina destino, se utiliza **PyInstaller**.

### Comando de Compilación

Ejecuta el siguiente comando desde la raíz del proyecto:

```bash
pyinstaller --add-data "sunat_mappings.db;." --add-data ".env;." --icon "assets/img/iconfinder.ico" --name "ScrapperDetracciones" main.py
```

### Detalles de Distribución:
- **`--windowed`**: Evita que se abra una consola negra al ejecutar el programa (ideal para entorno final de usuario).
- **`--add-data ".env;."`**: Incluye el archivo de configuración en el paquete. *Asegúrate de configurar las credenciales correctas antes de compilar si deseas un paquete pre-configurado.*
- **`--icon`**: Aplica el icono corporativo ubicado en `assets/img/iconfinder.ico`.
- **Salida**: El ejecutable generado se encontrará en la carpeta `dist/SunatDownloader/`.
