import os
import pandas as pd
from typing import Tuple, Set, List
from src.utils.logger import get_logger

logger = get_logger("Excel_Reader")

def get_excel_filters(filepath: str) -> Tuple[List[Tuple[int, int]], Set[Tuple[str, str]]]:
    """
    Lee el archivo Excel y devuelve:
    1. Una lista de tuplas únicas (año, mes) para saber qué consultar a la API.
    2. Un set ultra-rápido de tuplas (RUC, COD_DETRACCION) para filtrar en el iterador.
    """
    if not os.path.exists(filepath):
        logger.error(f"El archivo Excel no existe en la ruta: {filepath}")
        return [], set()

    try:
        # Cargar excel asumiendo que los tipos numéricos grandes como RUC o Constancias se formen como STRING
        df = pd.read_excel(filepath, dtype={'RUC': str, 'COD DETRACCION': str, 'ANIO': int, 'MES': int})
        
        # Limpiar posibles nulos y espacios en blanco
        df = df.dropna(subset=['RUC', 'COD DETRACCION', 'ANIO', 'MES'])
        df['RUC'] = df['RUC'].str.strip()
        df['COD DETRACCION'] = df['COD DETRACCION'].str.strip()

        # Extraer pares únicos de Año/Mes
        periodos_unicos = df[['ANIO', 'MES']].drop_duplicates()
        lista_periodos = list(periodos_unicos.itertuples(index=False, name=None))
        
        # Extraer Set de tuplas para búsqueda O(1) de descargas requeridas
        filtro_df = df[['RUC', 'COD DETRACCION']].drop_duplicates()
        set_filtros = set(filtro_df.itertuples(index=False, name=None))
        
        logger.info(f"Excel cargado OK. {len(set_filtros)} facturas para descargar en {len(lista_periodos)} periodos.")
        return lista_periodos, set_filtros

    except Exception as e:
        logger.error(f"Fallo al procesar el archivo Excel: {e}")
        return [], set()
