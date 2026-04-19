import pytest
from src.models.pago_model import PagoDetraccion

def test_pago_model_basic():
    data = {"num_constancia": "123456", "mto_deposito": 150.50}
    pago = PagoDetraccion(**data)
    assert pago.num_constancia == "123456"
    assert pago.mto_deposito == 150.50

def test_pago_model_alias():
    # El alias para num_constancia es num_constancia (mismo nombre), 
    # pero verificamos que funcione con la data real del API si viniera distinta.
    data = {"num_constancia": "CONST-001"}
    pago = PagoDetraccion(**data)
    assert pago.num_constancia == "CONST-001"

def test_pago_model_defaults():
    pago = PagoDetraccion()
    assert pago.num_constancia == ""
    assert pago.mto_deposito == 0.0
    assert pago.per_tributario == ""

def test_pago_model_extra_ignore():
    data = {"num_constancia": "123", "campo_extra": "valor_extra"}
    pago = PagoDetraccion(**data)
    assert pago.num_constancia == "123"
    # No debería fallar por campos extras según Config.extra = "ignore"
    assert not hasattr(pago, "campo_extra")
