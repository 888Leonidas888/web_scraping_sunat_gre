import os
from seleniumwire import webdriver
from src.utils.logger import get_logger

logger = get_logger("Browser_Manager")


def initialize_driver(headless: bool = False) -> webdriver.Chrome:
    """
    Configura e inicializa el Chrome WebDriver en modo interceptor.
    Devuelve la instancia del driver y la ruta local de descargas.
    """
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        # sin esta options, navegar en modo oculto falla.
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    else:
        options.add_argument("--start-maximized")

    prefs = {
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "profile.default_content_setting_values.automatic_downloads": 1,
        "safebrowsing.enabled": True,
        # Ocultar popup de contraseñas guardadas en UI
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False
    }
    options.add_experimental_option("prefs", prefs)
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    logger.info(f"Inicializando Chrome Driver (Headless: {headless})...")

    try:
        driver = webdriver.Chrome(options=options)
        return driver
    except Exception as e:
        logger.error(f"Falla crítica al inicializar WebDriver Chrome: {e}")
        raise e
