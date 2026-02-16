# 🚀 SunatDownloader - Automatización de Guías de Remisión (GRE)

Este proyecto es una solución integral para la automatización del portal SOL de la SUNAT (Perú). Permite la extracción masiva de tokens de sesión, consulta de Guías de Remisión Electrónicas (GRE) a través de APIs oficiales y la preparación de datos para su almacenamiento externo.

## ✨ Funcionalidades Principales

- **Web Scraping Avanzado**: Inicio de sesión automático y captura de tokens de seguridad mediante interceptación de tráfico de red.
- **Consulta Masiva vía API**: Orquestación de peticiones masivas filtradas por RUC emisor, receptor y fecha actual.
- **Arquitectura Limpia**: Separación estricta entre lógica de scraping, servicios y modelos de datos.
- **Resiliencia**: Manejo de errores granular que permite continuar el proceso ante fallas individuales de documentos o emisores.
- **CI/CD Ready**: Automatización de pruebas unitarias mediante GitHub Actions.

---

## 📋 Requisitos

- **Python 3.12+**
- **Google Chrome**: Necesario para la automatización con Selenium.
- **ChromeDriver**: Gestionado automáticamente por `webdriver-manager`.

---

## ⚙️ Instalación

1. **Clona el repositorio:**
   ```bash
   git clone <URL-DEL-REPOSITORIO>
   cd web_scraping_sunat_gre
   ```

2. **Crea y activa un entorno virtual:**
   ```bash
   # En Windows
   python -m venv .dev
   .dev\Scripts\activate
   ```

3. **Instala las dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

---

## 📝 Configuración (.env)

El archivo `.env` es crítico para el funcionamiento. Asegúrese de configurar las siguientes variables:

```dotenv
# Credenciales de acceso al Portal SOL
RUC_SUNAT = '20XXXXXXXXX'
USUARIO_SUNAT = 'USUARIO_SOL'
CONTRASENA_SUNAT = 'CLAVE_SOL'
URL_SUNAT = 'https://www.sunat.gob.pe/sol.html'

# Configuración de búsqueda masiva
RUC_RECEPTOR = '20XXXXXXXXX'
# EMITTER_RUCS: RUCs emisores separados por coma (sin espacios adicionales)
EMITTER_RUCS = '20100364451,20546654261'
```

---

## ▶️ Uso

### Ejecución Principal
Para iniciar el proceso de extracción de token y consulta masiva:
```bash
python main.py -run
```

### Ejecutar Pruebas (Tests)
El proyecto usa `pytest` para asegurar que la lógica de negocio sea correcta:
```bash
# Ejecutar todos los tests unitarios
pytest tests/test_proccess_logic.py
```

### Crear Ejecutable (.exe)
Si necesitas distribuir la herramienta en entornos Windows:
```bash
pyinstaller --windowed --add-data ".env;." --icon "src/assets/img/icon_xml_256_30060.ico" --name "SunatDownloader" main.py
```

---

## 🛠️ Desarrollo y CI/CD

- **GitHub Actions**: Cada vez que realices un `push` a las ramas `main` o `feat/*`, GitHub ejecutará automáticamente los tests definidos para asegurar la integridad del código.
- **Logs**: El sistema genera un archivo `app.log` detallado para auditar cada paso (Token capturado, errores de API, documentos encontrados, etc.).

---

## 📄 Estructura del Proyecto

```
├── .github/workflows/ # Configuración de GitHub Actions
├── src/
│   ├── core/         # Orquestadores y lógica de negocio principal
│   ├── models/       # Validaciones con Pydantic (GRE, Filtros, Paginación)
│   ├── scraping/     # Automatización con Selenium y captura de tokens
│   ├── service/      # Clientes de API (SUNAT y Almacenamiento)
│   └── utils/        # Funciones de apoyo genéricas
├── tests/            # Pruebas unitarias
├── main.py           # Punto de entrada del script
└── requirements.txt  # Dependencias del proyecto
```
