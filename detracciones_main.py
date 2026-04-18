import os
import logging
import time
import random
import argparse
import requests
import calendar
from datetime import datetime
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from seleniumwire import webdriver as seleniumwire_webdriver

# Configuración de Logging (Solo archivo)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("detracciones.log")
    ]
)

def human_like_type(element, text: str):
    """Escribe texto de forma humana con pausas aleatorias."""
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.05, 0.15))

def initialize_driver(headless: bool = False):
    """Configura e inicializa el WebDriver."""
    options = seleniumwire_webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
    else:
        options.add_argument("--start-maximized")
    
    download_path = os.path.join(os.getcwd(), "descargas_detracciones")
    os.makedirs(download_path, exist_ok=True)
    
    prefs = {
        "download.default_directory": download_path,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "profile.default_content_setting_values.automatic_downloads": 1,
        "safebrowsing.enabled": True
    }
    options.add_experimental_option("prefs", prefs)
    
    logging.info("Inicializando Chrome Driver...")
    driver = seleniumwire_webdriver.Chrome(options=options)
    return driver, download_path

def login_sunat(driver):
    """Realiza el proceso de login."""
    load_dotenv()
    url_base = "https://www.sunat.gob.pe/empresas.html"
    ruc = os.getenv('RUC_SUNAT')
    usuario = os.getenv('USUARIO_SUNAT')
    clave = os.getenv('CONTRASENA_SUNAT')

    if not all([ruc, usuario, clave]):
        logging.error("Faltan credenciales en .env")
        return False

    driver.get(url_base)
    time.sleep(2)

    try:
        link_xpath = "//a[contains(@href, 'declaraPagoCarrito()')]"
        btn_declaraciones = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, link_xpath)))
        btn_declaraciones.click()
    except Exception as e:
        logging.error(f"Error al buscar enlace inicial: {e}")
        return False

    time.sleep(2)
    if len(driver.window_handles) > 1:
        driver.switch_to.window(driver.window_handles[-1])

    try:
        ruc_input = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.ID, "txtRuc")))
        user_input = driver.find_element(By.ID, "txtUsuario")
        pass_input = driver.find_element(By.ID, "txtContrasena")

        human_like_type(ruc_input, ruc)
        human_like_type(user_input, usuario)
        human_like_type(pass_input, clave)

        driver.find_element(By.ID, "btnAceptar").click()
        time.sleep(5)
        return True
    except Exception as e:
        logging.error(f"Error en login: {e}")
        return False

def navigate_to_detracciones(driver):
    """Navega por el menú hasta el módulo de detracciones."""
    try:
        # Clic en Opciones
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "divOpcionServicio2"))).click()
        time.sleep(1)

        # Mis declaraciones y pagos
        mis_decl_xpath = "//li[@id='nivel1_55']//span[text()='Mis declaraciones y pagos']"
        WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, mis_decl_xpath))).click()
        time.sleep(1)

        # Consultas
        consultas_xpath = "//li[@id='nivel2_55_2']//span[text()='Consultas']"
        WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, consultas_xpath))).click()
        time.sleep(1)

        # Consultas de Presentación y Pago
        pres_pago_xpath = "//li[@id='nivel3_55_2_1']//span[text()='Consultas de Presentación y Pago']"
        WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, pres_pago_xpath))).click()
        time.sleep(1)

        # Consulta de Pago de Detracciones
        detracciones_final_xpath = "//li[@id='nivel4_55_2_1_1_4']//span[text()='Consulta de Pago de Detracciones']"
        WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, detracciones_final_xpath))).click()
        
        logging.info("Módulo de Detracciones cargado.")
        time.sleep(3)
        return True
    except Exception as e:
        logging.error(f"Error en navegación: {e}")
        return False

def capture_idcache_token(driver):
    """Extrae el Idcache específicamente de la petición de consultar."""
    logging.info("Escaneando tráfico de red para el token Idcache...")
    for request in reversed(driver.requests):
        if 'detracciones/t/consultar' in request.url:
            idcache = request.headers.get('Idcache')
            if idcache:
                logging.info(f"Token capturado satisfactoriamente.")
                return idcache
    return None

import sqlite3

def init_db():
    """Inicializa la base de datos de mapeos."""
    conn = sqlite3.connect('sunat_mappings.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mappings (
            tipo TEXT,
            codigo TEXT,
            descripcion TEXT,
            PRIMARY KEY (tipo, codigo)
        )
    ''')
    # Valores iniciales básicos (los que ya confirmamos en tu HTML)
    seed_data = [
        ('comprobante', '01', '01 - FACTURA'),
        ('documento', '06', '06 - REG. UNICO DE CONTRIBUYENTES'),
        ('operacion', '01', '01 - Venta de bienes o prestaci&oacute;n de servicios'),
        ('bien', '037', '037 - Dem&aacute;s Servicios gravados con el IGV')
    ]
    cursor.executemany('INSERT OR IGNORE INTO mappings VALUES (?,?,?)', seed_data)
    conn.commit()
    conn.close()

def get_mapping(tipo, codigo):
    """Consulta un mapeo en la base de datos."""
    try:
        conn = sqlite3.connect('sunat_mappings.db')
        cursor = conn.cursor()
        cursor.execute('SELECT descripcion FROM mappings WHERE tipo=? AND codigo=?', (tipo, codigo))
        res = cursor.fetchone()
        conn.close()
        return res[0] if res else f"{codigo} - DESC"
    except:
        return f"{codigo} - DESC"

import re

def update_mappings_from_html(html_content):
    """Extrae descripciones del HTML original y actualiza la DB (Aprendizaje)."""
    try:
        # Ejemplo: <td>Tipo de Comprobante</td><td>01 - FACTURA</td>
        patterns = {
            'comprobante': r'Tipo de Comprobante</td>\s*<td>(.*?)</td>',
            'operacion': r'Tipo de operaci&oacute;n</td>\s*<td>(.*?)</td>',
            'bien': r'Bien &oacute; servicio</td>\s*<td>(.*?)</td>',
            'documento': r'Tipo de Documento del Adquiriente</td>\s*<td>(.*?)</td>'
        }
        conn = sqlite3.connect('sunat_mappings.db')
        cursor = conn.cursor()
        for tipo, pattern in patterns.items():
            match = re.search(pattern, html_content, re.IGNORECASE | re.DOTALL)
            if match:
                desc = match.group(1).strip()
                # El código suele ser el inicio: "01 - ..."
                codigo = desc.split(' ')[0]
                cursor.execute('INSERT OR REPLACE INTO mappings VALUES (?,?,?)', (tipo, codigo, desc))
        conn.commit()
        conn.close()
        logging.info("Base de datos de mapeos actualizada con éxito.")
    except Exception as e:
        logging.error(f"Error al actualizar mapeos desde HTML: {e}")

CONSTANCIA_TEMPLATE = """
<html>
<head>
    <meta charset="UTF-8">
    <title>Constancia de Dep&oacute;sito</title>
    <style type="text/css">
        BODY {{ FONT-SIZE: 10px; MARGIN: 5px; COLOR: #000; FONT-FAMILY: verdana, arial, helvetica, sans-serif; BACKGROUND-COLOR: #ffffff }}
        TABLE {{ FONT-SIZE: 10px; PADDING: 0px; MARGIN: 0px; border: 0; }}
        .bgn {{ background-color: #FFF; FONT-WEIGHT: 900; }}
        .form-table {{ border: 1px solid #4682B4; }}
    </style>
</head>
<body>
    <table width="90%" cellpadding="3" cellspacing="3" align="center" class="form-table">
        <tr class="bgn" align="center"><td>CONSTANCIA DE DEPOSITO</td></tr>
        <tr class="bgn" align="center"><td>SISTEMA DE PAGO DE OBLIGACIONES TRIBUTARIAS D.LEG. 940</td></tr>
    </table>
    <br>
    <table cellpadding="3" cellspacing="2" width="90%" class="form-table" align="center">
        <tr class="bgn"><td>N&uacute;mero de constancia</td><td>{num_constancia}</td></tr>
        <tr><td>Usuario SOL</td><td>{cod_usuario_sol}</td></tr>
        <tr><td>N&deg; Cuenta de detracciones (Banco de la Naci&oacute;n)</td><td>{num_cuenta}</td></tr>
        <tr><td>Tipo de Cuenta:</td><td>Cuenta de Detracciones Convencional</td></tr>
        <tr><td>RUC del Proveedor</td><td>{num_ruc_proveedor}</td></tr>
        <tr><td>Nombre/Raz&oacute;n Social del Proveedor</td><td>{des_prov}</td></tr>
        <tr><td>Tipo de Documento del Adquiriente</td><td>{tip_doc_adq_desc}</td></tr>
        <tr><td>N&uacute;mero de Documento del Adquiriente</td><td>{num_doc_adq}</td></tr>
        <tr><td>Nombre/Raz&oacute;n Social del Adquiriente</td><td>{des_adq}</td></tr>
        <tr><td>Tipo de operaci&oacute;n</td><td>{tip_operacion_desc}</td></tr>
        <tr><td>Bien &oacute; servicio</td><td>{tip_bien_desc}</td></tr>
        <tr><td>Monto del dep&oacute;sito</td><td>S/{mto_deposito}</td></tr>
        <tr><td>Fecha y hora de pago</td><td>{fec_pago_legible}</td></tr>
        <tr><td>Periodo Tributario</td><td>{per_tributario}</td></tr>
        <tr><td>Tipo de Comprobante</td><td>{cod_tip_comp_desc}</td></tr>
        <tr><td>N&uacute;mero de Comprobante</td><td>{serie_correlativo}</td></tr>
        <tr><td>N&uacute;mero de operaci&oacute;n</td><td>{num_pres}</td></tr>
    </table>
</body>
</html>
"""

def reconstruct_constancia_html(pago):
    """Genera el HTML de la constancia consultando la DB dinámica."""
    try:
        dt = datetime.fromtimestamp(pago.get('fec_pago') / 1000)
        fec_pago_legible = dt.strftime("%d/%m/%Y %I:%M:%S %p")
        
        # Mapeos DINÁMICOS desde SQLite
        tip_doc_adq = pago.get('tip_doc_adq', '06')
        tip_doc_adq_desc = get_mapping('documento', tip_doc_adq)
        
        tip_op = pago.get('tip_operacion', '01')
        tip_op_desc = get_mapping('operacion', tip_op)
        
        tip_bien = pago.get('tip_bien', '037')
        tip_bien_desc = get_mapping('bien', tip_bien)
        
        tip_comp = pago.get('cod_tipcomprobante', '01')
        tip_comp_desc = get_mapping('comprobante', tip_comp)

        return CONSTANCIA_TEMPLATE.format(
            num_constancia=pago.get('num_constancia', ''),
            cod_usuario_sol=pago.get('cod_usuario_sol', ''),
            num_cuenta=pago.get('num_cuenta', ''),
            num_ruc_proveedor=pago.get('num_ruc_proveedor', ''),
            des_prov=pago.get('des_prov', ''),
            tip_doc_adq_desc=tip_doc_adq_desc,
            num_doc_adq=pago.get('num_doc_adq', ''),
            des_adq=pago.get('des_adq', ''),
            tip_operacion_desc=tip_op_desc,
            tip_bien_desc=tip_bien_desc,
            mto_deposito=pago.get('mto_deposito', '0.0'),
            fec_pago_legible=fec_pago_legible,
            per_tributario=pago.get('per_tributario', ''),
            cod_tip_comp_desc=tip_comp_desc,
            serie_correlativo=f"{pago.get('num_serie', '')} {pago.get('num_comprobante', '')}",
            num_pres=pago.get('num_pres', '')
        )
    except Exception as e:
        logging.error(f"Error al reconstruir HTML: {e}")
        return None

def download_detracciones_api(token, fecha_inicio, fecha_fin):
    """Llamada directa al API de SUNAT para obtener el JSON de pagos."""
    url = "https://e-plataformaunica.sunat.gob.pe/v1/recaudacion/tributaria/declapago/detracciones/t/consultar"
    headers = {
        "Idcache": token,
        "idformulario": "*MENU*",
        "Content-Type": "application/json",
        "Referer": "https://e-plataformaunica.sunat.gob.pe/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    params = {
        "fechaInicio": fecha_inicio,
        "fechaFin": fecha_fin,
        "tipoCuenta": "1",
        "tipoConsulta": "pagosIndividuales",
        "periodo": "",
        "_": str(int(time.time() * 1000))
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        logging.error(f"Error API ({response.status_code}): {response.text}")
        return None
    except Exception as e:
        logging.error(f"Error en requests: {e}")
        return None

def download_constancia_api(token, num_constancia):
    """Llamada al API que devuelve el HTML de la constancia."""
    url = f"https://e-plataformaunica.sunat.gob.pe/v1/recaudacion/tributaria/declapago/detracciones/t/descargarconstancia"
    headers = {
        "Idcache": token,
        "idformulario": "*MENU*",
        "Referer": "https://e-plataformaunica.sunat.gob.pe/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    params = {"numeroConstancia": num_constancia}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.text # Retorna el HTML
        logging.error(f"Error al obtener constancia {num_constancia}: {response.status_code}")
        return None
    except Exception as e:
        logging.error(f"Error en requests (constancia): {e}")
        return None

import base64

def save_html_as_pdf(driver, html_content, filename):
    """Usa Selenium para convertir HTML a PDF de forma nativa."""
    try:
        # Codificar el HTML en base64 para cargarlo sin crear archivos temporales
        b64_html = base64.b64encode(html_content.encode('utf-8')).decode('utf-8')
        driver.get(f"data:text/html;base64,{b64_html}")
        
        # Opciones de impresión a PDF (Selenium 4+)
        print_options = {
            'landscape': False,
            'displayHeaderFooter': False,
            'printBackground': True,
            'scale': 1.0
        }
        # Ejecutar comando CDP para imprimir a PDF
        pdf_data = driver.execute_cdp_cmd("Page.printToPDF", print_options)
        
        # Guardar el resultado
        with open(filename, "wb") as f:
            f.write(base64.b64decode(pdf_data['data']))
        
        return True
    except Exception as e:
        logging.error(f"Error al convertir HTML a PDF: {e}")
        return False

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn
from rich.panel import Panel
from rich.text import Text

console = Console()

def clean_filename(name):
    """Elimina caracteres inv\u00e1lidos para nombres de carpetas en Windows."""
    return re.sub(r'[<>:"/\\|?*]', '', name).strip()

def process_massive_downloads(driver, token, results, month_path):
    """Itera sobre los resultados organizando por carpetas de Proveedor con Progeso Visual."""
    pagos = results.get('resultado', [])
    if not pagos:
        console.print("[yellow]No hay pagos para descargar.[/yellow]")
        return

    failed_constancias = []
    success_count = 0
    reconstructed_count = 0
    
    total_constancias = [p for p in pagos if p.get('num_constancia')]
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=None, pulse_style="bright_blue"),
        TaskProgressColumn(),
        TimeRemainingColumn(),
        console=console,
        transient=False
    ) as progress:
        
        task = progress.add_task("[cyan]Descargando detracciones...", total=len(total_constancias))

        for pago in total_constancias:
            num_constancia = pago.get('num_constancia')
            ruc_prov = pago.get('num_ruc_proveedor', 'SIN_RUC')
            razon_social = clean_filename(pago.get('des_prov', 'PROVEEDOR_DESCONOCIDO'))
            
            provider_folder = f"{ruc_prov} - {razon_social}"
            provider_path = os.path.join(month_path, provider_folder)
            os.makedirs(provider_path, exist_ok=True)
            
            pdf_filename = os.path.join(provider_path, f"{num_constancia}.pdf")
            
            html_content = download_constancia_api(token, num_constancia)
            
            if html_content:
                is_reconstructed = False
                update_mappings_from_html(html_content)
            else:
                html_content = reconstruct_constancia_html(pago)
                is_reconstructed = True
            
            if html_content:
                if save_html_as_pdf(driver, html_content, pdf_filename):
                    status_text = "[bold yellow]RECONSTRUIDO[/bold yellow]" if is_reconstructed else "[bold green]ORIGINAL[/bold green]"
                    progress.console.print(f"{status_text} | {ruc_prov} | {num_constancia}.pdf")
                    success_count += 1
                    if is_reconstructed: reconstructed_count += 1
                else:
                    failed_constancias.append(num_constancia)
            else:
                failed_constancias.append(num_constancia)
            
            progress.update(task, advance=1)
            time.sleep(random.uniform(0.5, 1.5))

    # Reporte Final con Estilo
    summary = Text()
    summary.append("\n\u2550\u2550\u2550 RESUMEN DE PROCESAMIENTO \u2550\u2550\u2550\n", style="bold cyan")
    summary.append(f"Encontrados: {len(total_constancias)}\n", style="white")
    summary.append(f"Exito: {success_count}\n", style="bold green")
    summary.append(f" -> SUNAT Original: {success_count - reconstructed_count}\n", style="green")
    summary.append(f" -> Reconstruidos: {reconstructed_count}\n", style="yellow")
    if failed_constancias:
        summary.append(f"Fallidos: {len(failed_constancias)} {failed_constancias}\n", style="bold red")
    
    console.print(Panel(summary, border_style="bright_blue"))

def main():
    parser = argparse.ArgumentParser(
        description="SunatDownloader - Automatización de Detracciones",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="Ejemplos:\n"
               "  python detracciones_main.py -run --path \"C:\\SUNAT\" --year 2026\n"
               "  python detracciones_main.py -run --path \"\\\\Servidor\\Descargas\" --year 2026 --month 4"
    )
    parser.add_argument('-run', action='store_true', help="Ejecuta el proceso de automatización")
    parser.add_argument('-headless', action='store_true', help="Ejecuta Chrome en modo oculto")
    parser.add_argument('--path', type=str, help="Ruta base de descarga (Obligatorio)")
    parser.add_argument('--year', type=int, help="Año a consultar (Obligatorio)")
    parser.add_argument('--month', type=int, help="Mes a consultar (Opcional, 1-12)")

    args = parser.parse_args()

    if not args.run:
        parser.print_help()
        return

    # Validaciones Obligatorias
    if not args.path:
        print("ERROR: El parámetro --path es obligatorio.")
        return
    if not args.year:
        print("ERROR: El parámetro --year es obligatorio.")
        return
    if args.month and not (1 <= args.month <= 12):
        print("ERROR: El mes debe estar entre 1 y 12.")
        return

    # Determinando meses a procesar
    meses_a_procesar = [args.month] if args.month else list(range(1, 13))
    
    # Inicializar Base de Datos Dinámica
    init_db()

    driver, _ = initialize_driver(headless=args.headless)
    token = None
    try:
        if login_sunat(driver):
            if navigate_to_detracciones(driver):
                # 1. Capturar Token inicial
                for _ in range(15):
                    token = capture_idcache_token(driver)
                    if token: break
                    time.sleep(2)
                
                if token:
                    print(f"\n[TOKEN_CAPTURED]: {token}\n")
                    driver.quit() # Cerramos navegador de login
                else:
                    print("Error: No se encontró el token de consulta.")
                    driver.quit()
                    return
            else:
                print("Error en navegación.")
                driver.quit()
                return
        else:
            print("Error en login.")
            driver.quit()
            return

        # 2. Procesamiento por Meses
        if token:
            print(f"Iniciando procesamiento para el año {args.year}...")
            
            for mes in meses_a_procesar:
                # Calcular último día del mes
                ultimo_dia = calendar.monthrange(args.year, mes)[1]
                f_ini = f"01/{mes:02d}/{args.year}"
                f_fin = f"{ultimo_dia:02d}/{mes:02d}/{args.year}"
                
                # Crear estructura de carpetas: PATH/AÑO/MES
                nombre_mes = datetime(args.year, mes, 1).strftime("%B").capitalize()
                path_mes = os.path.join(args.path, str(args.year), f"{mes:02d}_{nombre_mes}")
                os.makedirs(path_mes, exist_ok=True)
                
                print(f"\n>>> Consultando: {nombre_mes} {args.year} ({f_ini} - {f_fin})")
                
                res = download_detracciones_api(token, f_ini, f_fin)
                if res:
                    pago_list = res.get('resultado', [])
                    print(f"API OK: {len(pago_list)} registros encontrados.")
                    
                    if pago_list:
                        # Motor PDF Headless independiente por mes
                        pdf_driver, _ = initialize_driver(headless=True)
                        try:
                            process_massive_downloads(pdf_driver, token, res, path_mes)
                        finally:
                            pdf_driver.quit()
                    
                    # Pausa aleatoria entre consultas de meses para evitar baneo (5 a 10 seg)
                    if len(meses_a_procesar) > 1 and mes != meses_a_procesar[-1]:
                        wait = random.uniform(5, 10)
                        print(f"Esperando {wait:.2f}s para el siguiente mes...")
                        time.sleep(wait)
                else:
                    print(f"No se pudieron obtener datos para el mes {mes}.")
            
            print("\n!!! PROCESO FINALIZADO !!!")

    except Exception as e:
        logging.error(f"Error crítico en main: {e}")
        if 'driver' in locals(): driver.quit()

if __name__ == "__main__":
    main()
