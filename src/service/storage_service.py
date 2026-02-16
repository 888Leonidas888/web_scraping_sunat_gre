import logging
from typing import List
from src.models.sunat_gre_model import SunatGreModel
import os
from dotenv import load_dotenv
import requests
load_dotenv()


class StorageService:
    """
    Servicio encargado de enviar los datos extraídos hacia el servicio de almacenamiento (.NET).
    Por ahora funciona como un placeholder.
    """

    def __init__(self):
        api_url = os.getenv('INTERNAL_SERVICE_API', None)
        if not api_url:
            raise ValueError(
                "La variable de entorno INTERNAL_SERVICE_API no está definida.")
        self.api_url = api_url

    def store_gre(self, gre: SunatGreModel) -> bool:
        """
        Envía una GRE individual al servicio externo.
        """
        try:
            logging.info(
                f"Enviando GRE {gre.numSerie}-{gre.numCpe} al servicio de almacenamiento... {self.api_url}")
            url = f"{self.api_url}/api/v1/guia"
            response = requests.post(url, json=gre.model_dump())
            response.raise_for_status()
            return True
        except Exception as e:
            logging.error(
                f"Error al enviar la GRE {gre.numSerie}-{gre.numCpe}: {e}")
            return False
