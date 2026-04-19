import pytest
from src.utils.helpers import clean_filename

def test_clean_filename_standard():
    assert clean_filename("Archivo Valido") == "Archivo Valido"

def test_clean_filename_invalid_chars():
    # Caracteres inválidos en Windows: <>:"/\|?*
    input_name = 'Archivo: <Con> *Caracteres* "Prohibidos"?'
    expected = "Archivo Con Caracteres Prohibidos"
    assert clean_filename(input_name) == expected

def test_clean_filename_trim():
    assert clean_filename("  Espacios al inicio y final  ") == "Espacios al inicio y final"

def test_clean_filename_empty():
    assert clean_filename("") == ""
