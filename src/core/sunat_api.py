import time
import requests
from typing import Optional, Dict, Any
from src.utils.logger import get_logger

logger = get_logger("API_Client")

def download_detracciones_api(token: str, fecha_inicio: str, fecha_fin: str) -> Optional[Dict[str, Any]]:
    """
    Llama a la API interna de SUNAT para listar todos los pagos de un periodo.
    Evita navegar la grilla de UI, devolviendo un JSON puro con cientos de registros rápidamente.
    """
    url = "https://e-plataformaunica.sunat.gob.pe/v1/recaudacion/tributaria/declapago/detracciones/t/consultar"
    headers = {
        "Idcache": token,
        "idformulario": "*MENU*",
        "Content-Type": "application/json",
        "Referer": "https://e-plataformaunica.sunat.gob.pe/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    params = {
        "fechaInicio": fecha_inicio,
        "fechaFin": fecha_fin,
        "tipoCuenta": "1",
        "tipoConsulta": "pagosIndividuales",
        "periodo": "",
        "_": str(int(time.time() * 1000))
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        if response.status_code == 200:
            return response.json()
        logger.error(f"Error listando detracciones ({response.status_code}): {response.text}")
        return None
    except Exception as e:
        logger.error(f"Excepción HTTP listando detracciones: {e}")
        return None


def download_constancia_api(token: str, num_constancia: str) -> Optional[str]:
    """
    Llama al endpoint que descarga el HTML nativo del comprobante/constancia SPOT.
    Suele fallar (HTTP 500) por inestabilidad de SUNAT.
    """
    url = "https://e-plataformaunica.sunat.gob.pe/v1/recaudacion/tributaria/declapago/detracciones/t/descargarconstancia"
    headers = {
        "Idcache": token,
        "idformulario": "*MENU*",
        "Referer": "https://e-plataformaunica.sunat.gob.pe/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    params = {"numeroConstancia": num_constancia}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        if response.status_code == 200:
            return response.text # Retorna la plantilla HTML generada por el backend SUNAT
        logger.warning(f"SUNAT falló al generar constancia {num_constancia} orig. (Status {response.status_code}). Se procederá en Modo Tanque.")
        return None
    except Exception as e:
        logger.error(f"Excepción HTTP al descargar la constancia HTML {num_constancia}: {e}")
        return None
