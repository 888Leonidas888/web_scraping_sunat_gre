import sqlite3
import html

def normalize_text(text):
    """Convierte tildes y caracteres especiales a entidades HTML."""
    chars = {
        'á': '&aacute;', 'é': '&eacute;', 'í': '&iacute;', 'ó': '&oacute;', 'ú': '&uacute;',
        'Á': '&Aacute;', 'É': '&Eacute;', 'Í': '&Iacute;', 'Ó': '&Oacute;', 'Ú': '&Uacute;',
        'ñ': '&ntilde;', 'Ñ': '&Ntilde;', 'ü': '&uuml;', 'Ü': '&Uuml;',
        '«': '&laquo;', '»': '&raquo;', '¿': '&iquest;', '¡': '&iexcl;', 'º': '&ordm;'
    }
    # Reemplazar espacios raros y múltiples espacios
    text = text.replace('\xa0', ' ').replace('  ', ' ')
    for char, entity in chars.items():
        text = text.replace(char, entity)
    return text

def populate():
    data_raw = """1	Azúcar y melaza de caña
2	Arroz
3	Alcohol etílico
4	Recursos hidrobiológicos
5	Maíz amarillo duro
6	Algodón
7	Caña de azúcar
8	Madera
9	Arena y piedra
10	Residuos, subproductos, desechos, recortes, desperdicios
11	Bienes gravados con el IGV, por renuncia a la exoneración
12	Intermediación laboral y tercerización
13	Animales vivos
14	Carnes y despojos comestibles
15	Abonos, cueros y pieles de origen animal
16	Aceite de pescado
17	Harina, polvo y «pellets» de pescado, crustáceos, moluscos y demás invertebrados acuáticos
18	Embarcaciones pesqueras
19	Arrendamiento de bienes
20	Mantenimiento y reparación de bienes muebles
21	Movimiento de carga
22	Otros Servicios Empresariales
23	Leche cruda entera
24	Comisión mercantil
25	Fabricación de bienes por encargo
26	Servicio de transporte de personas
27	Servicio de transporte de carga
28	Transporte de pasajeros
29	Algodón en rama sin desmontar
30	Contratos de Construcción
31	Oro gravado con el IGV
32	Páprika y otros frutos de los géneros capsicum o pimienta
33	Espárragos
34	Minerales metálicos no auríferos
35	Bienes exonerados del IGV
36	Oro y demás minerales metálicos exonerados del IGV
37	Demás servicios gravados con el IGV
38	Espectáculos públicos no deportivos grabados con el IGV
39	Minerales no metálicos
40	Primera venta inmuebles gravada con IGV
41	Plomo
42	Ladrillo de construcción y similares
43	Estructuras metálicas para la construcción
44	Beneficio de minerales metálicos gravados con IGV
45	Minerales de oro y sus concentrados gravados con el IGV
99	Ley 30737"""

    conn = sqlite3.connect('sunat_mappings.db')
    cursor = conn.cursor()
    
    # Limpiamos datos anteriores de tipo 'bien'
    cursor.execute("DELETE FROM mappings WHERE tipo='bien'")
    
    for line in data_raw.split('\n'):
        if not line.strip(): continue
        parts = line.split('\t')
        if len(parts) < 2: continue
        
        codigo = parts[0].strip().zfill(3)
        descripcion_raw = parts[1].strip()
        descripcion_final = f"{codigo} - {normalize_text(descripcion_raw)}"
        
        cursor.execute("INSERT OR REPLACE INTO mappings VALUES (?,?,?)", ('bien', codigo, descripcion_final))
        print(f"Cargado: {codigo} -> {descripcion_final}")
        
    conn.commit()
    conn.close()
    print("\n¡Base de datos poblada y normalizada con éxito!")

if __name__ == "__main__":
    populate()
