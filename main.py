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

logger = get_logger("Main")

def main():
    parser = argparse.ArgumentParser(
        description="SunatDownloader - RPA & BPA para SPOT (Detracciones)",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""Ejemplos:
  python main.py -run --path "C:\\SUNAT" --year 2026
  python main.py -run -headless --path "\\\\Servidor\\Descargas" --year 2026 --month 4"""
    )
    parser.add_argument('-run', action='store_true', help="Ejecuta el proceso RPA de extracción de Token y posterior BPA.")
    parser.add_argument('-headless', action='store_true', help="Oculta la ventana de Chrome durante el RPA (Ideal para Servidor).")
    parser.add_argument('--path', type=str, help="Carpeta o ruta de red donde guardar PDFs.")
    parser.add_argument('--year', type=int, help="Año del periodo de pagos.")
    parser.add_argument('--month', type=int, help="(Opcional) Un mes específico en numérico (1-12).")

    args = parser.parse_args()

    if not args.run:
        parser.print_help()
        return

    # Validaciones Obligatorias
    if not args.path:
        print("\n[ERROR] Debes proveer una ruta con el parámetro --path")
        return
    if not args.year:
        print("\n[ERROR] Debes proveer un año con el parámetro --year")
        return
    if args.month and not (1 <= args.month <= 12):
        print("\n[ERROR] El mes debe ser de 1 al 12")
        return

    logger.info("=== INICIANDO SUNAT DOWNLOADER ===")
    
    # Init Backend SQLite
    init_db()

    # Calcular meses a consultar
    meses_a_procesar = [args.month] if args.month else list(range(1, 13))

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
        print(f"=== PROCESANDO DESCARGAS PARA EL {args.year} ===")
        for mes in meses_a_procesar:
            last_day = calendar.monthrange(args.year, mes)[1]
            f_ini = f"01/{mes:02d}/{args.year}"
            f_fin = f"{last_day:02d}/{mes:02d}/{args.year}"
            
            month_name = datetime(args.year, mes, 1).strftime("%B").capitalize()
            path_mes = os.path.join(args.path, str(args.year), f"{mes:02d}_{month_name}")
            os.makedirs(path_mes, exist_ok=True)
            
            logger.info(f"-> BPA Consultando Petición API para Periodo: {mes:02d}/{args.year}")
            print(f"\n=> MES: {month_name.upper()} ({f_ini} al {f_fin})")
            
            api_res = download_detracciones_api(token, f_ini, f_fin)
            
            if api_res:
                count = api_res.get('resultado', [])
                print(f"=> DOCUMENTOS ENCONTRADOS: {len(count)}")

                pdf_driver, _ = initialize_driver(headless=True)
                try:
                    process_massive_downloads(pdf_driver, token, api_res, path_mes)
                finally:
                    pdf_driver.quit()
                
                # Evasión (Pausar entre meses)
                if len(meses_a_procesar) > 1 and mes != meses_a_procesar[-1]:
                    w = random.uniform(5, 10)
                    time.sleep(w)
            else:
                logger.warning(f"La API de SUNAT retornó datos nulos/inválidos para {mes:02d}/{args.year} o no hay pagos.")
                
        print("\n[OK] AUTOMATIZACIÓN COMPLETADA CON ÉXITO.\n")
    except Exception as e:
        logger.error(f"Falla total irrecuperable en Fase BPA: {e}")

if __name__ == "__main__":
    main()
