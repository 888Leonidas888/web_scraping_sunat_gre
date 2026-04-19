import os
import time
import random
from typing import Dict, Any, List, Optional
from datetime import datetime

from pydantic import ValidationError
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn
from rich.panel import Panel
from rich.text import Text

from src.models.pago_model import PagoDetraccion
from src.core.db_repository import get_mapping, update_mappings_from_html
from src.core.sunat_api import download_constancia_api
from src.scraping.sunat_scraper import save_html_as_pdf
from src.utils.helpers import clean_filename
from src.utils.logger import get_logger

logger = get_logger("Detracciones_Service")
console = Console()

# Base HTML robusta para el Fallback
CONSTANCIA_TEMPLATE = """
<html>
<head>
    <meta charset="UTF-8">
    <title>Constancia de Dep&oacute;sito</title>
    <style type="text/css">
        BODY {{ FONT-SIZE: 10px; MARGIN: 5px; COLOR: #000; FONT-FAMILY: verdana, arial, helvetica, sans-serif; BACKGROUND-COLOR: #ffffff }}
        TABLE {{ FONT-SIZE: 10px; PADDING: 0px; MARGIN: 0px; border: 0; }}
        .bgn {{ background-color: #FFF; FONT-WEIGHT: 900; }}
        .form-table {{ border: 1px solid #4682B4; }}
    </style>
</head>
<body>
    <table width="90%" cellpadding="3" cellspacing="3" align="center" class="form-table">
        <tr class="bgn" align="center"><td>CONSTANCIA DE DEPOSITO</td></tr>
        <tr class="bgn" align="center"><td>SISTEMA DE PAGO DE OBLIGACIONES TRIBUTARIAS D.LEG. 940</td></tr>
    </table>
    <br>
    <table cellpadding="3" cellspacing="2" width="90%" class="form-table" align="center">
        <tr class="bgn"><td>N&uacute;mero de constancia</td><td>{num_constancia}</td></tr>
        <tr><td>Usuario SOL</td><td>{cod_usuario_sol}</td></tr>
        <tr><td>N&deg; Cuenta de detracciones (Banco de la Naci&oacute;n)</td><td>{num_cuenta}</td></tr>
        <tr><td>Tipo de Cuenta:</td><td>Cuenta de Detracciones Convencional</td></tr>
        <tr><td>RUC del Proveedor</td><td>{num_ruc_proveedor}</td></tr>
        <tr><td>Nombre/Raz&oacute;n Social del Proveedor</td><td>{des_prov}</td></tr>
        <tr><td>Tipo de Documento del Adquiriente</td><td>{tip_doc_adq_desc}</td></tr>
        <tr><td>N&uacute;mero de Documento del Adquiriente</td><td>{num_doc_adq}</td></tr>
        <tr><td>Nombre/Raz&oacute;n Social del Adquiriente</td><td>{des_adq}</td></tr>
        <tr><td>Tipo de operaci&oacute;n</td><td>{tip_operacion_desc}</td></tr>
        <tr><td>Bien &oacute; servicio</td><td>{tip_bien_desc}</td></tr>
        <tr><td>Monto del dep&oacute;sito</td><td>S/ {mto_deposito}</td></tr>
        <tr><td>Fecha y hora de pago</td><td>{fec_pago_legible}</td></tr>
        <tr><td>Periodo Tributario</td><td>{per_tributario}</td></tr>
        <tr><td>Tipo de Comprobante</td><td>{cod_tip_comp_desc}</td></tr>
        <tr><td>N&uacute;mero de Comprobante</td><td>{serie_correlativo}</td></tr>
        <tr><td>N&uacute;mero de operaci&oacute;n</td><td>{num_pres}</td></tr>
    </table>
</body>
</html>
"""

def reconstruct_constancia_html(pago: PagoDetraccion) -> Optional[str]:
    """
    MODO TANQUE: Utiliza la data validada por el Pydantic Model (pago)
    y la base de SQLite para cruzar códigos ausentes en el JSON y generar HTML válido.
    """
    try:
        # Convertir tiempo EPOCH a legible
        fec_pago_legible = ""
        if pago.fec_pago > 0:
            dt = datetime.fromtimestamp(pago.fec_pago / 1000)
            fec_pago_legible = dt.strftime("%d/%m/%Y %I:%M:%S %p")
            
        # SQLite Lookups: Mapeos dinámicos
        tip_doc_adq_desc = get_mapping('documento', pago.tip_doc_adq)
        tip_op_desc = get_mapping('operacion', pago.tip_operacion)
        tip_bien_desc = get_mapping('bien', pago.tip_bien)
        tip_comp_desc = get_mapping('comprobante', pago.cod_tipcomprobante)

        serie_corr = f"{pago.num_serie} {pago.num_comprobante}".strip()

        html_out = CONSTANCIA_TEMPLATE.format(
            num_constancia=pago.num_constancia,
            cod_usuario_sol=pago.cod_usuario_sol,
            num_cuenta=pago.num_cuenta,
            num_ruc_proveedor=pago.num_ruc_proveedor,
            des_prov=pago.des_prov,
            tip_doc_adq_desc=tip_doc_adq_desc,
            num_doc_adq=pago.num_doc_adq,
            des_adq=pago.des_adq,
            tip_operacion_desc=tip_op_desc,
            tip_bien_desc=tip_bien_desc,
            mto_deposito=f"{pago.mto_deposito:,.2f}",
            fec_pago_legible=fec_pago_legible,
            per_tributario=pago.per_tributario,
            cod_tip_comp_desc=tip_comp_desc,
            serie_correlativo=serie_corr,
            num_pres=pago.num_pres
        )
        return html_out
    except Exception as e:
        logger.error(f"Falla crítica en Modo Tanque al reconstruir HTML: {e}")
        return None

def process_massive_downloads(headless_driver, token: str, api_response: Dict[str, Any], month_path: str, filtro_excel: set = None) -> None:
    """
    Iterador central BPA que procesa cada pago:
    1. Descarga Constancia Oficial (si falla -> Modo Tanque).
    2. Convierte a PDF en disco.
    3. Muestra progreso Rich UI.
    """
    raw_pagos = api_response.get('resultado', [])
    if not raw_pagos:
        console.print("[yellow]0 pagos retornados para este mes.[/yellow]")
        return

    # Validar a través de Pydantic
    pagos_model_list: List[PagoDetraccion] = []
    for rp in raw_pagos:
        try:
            if rp.get('num_constancia'):
                pagos_model_list.append(PagoDetraccion(**rp))
        except ValidationError as e:
            logger.warning(f"Pago inválido ignorado: {e}")

    failed_constancias = []
    success_count = 0
    reconstructed_count = 0

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=None, pulse_style="bright_blue"),
        TaskProgressColumn(),
        TimeRemainingColumn(),
        console=console,
        transient=False
    ) as progress:
        
        task = progress.add_task("[cyan]Procesando documentos...", total=len(pagos_model_list))

        for pago in pagos_model_list:
            
            # FILTRO POR EXCEL: Saltamos si no está en la lista blanca de requerimientos
            if filtro_excel:
                if (pago.num_ruc_proveedor, pago.num_constancia) not in filtro_excel:
                    continue

            provider_folder = f"{pago.num_ruc_proveedor} - {clean_filename(pago.des_prov)}"
            provider_path = os.path.join(month_path, provider_folder)
            os.makedirs(provider_path, exist_ok=True)
            
            pdf_filename = os.path.join(provider_path, f"{pago.num_constancia}.pdf")
            
            # Paso 1: Intentar API Constancia
            html_content = download_constancia_api(token, pago.num_constancia)
            
            if html_content:
                 is_reconstructed = False
                 # APRENDIZAJE ACTIVO: SUNAT entregó el HTML, extraemos catálogos si hay
                 update_mappings_from_html(html_content)
            else:
                 # FALLBACK: Modo Tanque (Híbrido - BPA)
                 logger.debug(f"Activando Modo Tanque para {pago.num_constancia}")
                 html_content = reconstruct_constancia_html(pago)
                 is_reconstructed = True
            
            # Paso 2: Imprimir HTML a PDF Localmente
            if html_content:
                if save_html_as_pdf(headless_driver, html_content, pdf_filename):
                    status_text = "[bold yellow]MODO_TANQUE[/bold yellow]" if is_reconstructed else "[bold green]SUNAT_ORIG[/bold green]"
                    progress.console.print(f" {status_text} | {pago.num_ruc_proveedor} | {pago.num_constancia}.pdf")
                    success_count += 1
                    if is_reconstructed: 
                        reconstructed_count += 1
                else:
                    failed_constancias.append(pago.num_constancia)
            else:
                failed_constancias.append(pago.num_constancia)
            
            progress.update(task, advance=1)
            # Evitar sobrecargar el microservicio de headless Chrome
            time.sleep(random.uniform(0.3, 0.8))

    # Resumen Dashboard Console
    summary = Text()
    summary.append("\n\n═ RESUMEN DE EJECUCIÓN (MES) ═\n", style="bold cyan")
    summary.append(f"TOTAL: {len(pagos_model_list)}\n", style="white")
    summary.append(f"EXITO: {success_count}\n", style="bold green")
    summary.append(f"  └─ SUNAT Oficial: {success_count - reconstructed_count}\n", style="green")
    summary.append(f"  └─ Rescatados (Tanque): {reconstructed_count}\n", style="yellow")
    if failed_constancias:
        summary.append(f"FALLIDOS: {len(failed_constancias)} {failed_constancias}\n", style="bold red")

    console.print(Panel(summary, border_style="bright_blue"))
    logger.info(f"Mes completado: {success_count}/{len(pagos_model_list)} archivos.")
