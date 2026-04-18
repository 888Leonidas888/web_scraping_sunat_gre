import os
import argparse
import time
import random
import calendar
from datetime import datetime

from src.utils.logger import get_logger
from src.core.db_repository import init_db
from src.core.sunat_api import download_detracciones_api
from src.scraping.browser_manager import initialize_driver
from src.scraping.sunat_scraper import login_sunat, navigate_to_detracciones, capture_idcache_token
from src.service.detracciones_service import process_massive_downloads
from src.utils.excel_reader import get_excel_filters

logger = get_logger("Main")

def main():
    parser = argparse.ArgumentParser(
        description="SunatDownloader - RPA & BPA para SPOT (Detracciones)",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""Ejemplos:
  python main.py -run --path "C:\\SUNAT" --year 2026
  python main.py -run --path "C:\\SUNAT" --excel "lista_detracciones.xlsx"
  python main.py -run -headless --path "\\\\Servidor\\Descargas" --year 2026 --month 4"""
    )
    parser.add_argument('-run', action='store_true', help="Ejecuta el proceso RPA de extracción de Token y posterior BPA.")
    parser.add_argument('-headless', action='store_true', help="Oculta la ventana de Chrome durante el RPA (Ideal para Servidor).")
    parser.add_argument('--path', type=str, help="Carpeta o ruta de red donde guardar PDFs.")
    parser.add_argument('--year', type=int, help="Año del periodo de pagos (ignorada si se usa --excel).")
    parser.add_argument('--month', type=int, help="(Opcional) Un mes específico en numérico (ignorada si se usa --excel).")
    parser.add_argument('--excel', type=str, help="(Opcional) Ruta al archivo Excel para filtrar qué constancias descargar.")

    args = parser.parse_args()

    if not args.run:
        parser.print_help()
        return

    # Validaciones Obligatorias
    if not args.path:
        print("\n[ERROR] Debes proveer una ruta con el parámetro --path")
        return
    if not args.excel and not args.year:
        print("\n[ERROR] Debes proveer al menos el parámetro --year o --excel")
        return
    if args.month and not (1 <= args.month <= 12):
        print("\n[ERROR] El mes debe ser de 1 al 12")
        return

    logger.info("=== INICIANDO SUNAT DOWNLOADER ===")
    
    # Init Backend SQLite
    init_db()

    # Calcular periodos a consultar: lista de tuplas [(año, mes)]
    filtro_excel = set()
    periodos_a_procesar = []

    if args.excel:
        logger.info("Modo Excel Activado: Extrayendo información...")
        periodos_excel, filtro_excel = get_excel_filters(args.excel)
        if not periodos_excel:
            print("\n[ERROR] El Excel está vacío o no se procesó correctamente.")
            return
        periodos_a_procesar = periodos_excel
    else:
        # Modo Tradicional
        meses = [args.month] if args.month else list(range(1, 13))
        periodos_a_procesar = [(args.year, m) for m in meses]

    # Fase 1: RPA -> Capturar IDCache
    driver, _ = initialize_driver(headless=args.headless)
    token = None
    
    try:
        if login_sunat(driver):
            if navigate_to_detracciones(driver):
                logger.info("Intentando interceptar Token XHR...")
                for _ in range(15):
                    token = capture_idcache_token(driver)
                    if token: break
                    time.sleep(2)
                
                if token:
                    print(f"\n[ÉXITO RPA] Token Idcache capturado: {token[:20]}...\n")
                else:
                    logger.error("Se agotó el tiempo para atrapar el Token.")
                    return
            else:
                logger.error("Fallo durante la navegación RPA.")
                return
        else:
            logger.error("Fallo durante el login en SUNAT.")
            return
            
    finally:
        driver.quit()

    if not token:
        return

    # Fase 2: BPA Masivo -> Peticiones API y Modo Tanque
    try:
        print(f"=== PROCESANDO DESCARGAS MASIVAS ===")
        for index, (anio_param, mes_param) in enumerate(periodos_a_procesar):
            last_day = calendar.monthrange(anio_param, mes_param)[1]
            f_ini = f"01/{mes_param:02d}/{anio_param}"
            f_fin = f"{last_day:02d}/{mes_param:02d}/{anio_param}"
            
            month_name = datetime(anio_param, mes_param, 1).strftime("%B").capitalize()
            path_anio = os.path.join(args.path, str(anio_param))
            os.makedirs(path_anio, exist_ok=True)
            
            logger.info(f"-> BPA Consultando Petición API para Periodo: {mes_param:02d}/{anio_param}")
            print(f"\n=> PERIODO: {month_name.upper()} {anio_param} ({f_ini} al {f_fin})")
            
            api_res = download_detracciones_api(token, f_ini, f_fin)
            
            if api_res:
                count = api_res.get('resultado', [])
                print(f"=> DOCUMENTOS ENCONTRADOS EN API: {len(count)}")

                # Motor PDF sin cabeza
                pdf_driver, _ = initialize_driver(headless=True)
                try:
                    # Se pasa el filtro de Excel (puede estar vacío en modo tradicional)
                    process_massive_downloads(pdf_driver, token, api_res, path_anio, filtro_excel)
                finally:
                    pdf_driver.quit()
                
                # Evasión (Pausar entre meses) solo si hay más por delante
                if len(periodos_a_procesar) > 1 and index < len(periodos_a_procesar) - 1:
                    w = random.uniform(5, 10)
                    time.sleep(w)
            else:
                logger.warning(f"La API de SUNAT retornó datos nulos/inválidos para {mes_param:02d}/{anio_param} o no hay pagos.")
                
        print("\n[OK] AUTOMATIZACIÓN COMPLETADA CON ÉXITO.\n")
    except Exception as e:
        logger.error(f"Falla total irrecuperable en Fase BPA: {e}")

if __name__ == "__main__":
    main()
