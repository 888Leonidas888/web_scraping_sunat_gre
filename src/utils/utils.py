import time
import random
import logging
import os


def human_like_type(element, text):
    """
    Simula la escritura humana en un elemento input, con pausas aleatorias.
    """
    for char in text:
        element.send_keys(char)
        # Pausa aleatoria entre caracteres
        time.sleep(random.uniform(0.05, 0.2))
    # Pausa después de terminar de escribir
    time.sleep(random.uniform(0.5, 1.5))


def wait_for_download(download_path: str, timeout: int = 60):
    """
    Espera a que un archivo se descargue completamente en la ruta especificada.

    Args:
        download_path (str): La ruta al directorio de descargas.
        timeout (int): Tiempo máximo de espera en segundos.
    """
    seconds = 0
    download_complete = False
    logging.info(
        f"Esperando la descarga en '{download_path}' durante {timeout} segundos...")

    while not download_complete and seconds < timeout:
        time.sleep(1)
        seconds += 1
        # Busca archivos temporales de descarga de Chrome.
        crdownload_files = [f for f in os.listdir(
            download_path) if f.endswith('.crdownload')]
        if not crdownload_files and any(os.listdir(download_path)):
            # Si no hay archivos .crdownload y la carpeta no está vacía, asumimos que la descarga finalizó.
            download_complete = True
            logging.info(f"Descarga completada en {seconds} segundos.")
    if not download_complete:
        logging.warning(
            f"La descarga no se completó en el tiempo de espera de {timeout} segundos.")
