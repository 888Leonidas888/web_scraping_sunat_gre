from pydantic import BaseModel, Field
from typing import List, Optional


class ReceptorObs(BaseModel):
    codObs: str
    desObs: str


class Pse(BaseModel):
    razonSocial: Optional[str] = None
    numRuc: str


class Firma(BaseModel):
    idCertificado: str
    digestValue: str
    fecFirma: Optional[str] = None


class Emision(BaseModel):
    fecEmision: str
    indSEE: str
    indOrigen: str
    desNota: str
    desHashQr: str
    desQr: str
    receptorObs: List[ReceptorObs]
    pse: Pse
    firma: Firma
    numIpCliente: Optional[str] = None
    numFecEmision: int
    numRangoHora: int


class Emisor(BaseModel):
    desNombre: str
    numAutorizacionMtc: Optional[str] = None
    indEncSunNumAutorizacionMtc: Optional[str] = None
    indSubContratacion: str
    autorizacion: Optional[str] = None
    subContratador: Optional[str] = None


class Bien(BaseModel):
    numOrden: int
    codTipoDocumento: Optional[str] = None
    desCortaTipoDocumento: Optional[str] = None
    numSerie: Optional[str] = None
    numDocumento: Optional[str] = None
    numItem: Optional[str] = None
    indBienRegulado: str
    codBien: str
    codProductoSunat: Optional[str] = None
    codSubPartida: Optional[str] = None
    codGtin: Optional[str] = None
    desBien: str
    codUniMedida: str
    desUniMedida: str
    numCantidad: float
    indFrecuente: str
    docRelacionado: Optional[str] = None
    numDocTransporte: Optional[str] = None
    numDetalle: Optional[str] = None
    numContenedor: Optional[str] = None
    numPrecinto: Optional[str] = None
    indContenedorVacio: Optional[str] = None


class Traslado(BaseModel):
    codMotivoTraslado: str
    desMotivoTraslado: str
    desMotivoTrasladoOtros: Optional[str] = None
    fecInicioTraslado: Optional[str] = None
    numPlacaVehiculo: Optional[str] = None
    fecEntrega: str
    indModalidadTraslado: str
    desModalidadTraslado: str
    indTrasladoVehiculo: str
    indTransbordo: str
    indRetornoVehicEnvEmbVacio: str
    indRetornoVehicVacio: str
    indPagadorFlete: str
    indTrasladoDua: str
    desTrasladoDua: str
    indTrasladoTotalBienes: str
    numBultosPallets: Optional[str] = None
    desBien: Optional[str] = None
    codUnidadMedidaPb: str
    numPesoBruto: float
    numPesoBrutoItemsSel: Optional[float] = None
    desSustentoPesoBrutoItemsSel: str
    contenedores: Optional[str] = None
    autorizacion: Optional[str] = None
    bien: List[Bien]


class Receptor(BaseModel):
    codTipoDocIdentidad: str
    desTipoDocIdentidad: str
    numDocIdentidad: str
    desNombre: str
    indFrecuente: str


class SunatGreModel(BaseModel):
    id: str
    codCpe: str
    numRuc: str
    cantidad: Optional[float] = None
    codTipoCpe: str
    numSerie: str
    numCpe: int
    codEstado: str
    desEstado: str
    emision: Emision
    emisor: Emisor
    traslado: Traslado
    receptor: Receptor
