import requests
from typing import Optional
from src.models.paginacion_model import SunatGreBatchResponse
from src.models.sunat_gre_model import SunatGreModel
import logging

URL_BASE = "https://api-cpe.sunat.gob.pe/v1/contribuyente/gre/comprobantes"


def _create_query_parameters(filter: dict) -> str:
    """
    Convierte un diccionario de filtros en una cadena de parámetros de consulta (query string).

    Args:
        filter (dict): Diccionario con los pares clave-valor de los filtros.

    Returns:
        str: Cadena formateada para URL (ej: "key1=val1&key2=val2").
    Example:
    ```sh
    >>> create_query_parameters({"key1": "val1", "key2": "val2"})
    'key1=val1&key2=val2'
    ```
    """
    query_parameters = ""
    for key, value in filter.items():
        query_parameters += f"{key}={value}&"
    return query_parameters[:-1]


def get_gre_by_ruc_and_serie(token: str, documento: str) -> Optional[SunatGreModel]:
    """
    Obtiene los detalles de una Guía de Remisión Electrónica (GRE) específica mediante su identificador.

    Args:
        token (str): Token de autenticación Bearer.
        documento (str): Identificador del documento en formato RUC-TIPO-SERIE-NUMERO.

    Returns:
        Optional[SunatGreModel]: Instancia del modelo con los datos de la GRE o None si ocurre un error.
    """
    url = f"{URL_BASE}/{documento}"

    payload = {}
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json, text/plain, */*',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'es-ES,es;q=0.9',
        'Host': 'api-cpe.sunat.gob.pe',
        'Origin': 'https://e-factura.sunat.gob.pe',
        'Referer': 'https://e-factura.sunat.gob.pe/',
        'sec-ch-ua': '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors'
    }

    try:
        response = requests.request("GET", url, headers=headers, data=payload)
        response.raise_for_status()
        return SunatGreModel(**response.json())
    except Exception as e:
        logging.error(f"Error al obtener la GRE: {e}")
        return None


def get_gre_bacth(token: str, filter: dict) -> Optional[SunatGreBatchResponse]:
    """
    Realiza una búsqueda masiva de Guías de Remisión según los filtros proporcionados.

    Args:
        token (str): Token de autenticación Bearer.
        filter (dict): Diccionario de filtros (fecInicio, fecFin, etc.).

    Returns:
        Optional[SunatGreBatchResponse]: Modelo con la lista de resultados paginados o None si falla.
    """
    query_parameters = _create_query_parameters(filter)
    url = f"{URL_BASE}?{query_parameters}"

    headers = {
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

    try:
        response = requests.request("GET", url, headers=headers)
        response.raise_for_status()
        return SunatGreBatchResponse(**response.json())
    except Exception as e:
        logging.error(f"Error al obtener la GRE en lote: {e}")
        return None


def get_xml_by_ruc_and_serie(token: str, documento: str) -> Optional[dict]:
    """
    Solicita la descarga del contenido XML de una GRE específica.

    Args:
        token (str): Token de autenticación Bearer.
        ruc (str): RUC del emisor.
        codigo (str): Codigo del comprobante.
        serie (str): Serie del comprobante.
        numero (str): Correlativo del comprobante.

    Returns:
        Optional[dict]: Diccionario con la información del XML (usualmente contiene el base64) o None.
    """
    url = f"{URL_BASE}/{documento}/descarga/xml"

    payload = {}
    headers = {
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

    try:
        response = requests.request("GET", url, headers=headers, data=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logging.error(f"Error al obtener el XML de la GRE: {e}")
        return None
