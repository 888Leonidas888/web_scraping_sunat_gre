import sqlite3
import re
from typing import Optional
from src.utils.logger import get_logger

logger = get_logger("DB_Repository")
DB_NAME = "sunat_mappings.db"

def init_db() -> None:
    """Inicializa la base de datos de mapeos si no existe."""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mappings (
                tipo TEXT,
                codigo TEXT,
                descripcion TEXT,
                PRIMARY KEY (tipo, codigo)
            )
        ''')
        # Seed inicial de mapeos básicos comprobados que ayudan en las primeras descargas
        seed_data = [
            ('comprobante', '01', '01 - FACTURA'),
            ('documento', '06', '06 - REG. UNICO DE CONTRIBUYENTES'),
            ('operacion', '01', '01 - Venta de bienes o prestaci&oacute;n de servicios'),
            ('bien', '037', '037 - Dem&aacute;s Servicios gravados con el IGV')
        ]
        cursor.executemany('INSERT OR IGNORE INTO mappings VALUES (?,?,?)', seed_data)
        conn.commit()
    except Exception as e:
        logger.error(f"Error al inicializar la BD SQLite: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

def get_mapping(tipo: str, codigo: str) -> str:
    """
    Busca la descripción de un código específico en la BD.
    Si no lo encuentra de manera exacta, devuelve el código como fallback.
    """
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('SELECT descripcion FROM mappings WHERE tipo=? AND codigo=?', (tipo, codigo))
        res = cursor.fetchone()
        conn.close()
        return res[0] if res else f"{codigo} - DESC"
    except Exception as e:
        logger.error(f"Error en get_mapping ({tipo}-{codigo}): {e}")
        return f"{codigo} - DESC"

def update_mappings_from_html(html_content: str) -> None:
    """
    Aprendizaje Automático:
    Extrae descripciones completas del HTML original devuelto con éxito por SUNAT
    y actualiza la Base de Datos para que el Modo Tanque las aproveche en el futuro.
    """
    try:
        patterns = {
            'comprobante': r'Tipo de Comprobante</td>\s*<td.*?>(.*?)</td>',
            'operacion': r'Tipo de operaci&oacute;n</td>\s*<td.*?>(.*?)</td>',
            'bien': r'Bien &oacute; servicio</td>\s*<td.*?>(.*?)</td>',
            'documento': r'Tipo de Documento del Adquiriente</td>\s*<td.*?>(.*?)</td>'
        }
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        updated_count = 0
        for tipo, pattern in patterns.items():
            match = re.search(pattern, html_content, re.IGNORECASE | re.DOTALL)
            if match:
                desc = match.group(1).replace("<br>", "").replace("\n", "").strip()
                # El código suele venir al frente de la cadena: "01 - FACTURA"
                codigo = desc.split(' ')[0].strip()
                if codigo:
                    cursor.execute('INSERT OR REPLACE INTO mappings VALUES (?,?,?)', (tipo, codigo, desc))
                    updated_count += 1
                    
        conn.commit()
        conn.close()
        if updated_count > 0:
            logger.debug(f"DB Aprendizaje Dinámico alojó {updated_count} nuevos mappings del documento original.")
    except Exception as e:
        logger.error(f"Error al actualizar mapeos desde HTML: {e}")
