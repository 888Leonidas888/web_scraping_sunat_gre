---
name: clean-architecture-python
description: Especialista en Arquitectura Limpia aplicada a Python, modelos Pydantic y tipado estático (Type Hints).
---

# 🏗️ Skill: Clean Architecture Python

Esta skill se enfoca en mantener el código backend bajo los más altos estándares de calidad, mantenibilidad y escalabilidad, siguiendo los principios de S.O.L.I.D. y Clean Architecture.

## 🎯 Capacidades Principales
- Diseño de **modelos de datos** robustos con `Pydantic`.
- Implementación de **Type Hints** obligatorios para validación estática.
- Separación de responsabilidades: Core (Scraping), Business Logic, y Utils.
- Refactorización de código repetido (DRY).

## 🛠️ Estándares Técnicos

### 1. Modelado con Pydantic
Usa siempre modelos para representar los datos extraídos de SUNAT. Esto permite validación automática y autocompletado.
```python
from pydantic import BaseModel, Field

class GREModel(BaseModel):
    ruc_emisor: str = Field(..., pattern=r'^\d{11}$')
    serie: str
    numero: int
```

### 2. Capas de la Aplicación
- **`src/scraping/`**: Contiene la lógica técnica de Selenium y navegación.
- **`src/service/`**: Orquestación de la lógica de negocio y llamadas a scraping.
- **`src/models/`**: Definición de esquemas de datos con Pydantic.
- **`src/utils/`**: Funciones de apoyo que no dependen del estado global.

### 3. Tipado (Type Hints)
No se permiten funciones sin tipos.
- Correcto: `def get_data(ruc: str) -> dict:`
- Incorrecto: `def get_data(ruc):`

## 📋 Directrices de Revisión
- [ ] ¿La función tiene Type Hints?
- [ ] ¿Se utiliza un modelo de `src/models/` para los retornos de datos?
- [ ] ¿Los logs usan el módulo `logging` estándar?

## 📂 Referencias
- `src/utils/`: Utilidades compartidas.
- `src/models/`: Modelos de datos.
- `.env`: Configuración de variables de entorno.
