---
name: sunat-automation-expert
description: Especialista en la automatización del portal SOL de SUNAT y manejo avanzado de Selenium.
---

# 🚀 Skill: Sunat Automation Expert

Este módulo de conocimiento especializado está diseñado para optimizar el desarrollo y mantenimiento de scripts de automatización para SUNAT (Perú), enfocándose en la robustez y la evasión de bloqueos.

## 🎯 Capacidades Principales
- Manejo avanzado de **IFRAMES** anidados en el portal SOL.
- Estrategias de **esperas inteligentes** (Explicit Waits) para cargando/spinners de SUNAT.
- Patrones de navegación para evitar la detección de bots.
- Extracción segura de datos desde tablas dinámicas y elementos AJAX.

## 🛠️ Guía de Implementación Logística

### 1. Gestión de Ventanas y Contextos
SUNAT suele abrir nuevas ventanas o usar frames pesados. Sigue siempre este orden:
1. Validar si el elemento está dentro de un `iframe`.
2. Usar `driver.switch_to.frame()` antes de interactuar.
3. Volver siempre al contexto principal con `driver.switch_to.default_content()`.

### 2. Evasión de Bloqueos (Human-Like Behavior)
Para evitar el error "Service Unavailable" o retos de seguridad:
- **Movimientos de mouse:** No vayas directo al elemento, usa acciones intermedias.
- **Tipeo humano:** Usa la función `human_like_type` (disponible en `utils`) con retrasos de `random.uniform(0.05, 0.15)`.
- **Análisis de RED:** Usa `selenium-wire` para capturar respuestas JSON/XML directamente de las peticiones XHR, lo que es más rápido que el scraping visual.

### 3. Selectores Robustos
Evita XPaths absolutos. Usa patrones de texto:
- Botón Consultar: `//button[contains(text(), 'Consultar')]`
- Inputs de RUC: `//input[@id='txtRuc']` o `//input[contains(@title, 'RUC')]`

## 📋 Checklist de Errores Comunes
- [ ] **Timeout:** SUNAT es lento. Aumenta los timeouts a 20-30 segundos en horas pico.
- [ ] **Sesión Expirada:** Implementar detector de redirección al login.
- [ ] **Spinners:** Esperar a que el overlay de carga desaparezca antes de Click.

## 📂 Recursos Relacionados
- `src/core/`: Implementaciones de referencia.
- `.agent/rules/GEMINI.md`: Estándares de código.
