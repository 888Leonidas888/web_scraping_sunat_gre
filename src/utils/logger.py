import logging

def get_logger(name: str) -> logging.Logger:
    """Configura e inyecta un logger estándar en toda la aplicación."""
    
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - [%(name)s] - %(message)s')
        
        file_handler = logging.FileHandler("detracciones.log", encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
    return logger
