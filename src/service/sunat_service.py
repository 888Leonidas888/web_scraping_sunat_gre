from src.utils.utils import dict_to_query_params
import requests
from typing import Optional
from src.models.paginacion_model import SunatGreBatchResponse
from src.models.sunat_gre_model import SunatGreModel
import logging

URL_BASE = "https://api-cpe.sunat.gob.pe/v1/contribuyente/gre/comprobantes"


def _get_headers(token: str) -> dict:
    """
    Retorna los headers estandarizados para las peticiones a la API de SUNAT.
    """
    return {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json, text/plain, */*',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'es-ES,es;q=0.9',
        'connection': 'keep-alive',
        'Host': 'api-cpe.sunat.gob.pe',
        'Origin': 'https://e-factura.sunat.gob.pe',
        'Referer': 'https://e-factura.sunat.gob.pe/',
        'sec-ch-ua': '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36'
    }


def get_gre_by_ruc_and_serie(token: str, documento: str) -> Optional[SunatGreModel]:
    """
    Obtiene los detalles de una Guía de Remisión Electrónica (GRE) específica.

    Args:
    ---
        token (str): Token Bearer obtenido de la sesión SOL.
        documento (str): Identificador completo del documento. 
                         Formato: {RUC_EMISOR}-{TIPO_DOC}-{SERIE}-{CORRELATIVO}
                         Ejemplo: "20100364451-09-T023-00018069"

    Returns:
    ---
        Optional[SunatGreModel]: Modelo con la data de la GRE o None si hay error.
    """
    url = f"{URL_BASE}/{documento}"
    try:
        response = requests.get(url, headers=_get_headers(token))
        response.raise_for_status()
        return SunatGreModel(**response.json())
    except Exception as e:
        logging.error(f"Error al obtener la GRE {documento}: {e}")
        return None


def get_gre_bacth(token: str, filter: dict) -> Optional[SunatGreBatchResponse]:
    """
    Realiza una búsqueda masiva de Guías de Remisión según filtros de fecha o estado.

    Args:
    ---
        token (str): Token Bearer de autenticación.
        filter (dict): Diccionario con parámetros de búsqueda.
                       Ejemplo: {"fecInicio": "2024-01-01", "fecFin": "2024-01-31", "page": 1}

    Returns:
    ---
        Optional[SunatGreBatchResponse]: Lista paginada de GREs o None.
    """
    query_params = dict_to_query_params(filter)
    url = f"{URL_BASE}?{query_params}"

    try:
        response = requests.get(url, headers=_get_headers(token))
        response.raise_for_status()
        return SunatGreBatchResponse(**response.json())
    except Exception as e:
        logging.error(f"Error en búsqueda masiva de GRE: {e}")
        return None


def get_xml_by_ruc_and_serie(token: str, documento: str) -> Optional[dict]:
    """
    Solicita el contenido XML (base64) de una GRE específica para su posterior descarga.

    Args:
    ---
        token (str): Token Bearer de autenticación.
        documento (str): Identificador completo del documento.
                         Ejemplo: "20100364451-09-T023-00018069"

    Returns:
    ---
        Optional[dict]: Diccionario con la data del XML o None.
    """
    url = f"{URL_BASE}/{documento}/descarga/xml"
    try:
        response = requests.get(url, headers=_get_headers(token))
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logging.error(f"Error al obtener XML para {documento}: {e}")
        return None
