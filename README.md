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

## 📝 Configuración del Entorno (.env)

Crea un archivo `.env` en la raíz con tus llaves del Portal SOL:

```dotenv
# Credenciales SUNAT
RUC_SUNAT = '20XXXXXXXXX'
USUARIO_SUNAT = 'TU_USUARIO'
CONTRASENA_SUNAT = 'TU_CLAVE'
```

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


## 📦 Compilación y Distribución

Para generar un ejecutable independiente (`.exe`) que pueda ser distribuido sin necesidad de instalar Python en la máquina destino, se utiliza **PyInstaller**.

### Comando de Compilación

Ejecuta el siguiente comando desde la raíz del proyecto:

```bash
pyinstaller --add-data "sunat_mappings.db;." --add-data ".env;." --icon "assets/img/iconfinder.ico" --name "ScrapperDetracciones" main.py
```

> [!NOTE]
> Después de la compilación deberá mover el archivo `sunat_mappings.db` y `.env` a la carpeta `dist/ScrapperDetracciones` junto con el ejecutable.
> La base de datos `sunat_mappings.db` es necesaria para que el programa funcione correctamente ya viene cargada de no estarlo puede ejecutar el archvivo `src/utils/populate.db` para cargarla.