import os
import logging
import argparse
from src.core.download_sunat_gre import process_main_sunat
from dotenv import load_dotenv


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s', filename='app.log')


def run_automation():
    """Carga las credenciales y ejecuta el proceso de automatización."""
    load_dotenv()

    URL_SUNAT = 'https://www.sunat.gob.pe/sol.html'
    RUC = os.getenv('RUC_SUNAT', '')
    USUARIO = os.getenv('USUARIO_SUNAT', '')
    CONTRASENA = os.getenv('CONTRASENA_SUNAT', '')

    if all(v == '' for v in [RUC, USUARIO, CONTRASENA]):
        logging.error(
            "Por favor, asegúrese de que las variables de entorno RUC_SUNAT, USUARIO_SUNAT y CONTRASENA_SUNAT estén configuradas correctamente.")
    else:
        process_main_sunat(URL_SUNAT, RUC, USUARIO, CONTRASENA)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Automatización para descargar Guías de Remisión de SUNAT.")
    parser.add_argument('-run', action='store_true',
                        help='Ejecuta el proceso de automatización.')

    args = parser.parse_args()

    if args.run:
        run_automation()
    else:
        logging.error(
            "El proceso no se inició. Por favor, use el argumento -run para ejecutar la automatización.")
        parser.print_help()
