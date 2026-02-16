from pydantic import BaseModel


class SunatFilterRequest(BaseModel):
    """
    Modelo para los parámetros de búsqueda masiva de GRE en la API de SUNAT.
    """
    numRucEmisor: str
    numRucReceptor: str
    codCpe: str = "09"  # Por defecto Guía de Remisión Remitente
    numSerie: str = ""
    numCpe: str = ""
    fecEmisionIni: str
    fecEmisionFin: str
    codEstado: str = ""
    codSubEstado: str = ""
    rangoHoras: str = "1,2,3,4,5,6"
    page: int = 1
    per_page: int = 100
    tipBusqueda: str = "2"
