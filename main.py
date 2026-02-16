import logging
import argparse
from src.scraping.scrapper_sunat_gre import start_scrapper
from src.core.proccess import run_massive_query_process

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s', filename='app.log')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Automatización para descargar Guías de Remisión de SUNAT.")
    parser.add_argument('-run', action='store_true',
                        help='Ejecuta el proceso de automatización.')
    parser.add_argument('-headless', action='store_true',
                        help='Ejecuta el navegador sin interfaz gráfica.')
    parser.add_argument('-help', action='help',
                        help='Muestra este mensaje de ayuda y sale.')

    args = parser.parse_args()

    if args.run:
        try:
            import os
            from dotenv import load_dotenv
            load_dotenv()

            ruc_receptor = os.getenv('RUC_RECEPTOR')
            emitters_raw = os.getenv('EMITTER_RUCS', '')
            emitter_rucs = [r.strip()
                            for r in emitters_raw.split(',') if r.strip()]

            if not ruc_receptor or not emitter_rucs:
                logging.error(
                    "Faltan configurar RUC_RECEPTOR o EMITTER_RUCS en el archivo .env. Asegúrese de que ambas variables estén definidas y no estén vacías.")
            else:
                token = start_scrapper(headless=args.headless)
                if token:
                    run_massive_query_process(
                        token, ruc_receptor, emitter_rucs)
                else:
                    logging.error("No se pudo obtener el token de SUNAT.")

        except Exception as e:
            logging.error(f"Error crítico en el orquestador principal: {e}")
    else:
        logging.error(
            "El proceso no se inició. Por favor, use el argumento -run para ejecutar la automatización.")
        parser.print_help()
