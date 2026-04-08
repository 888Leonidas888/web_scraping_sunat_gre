import logging
from datetime import datetime
from typing import List, Optional
from src.service.sunat_service import get_gre_batch, get_gre_by_ruc_and_serie
from src.service.storage_service import StorageService
from src.models.sunat_filter_model import SunatFilterRequest
from src.models.paginacion_model import SunatGreBatchResponse


def run_massive_query_process(token: str, ruc_receptor: str, emitter_rucs: List[str]):
    """
    Orquesta el proceso de consulta masiva para una lista de RUCs emisores.
    """
    storage_service = StorageService()

    for i in range(1, 31):
        todayStr = datetime.now().replace(day=i).strftime("%Y-%m-%d")

        logging.info(
            f"Iniciando proceso de consulta masiva para la fecha: {todayStr}")
        for ruc_emisor in emitter_rucs:
            try:
                logging.info(
                    f"Consultando GREs para Emisor: {ruc_emisor} -> Receptor: {ruc_receptor}")

                # 1. Preparar filtro
                filter_request = SunatFilterRequest(
                    numRucEmisor=ruc_emisor,
                    numRucReceptor=ruc_receptor,
                    fecEmisionIni=todayStr,
                    fecEmisionFin=todayStr,
                    rangoHoras="1,2,3,4,5,6"
                )

                # 2. Realizar búsqueda masiva
                batch_response: Optional[SunatGreBatchResponse] = get_gre_batch(
                    token, filter_request.model_dump())

                if not batch_response or not batch_response.items:
                    logging.info(
                        f"No se encontraron GREs para el emisor {ruc_emisor} en esta fecha.")
                    continue

                logging.info(
                    f"Se encontraron {len(batch_response.items)} GREs. Procesando detalles...")

                # 3. Procesar cada GRE encontrada
                for item in batch_response.items:
                    try:
                        documento = f"{item.rucEmisor}-{item.codCpe}-{item.numSerie}-{str(item.numCpe).zfill(8)}"
                        logging.info(f"Obteniendo detalle de: {documento}")

                        # Obtener detalle completo si es necesario (el batch trae data básica)
                        gre_detail = get_gre_by_ruc_and_serie(token, documento)

                        if gre_detail:
                            # 4. Enviar al servicio de almacenamiento
                            storage_service.store_gre(gre_detail)
                        else:
                            logging.warning(
                                f"No se pudo obtener el detalle para {documento}")
                    except Exception as ex:
                        logging.error(
                            f"Error procesando la GRE individual {item.numSerie}-{item.numCpe}: {ex}")
            except Exception as e:
                logging.error(f"Error procesando el emisor {ruc_emisor}: {e}")

    logging.info("Proceso de consulta masiva finalizado.")
