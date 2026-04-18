from pydantic import BaseModel, Field
from typing import Optional

class PagoDetraccion(BaseModel):
    """
    Modelo representativo de un comprobante de pago de detracciones según el API de SUNAT.
    Ayuda a procesar con seguridad la data JSON para inyectarla en el HTML reconstruido.
    """
    num_constancia: Optional[str] = Field(default="", alias="num_constancia")
    cod_usuario_sol: Optional[str] = Field(default="")
    num_cuenta: Optional[str] = Field(default="")
    
    # Proveedor
    num_ruc_proveedor: Optional[str] = Field(default="")
    des_prov: Optional[str] = Field(default="")
    
    # Adquiriente
    tip_doc_adq: Optional[str] = Field(default="")
    num_doc_adq: Optional[str] = Field(default="")
    des_adq: Optional[str] = Field(default="")
    
    # Atributos Codificados a Mapear mediante SQLite
    tip_operacion: Optional[str] = Field(default="")
    tip_bien: Optional[str] = Field(default="")
    cod_tipcomprobante: Optional[str] = Field(default="")
    
    # Data Monetaria y Tiempo
    mto_deposito: Optional[float] = Field(default=0.0)
    fec_pago: Optional[int] = Field(default=0)  # Epoch timestamp en milisegundos

    # Período y Serie
    per_tributario: Optional[str] = Field(default="")
    num_serie: Optional[str] = Field(default="")
    num_comprobante: Optional[str] = Field(default="")
    num_pres: Optional[int] = Field(default=0)

    class Config:
        populate_by_name = True
        extra = "ignore"
