import logging
import argparse
from src.scraping.scrapper_sunat_gre import start_scrapper


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
        start_scrapper(headless=args.headless)
    else:
        logging.error(
            "El proceso no se inició. Por favor, use el argumento -run para ejecutar la automatización.")
        parser.print_help()
