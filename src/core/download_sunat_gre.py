"""
Automatiza el proceso de login y descarga de Guías de Remisión Electrónicas (GRE)
desde la página de SUNAT utilizando Selenium.
"""

import os
import logging
import time
import random
from selenium import webdriver
from datetime import datetime
from seleniumwire import webdriver as seleniumwire_webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from src.utils.utils import human_like_type, wait_for_download
from typing import Optional


def initialize_driver(download_path: str, headless: bool = False) -> Optional[webdriver.Chrome]:
    """
    Inicializa el navegador Chrome con las configuraciones necesarias para la descarga automática.
    Args:
        download_path (str): Ruta donde se guardarán los archivos descargados.
        headless (bool): Indica si se debe ejecutar el navegador en modo sin interfaz gráfica.
    Returns:
        webdriver.Chrome: Instancia del controlador del navegador Chrome.
    """
    try:
        # Usar las opciones de selenium-wire, que heredan de las de Selenium
        options = seleniumwire_webdriver.ChromeOptions()
        # Opciones de selenium-wire para configurar el proxy si es necesario
        seleniumwire_options = {}

        # --- Argumentos para deshabilitar funciones de seguridad ---
        options.add_argument("--disable-gpu")
        # Desactiva explícitamente la protección de descargas de Safe Browsing a nivel de argumento
        options.add_argument("--safebrowsing-disable-download-protection")

        if headless:
            logging.info("Configurando Chrome en modo headless...")
            options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            # Forzar un tamaño de ventana grande y constante en modo headless
            options.add_argument("--window-size=1920,1080")
            # En modo headless a veces es necesario establecer un user-agent para evitar bloqueos básicos
            options.add_argument(
                "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        else:
            options.add_argument("--start-maximized")

        # --- Preferencias para controlar el comportamiento de las descargas (Configuración más robusta) ---
        prefs = {
            "download.default_directory": download_path,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            # Permitir descargas múltiples
            "profile.default_content_setting_values.automatic_downloads": 1,
            # Mantenemos la navegación segura activada...
            "safebrowsing.enabled": True,
            # Desactivar la protección de descargas a nivel de perfil
            "safebrowsing.download_protection.enabled": False
        }

        options.add_experimental_option("prefs", prefs)

        # --- Inicialización de Chrome ---
        logging.info("Inicializando el navegador Chrome...")
        # selenium-wire maneja el driver automáticamente si Chrome está instalado
        # y chromedriver está en el PATH o es manejado por el propio selenium-wire.
        driver = seleniumwire_webdriver.Chrome(
            options=options, seleniumwire_options=seleniumwire_options)
        logging.info("Navegador Chrome inicializado correctamente.")
        return driver
    except Exception as e:
        logging.error(f"Ocurrió un error al inicializar el navegador: {e}")
        return None


def create_download_directory() -> str:
    """
    Crea un directorio para guardar los archivos descargados.
    Returns:
        str: Ruta del directorio donde se guardarán los archivos descargados.
    """
    download_path = os.path.join(os.getcwd(), "descargas_sunat")
    os.makedirs(download_path, exist_ok=True)
    logging.info(f"Los archivos se guardarán en: {download_path}")
    return download_path


def page_main_sunat(driver: webdriver.Chrome, url_sunat: str) -> None:
    """
    Navega a la página principal de SUNAT y abre la ventana de login.

    Args:
        driver (webdriver.Chrome): La instancia del controlador del navegador.
        url_sunat (str): URL de la página principal de SUNAT.
    """
    # Navegar a la URL principal de SUNAT
    logging.info(f"Navegando a la URL: {url_sunat}")
    driver.get(url_sunat)
    time.sleep(random.uniform(2, 4))  # Pausa inicial para que la página cargue

    # Guardar el handle de la ventana principal
    main_window_handle = driver.current_window_handle

    # Esperar y hacer clic en el enlace "Ingresar"
    logging.info("Buscando y haciendo clic en el enlace 'Ingresar'...")
    ingresar_link_xpath = "//a[./span[text()='Ingresar'] and contains(@href, 'tramiteConsulta()')]"
    ingresar_link = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, ingresar_link_xpath))
    )
    ingresar_link.click()
    time.sleep(random.uniform(1, 3))  # Pausa después del clic

    # Esperar a que se abra la nueva ventana y cambiar el control a ella
    logging.info("Esperando la nueva ventana y cambiando el control...")
    WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))

    # Encontrar el handle de la nueva ventana
    all_handles = driver.window_handles
    new_window_handle = [
        handle for handle in all_handles if handle != main_window_handle][0]

    if new_window_handle:
        driver.switch_to.window(new_window_handle)
        logging.info("Control cambiado a la nueva ventana.")
        # Pausa para que la nueva página cargue
        time.sleep(random.uniform(1, 2))
    else:
        # Lanza una excepción si la nueva ventana no se encuentra
        raise Exception("No se pudo encontrar o cambiar a la nueva ventana.")


def login_sunat(driver: webdriver.Chrome, ruc: str, usuario: str, contrasena: str) -> None:
    """
    Realiza el login en la página de SUNAT.
    Args:
        driver (webdriver.Chrome): La instancia del controlador del navegador.
        ruc (str): Número de RUC para el login.
        usuario (str): Nombre de usuario para el login.
        contrasena (str): Contraseña para el login.
    """
    logging.info("Rellenando campos de RUC, Usuario y Contraseña...")
    ruc_input = WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located((By.ID, "txtRuc")))
    human_like_type(ruc_input, ruc)

    usuario_input = WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located((By.ID, "txtUsuario")))
    human_like_type(usuario_input, usuario)

    contrasena_input = WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located((By.ID, "txtContrasena")))
    human_like_type(contrasena_input, contrasena)

    # Hacer clic en el botón "Iniciar sesión"
    logging.info("Haciendo clic en el botón 'Iniciar sesión'...")
    login_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "btnAceptar")))
    login_button.click()

    logging.info("Login exitoso. Navegando por el menú...")
    time.sleep(random.uniform(2, 4))


def selection_tree_gre(driver: webdriver.Chrome) -> None:
    """
    Navega por el menú de SUNAT para llegar a la sección de Consulta de GRE.
    Args:
        driver (webdriver.Chrome): La instancia del controlador del navegador.
    """
    # 1. Clic en la sección "Empresas"
    logging.info("Haciendo clic en la sección 'Empresas'...")
    empresas_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.ID, "divOpcionServicio2"))
    )
    empresas_button.click()
    time.sleep(random.uniform(1, 2.5))

    # 2. Clic en "Guía de Remisión Electrónica" (Nivel 1)
    logging.info(
        "Haciendo clic en 'Guía de Remisión Electrónica' (Nivel 1)...")
    guia_remision_n1_xpath = "//li[@id='nivel1_62']/span[contains(text(),'Guía de Remisión Electrónica')]"
    guia_remision_n1 = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, guia_remision_n1_xpath))
    )
    guia_remision_n1.click()
    time.sleep(random.uniform(1, 2))

    # 3. Clic en "Guía de Remisión Electrónica" (Nivel 2)
    logging.info(
        "Haciendo clic en 'Guía de Remisión Electrónica' (Nivel 2)...")
    guia_remision_n2_xpath = "//li[@id='nivel2_62_1']/span[contains(text(),'Guía de Remisión Electrónica')]"
    guia_remision_n2 = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, guia_remision_n2_xpath))
    )
    guia_remision_n2.click()
    time.sleep(random.uniform(1, 2))

    # 4. Clic en "Consulta de GRE"
    logging.info("Haciendo clic en 'Consulta de GRE'...")
    consulta_gre_xpath = "//li[contains(@class, 'nivel3')]//span[contains(text(), 'Consulta de GRE')]"
    consulta_gre = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, consulta_gre_xpath))
    )
    consulta_gre.click()
    time.sleep(random.uniform(1, 2))

    # 5. Clic en "Consulta de GRE" (Nivel 4, el enlace final)
    logging.info(
        "Haciendo clic en el enlace final 'Consulta de GRE' (Nivel 4)...")
    consulta_gre_final_xpath = "//li[@id='nivel4_62_1_5_1_1']/span[contains(text(), 'Consulta de GRE')]"
    consulta_gre_final = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, consulta_gre_final_xpath))
    )
    consulta_gre_final.click()

    logging.info(
        "Navegación completada. Esperando a que cargue la página de consulta...")
    time.sleep(random.uniform(3, 5))


def windows_iframe_gre(driver: webdriver.Chrome) -> None:
    """
    Cambia el control al iframe correcto dentro de la página de consulta de GRE.
    Args:
        driver (webdriver.Chrome): La instancia del controlador del navegador.
    """
    logging.info(
        "Buscando el iframe correcto dentro del primer div 'iDivApplication'...")
    iframe_xpath = "(//div[@id='iDivApplication'])[1]//iframe[@id='iframeApplication']"
    iframe_element = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, iframe_xpath))
    )
    driver.switch_to.frame(iframe_element)
    logging.info("Control cambiado al iframe correcto.")
    time.sleep(random.uniform(1, 2.5))

    logging.info(
        "Haciendo clic en el botón 'GRE recibidas' usando el XPath completo...")
    gre_recibidas_button_xpath = "/html/body/guia-remision-root/guia-remision-datos-iniciales/div/div/form/div[3]/div[2]/button"
    gre_recibidas_button = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, gre_recibidas_button_xpath))
    )
    gre_recibidas_button.click()
    time.sleep(random.uniform(1, 2))

    logging.info(
        "Haciendo clic en el botón 'Masiva' usando el XPath completo...")
    masiva_button_xpath = "/html/body/guia-remision-root/guia-remision-datos-iniciales/div/div/form/div[4]/div[2]/button"
    masiva_button = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, masiva_button_xpath))
    )
    masiva_button.click()
    time.sleep(random.uniform(1, 2))

    logging.info(
        "Haciendo clic en el botón 'Siguiente' usando el XPath completo...")
    siguiente_button_xpath = "/html/body/guia-remision-root/guia-remision-datos-iniciales/div/div/form/div[5]/div/button"
    siguiente_button = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, siguiente_button_xpath)))
    # Desplazar al elemento para asegurar que sea visible antes de clicar
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", siguiente_button)
    time.sleep(1)
    # Usar JS click si el click estándar falla o es interceptado
    try:
        siguiente_button.click()
    except Exception:
        logging.warning("Click estándar falló, intentando con JavaScript...")
        driver.execute_script("arguments[0].click();", siguiente_button)
    time.sleep(random.uniform(2, 4))


def search_filters_gre(driver: webdriver.Chrome) -> None:
    """
    Aplica los filtros de búsqueda para las GRE.
    Args:
        driver (webdriver.Chrome): La instancia del controlador del navegador.
    """
    logging.info("Aplicando zoom para ver más contenido en la página final...")
    driver.execute_script("document.body.style.zoom='80%'")

    logging.info("Seleccionando el tipo de comprobante 'GRE - Remitente'...")
    gre_remitente_label_xpath = "//label[contains(., 'GRE - Remitente')]"
    gre_remitente_label = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, gre_remitente_label_xpath))
    )
    gre_remitente_label.click()
    time.sleep(random.uniform(0.5, 1.5))

    today = datetime.now()
    fecha_inicio_str = today.strftime("%Y-%m-%d")
    fecha_fin_str = today.strftime("%Y-%m-%d")

    logging.info(
        f"Estableciendo fecha de inicio con JavaScript: {fecha_inicio_str}")
    fecha_inicio_input = WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located((By.ID, "fechaInicio")))
    driver.execute_script("arguments[0].value = arguments[1];",
                          fecha_inicio_input, fecha_inicio_str)
    driver.execute_script(
        "arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", fecha_inicio_input)
    time.sleep(random.uniform(0.5, 1.5))

    logging.info(f"Estableciendo fecha de fin con JavaScript: {fecha_fin_str}")
    fecha_fin_input = WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located((By.ID, "fechaFin")))
    driver.execute_script("arguments[0].value = arguments[1];",
                          fecha_fin_input, fecha_fin_str)
    driver.execute_script(
        "arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", fecha_fin_input)
    time.sleep(random.uniform(0.5, 1.5))

    # logging.info("Seleccionando el rango horario '12:00:00 al 15:59:59'...")
    logging.info("Seleccionando el rango todos los rangos horarios'...")
    for check_id in ["1", "2", "3"]:#, "4", "5", "6"]:
        horario_checkbox = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.ID, check_id)))
        horario_checkbox.click()
        time.sleep(random.uniform(0.5, 1.5))

    logging.info("Haciendo clic en 'Siguiente' para iniciar la búsqueda...")
    buscar_button_xpath = "//button[contains(@class, 'col-xl-3') and normalize-space()='Siguiente']"
    buscar_button = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, buscar_button_xpath)))
    buscar_button.click()

    logging.info("Resultados cargados en la página.")
    time.sleep(random.uniform(1, 4)) # Pequeña pausa adicional por si acaso


def download_gre_all_files(driver: webdriver.Chrome, download_path: str) -> None:
    """
    Descarga todos los archivos GRE disponibles después de aplicar los filtros.
    Args:
        driver (webdriver.Chrome): La instancia del controlador del navegador.
        download_path (str): Ruta donde se guardarán los archivos descargados.
    """
    logging.info(
        "Activando el checkbox principal para seleccionar todos los resultados...")
    check_principal = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.NAME, "checkPrincipal"))
    )
    check_principal.click()
    time.sleep(random.uniform(1, 2))

    logging.info("Haciendo clic en 'Descargar XML'...")
    descargar_button_xpath = "//button[normalize-space()='Descargar XML']"
    descargar_button = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, descargar_button_xpath)))
    descargar_button.click()
    time.sleep(random.uniform(1, 2))

    logging.info("Haciendo clic en 'Aceptar' en el modal de confirmación...")
    aceptar_modal_xpath = "//guia-remision-modal-confirmar//button[normalize-space()='Aceptar']"
    aceptar_modal_button = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, aceptar_modal_xpath)))
    aceptar_modal_button.click()
    
    # Pausa para dar tiempo a que el navegador inicie la descarga del ZIP
    time.sleep(random.uniform(3, 5))

    wait_for_download(download_path, timeout=120)


def extract_auth_token(driver: webdriver.Chrome) -> Optional[str]:
    """
    Busca y extrae el token de Authorization de las peticiones capturadas.

    Args:
        driver (webdriver.Chrome): La instancia del controlador de selenium-wire.
    Returns:
        Optional[str]: El token encontrado o None si no se halla.
    """
    logging.info("Buscando token 'Authorization' en las peticiones de red...")
    # Iterar en reversa para obtener el token más reciente
    for request in reversed(driver.requests):
        auth_header = request.headers.get('Authorization')
        if auth_header and "Bearer" in auth_header:
            logging.info(f"¡Token encontrado en la petición a: {request.url}!")
            return auth_header
    return None


def process_main_sunat(url_sunat: str, ruc: str, usuario: str, contrasena: str, headless: bool = False) -> Optional[str]:
    """
    Función optimizada: Realiza login, navega hasta el módulo GRE, extrae el token
    de sesión y finaliza el proceso para uso posterior vía API.

    Args:
        url_sunat (str): URL de la página principal de SUNAT.
        ruc (str): Número de RUC para el login.
        usuario (str): Nombre de usuario para el login.
        contrasena (str): Contraseña para el login.
        headless (bool): Indica si se debe ejecutar en modo sin interfaz gráfica.

    Returns:
        Optional[str]: El token de Authorization capturado.
    """
    driver = None
    token = None
    try:
        download_path = create_download_directory()
        driver = initialize_driver(download_path, headless=headless)

        if not driver:
            return None

        # 1. Login y navegación base
        page_main_sunat(driver, url_sunat)
        login_sunat(driver, ruc, usuario, contrasena)

        # 2. Navegar al árbol de GRE y entrar al Iframe
        # Este punto dispara las peticiones a la API de SUNAT con el token JWT
        selection_tree_gre(driver)
        windows_iframe_gre(driver)

        # 3. Captura del token
        # Reintentamos brevemente por si la petición tarda unos ms en procesarse
        for i in range(5):
            token = extract_auth_token(driver)
            if token:
                break
            logging.info(f"Reintentando captura de token ({i+1}/5)...")
            time.sleep(1.5)

        if token:
            logging.info("Proceso de captura completado exitosamente.")
            # Opcional: imprimir para que procesos externos lo capturen fácilmente
            print(f"\n[TOKEN_SUCCESS]\n{token}\n")
        else:
            logging.error("No se pudo capturar el token tras la navegación.")

        return token

    except Exception as e:
        logging.error(f"Ocurrió un error durante la automatización: {e}")
        return None
    finally:
        if driver:
            logging.info("Cerrando el navegador.")
            driver.quit()
