import logging
from typing import List
from src.models.sunat_gre_model import SunatGreModel


class StorageService:
    """
    Servicio encargado de enviar los datos extraídos hacia el servicio de almacenamiento (.NET).
    Por ahora funciona como un placeholder.
    """

    def __init__(self, api_url: str = ""):
        self.api_url = api_url

    def store_gre_batch(self, gres: List[SunatGreModel]) -> bool:
        """
        Envía un lote de GREs al servicio externo.
        """
        try:
            logging.info(
                f"Enviando {len(gres)} GREs al servicio de almacenamiento...")
            # Aquí se implementará la llamada HTTP al servicio .NET mas adelante
            # response = requests.post(f"{self.api_url}/api/gre/batch", json=[gre.model_dump() for gre in gres])
            # response.raise_for_status()
            return True
        except Exception as e:
            logging.error(
                f"Error al enviar datos al servicio de almacenamiento: {e}")
            return False

    def store_gre(self, gre: SunatGreModel) -> bool:
        """
        Envía una GRE individual al servicio externo.
        """
        try:
            logging.info(
                f"Enviando GRE {gre.numSerie}-{gre.numCpe} al servicio de almacenamiento...")
            # Aquí se implementará la llamada HTTP
            return True
        except Exception as e:
            logging.error(
                f"Error al enviar la GRE {gre.numSerie}-{gre.numCpe}: {e}")
            return False
