from pydantic import BaseModel
from typing import List, Optional


class Paginacion(BaseModel):
    totalRegistros: int
    page: int
    per_page: int


class DocGrePorEvento(BaseModel):
    pass


class Item(BaseModel):
    rucEmisor: str
    rucReceptor: str
    codCpe: str
    desCpe: str
    desCortaCpe: str
    numSerie: str
    numCpe: int
    fecEmision: str
    codEstado: str
    desEstado: str
    codSubEstado: Optional[str] = None
    desSubEstado: Optional[str] = None
    cantGreXEvento: int
    docGrePorEvento: List[DocGrePorEvento]


class SunatGreBatchResponse(BaseModel):
    paginacion: Paginacion
    items: List[Item]
