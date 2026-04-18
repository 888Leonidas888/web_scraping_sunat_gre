import os
import time
import base64
from typing import Optional
from dotenv import load_dotenv

from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from src.utils.logger import get_logger
from src.utils.helpers import human_like_type

logger = get_logger("Sunat_Scraper")

def login_sunat(driver: webdriver.Chrome) -> bool:
    """Ejecuta el proceso RPA de login resolviendo flujos de UI y esperas explícitas."""
    load_dotenv()
    url_base = os.getenv('URL_SUNAT')
    ruc = os.getenv('RUC_SUNAT')
    usuario = os.getenv('USUARIO_SUNAT')
    clave = os.getenv('CONTRASENA_SUNAT')

    if not all([url_base, ruc, usuario, clave]):
        logger.error("Error: Faltan credenciales (URL_SUNAT, RUC_SUNAT, USUARIO_SUNAT, CONTRASENA_SUNAT) en .env")
        return False

    driver.get(url_base)
    time.sleep(2)

    try:
        link_xpath = "//a[contains(@href, 'declaraPagoCarrito()')]"
        btn_declaraciones = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, link_xpath)))
        btn_declaraciones.click()
    except Exception as e:
        logger.error(f"Error al buscar enlace inicial 'Mis Declaraciones': {e}")
        return False

    time.sleep(2)
    
    # Manejar popup si se abre en otra pestaña
    if len(driver.window_handles) > 1:
        driver.switch_to.window(driver.window_handles[-1])

    try:
        ruc_input = WebDriverWait(driver, 25).until(EC.visibility_of_element_located((By.ID, "txtRuc")))
        user_input = driver.find_element(By.ID, "txtUsuario")
        pass_input = driver.find_element(By.ID, "txtContrasena")

        human_like_type(ruc_input, ruc)
        human_like_type(user_input, usuario)
        human_like_type(pass_input, clave)

        driver.find_element(By.ID, "btnAceptar").click()
        logger.info("Login en SUNAT enviado.")
        time.sleep(5)
        return True
    except Exception as e:
        logger.error(f"Excepción interactuando con formulario login: {e}")
        return False

def navigate_to_detracciones(driver: webdriver.Chrome) -> bool:
    """Robot de menús: despliega el acordeón hasta Consulta de Pago de Detracciones."""
    try:
        WebDriverWait(driver, 25).until(EC.element_to_be_clickable((By.ID, "divOpcionServicio2"))).click()
        time.sleep(1)

        mis_decl_xpath = "//li[@id='nivel1_55']//span[text()='Mis declaraciones y pagos']"
        WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, mis_decl_xpath))).click()
        time.sleep(1)

        consultas_xpath = "//li[@id='nivel2_55_2']//span[text()='Consultas']"
        WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, consultas_xpath))).click()
        time.sleep(1)

        pres_pago_xpath = "//li[@id='nivel3_55_2_1']//span[text()='Consultas de Presentación y Pago']"
        WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, pres_pago_xpath))).click()
        time.sleep(1)

        detracciones_final_xpath = "//li[@id='nivel4_55_2_1_1_4']//span[text()='Consulta de Pago de Detracciones']"
        WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, detracciones_final_xpath))).click()
        
        logger.info("Módulo de Detracciones cargado exitosamente en navegador.")
        time.sleep(3)
        return True
    except Exception as e:
        logger.error(f"Error RPA al navegar por el árbol de opciones: {e}")
        return False

def capture_idcache_token(driver: webdriver.Chrome) -> Optional[str]:
    """Sniffer de tráfico: rastrea las peticiones y extrae el Idcache XHR."""
    logger.info("Escaneando tráfico de red para capturar el token 'Idcache'...")
    for request in reversed(driver.requests):
        if 'detracciones/t/consultar' in request.url:
            idcache = request.headers.get('Idcache')
            if idcache:
                logger.info(f"Token Idcache interceptado con éxito! : {idcache}")
                return idcache
    return None

def save_html_as_pdf(driver: webdriver.Chrome, html_content: str, filename: str) -> bool:
    """BPA Fallback: Renderiza cualquier HTML local en un PDF nativo utilizando CDP."""
    try:
        b64_html = base64.b64encode(html_content.encode('utf-8')).decode('utf-8')
        driver.get(f"data:text/html;base64,{b64_html}")
        
        print_options = {
            'landscape': False,
            'displayHeaderFooter': False,
            'printBackground': True,
            'scale': 1.0
        }
        # Chrome DevTools Protocol invocación a bajo nivel
        pdf_data = driver.execute_cdp_cmd("Page.printToPDF", print_options)
        
        with open(filename, "wb") as f:
            f.write(base64.b64decode(pdf_data['data']))
        
        return True
    except Exception as e:
        logger.error(f"Error al escribir PDF desde CDP Chrome: {e}")
        return False
