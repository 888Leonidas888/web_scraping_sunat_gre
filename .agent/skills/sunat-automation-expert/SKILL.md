---
name: sunat-automation-expert
description: Especialista en automatización RPA/BPA del portal SOL de SUNAT, evasión web y rescate de data vía APIs.
---

# 🚀 Skill: Sunat Automation Expert (Actualizado: Híbrido RPA/BPA)

Este módulo de conocimiento rige las automatizaciones para SUNAT (Perú), enfocándose tanto en la evasión de CAPTCHAs como en el consumo interno de APIs (Idcache) y mecanismos de redención (Fallback).

## 🎯 Capacidades Principales
- Captura de **Tokens Internos (Idcache)** esnifando la red para habilitar llamadas BPA masivas.
- Implementación del **"Modo Tanque"**: Conversión de JSONs en comprobantes PDF cuando el portal web revienta con Error 500.
- Bases de Datos de Conocimiento (SQLite) que aprenden en caliente atributos tributarios (códigos de Bienes, Servicios y Tipo de Operación).
- Patrones de navegación Headless para evitar detección.

## 🛠️ Guía de Implementación Logística

### 1. Interceptación de Tráfico (Idcache)
En lugar de procesar HTML y clics lentos, el objetivo primario del RPA es obtener el token.
1. Utiliza `selenium-wire` en lugar del Selenium estándar.
2. Escanea `driver.requests` apenas se dispare una consulta interna.
3. Extrae el header `Idcache` y cierra el navegador de ser posible para liberar RAM. 

### 2. Evasión de Bloqueos (Human-Like Behavior)
Para las partes visuales previas a la API:
- Usa `human_like_type` (con delays de `0.05-0.15s`) para ingresar el RUC y Clave SOL.
- Pausas aleatorias prolongadas (`time.sleep(random.uniform(5, 10))`) entre consultas masivas (mes a mes) para no activar las alarmas WAF de SUNAT.

### 3. Redundancia BPA "Modo Tanque" (Rescate de Datos)
SUNAT es inestable y seguido retorna Error 500 al pedir un PDF. Si falla:
1. Extrae los datos desde el payload JSON y construye un documento HTML local usando una plantilla HTML base.
2. Debido a que el JSON omite las descripciones a favor de códigos (`'037'`, `'01'`), apóyate en `sqlite3` para traducir el código a su texto correspondiente.
3. Alimenta la base SQLite cuando la descarga original de un HTML sí resulte exitosa (Aprendizaje dinámico).
4. Usa el motor interno de CDP en Chrome (`Page.printToPDF`) para transformar tu HTML en un PDF nativo local.

## 📋 Checklist de Errores Comunes
- [ ] **Timeout:** Aumenta los timeouts a 20-30s en login.
- [ ] **Data faltante en JSON (Modo Tanque):** Validar contra base local (sqlite) siempre y usar placeholders como `"PROVEEDOR_DESCONOCIDO"` y en los nombres de archivo sanitizarlos para evitar caracteres inválidos (`\`, `/`, `:`).
- [ ] **Recursos Colgados:** Asegúrate de ejecutar `driver.quit()` siempre en los bloques `finally`.
