import pytest
import sqlite3
import os
from unittest.mock import patch
from src.core.db_repository import init_db, get_mapping

# Nombre de la DB de prueba
TEST_DB = "test_mappings.db"

@pytest.fixture(autouse=True)
def mock_db_name():
    # Parcheamos el nombre de la base de datos en el módulo original
    with patch("src.core.db_repository.DB_NAME", TEST_DB):
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)
        yield
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)

def test_init_db():
    init_db()
    conn = sqlite3.connect(TEST_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM mappings")
    count = cursor.fetchone()[0]
    conn.close()
    # Debe haber al menos los registros de seed_data
    assert count >= 4

def test_get_mapping_success():
    init_db()
    # Probar un valor del seed
    desc = get_mapping('comprobante', '01')
    assert "FACTURA" in desc

def test_get_mapping_fallback():
    init_db()
    # Probar un valor que no existe
    desc = get_mapping('bien', '999')
    assert desc == "999 - DESC"
