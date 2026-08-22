# 🚀 ATS & Job Application Tracking System (PostgreSQL + Streamlit + Gemini AI)

Sistema integral de gestión, seguimiento y evaluación inteligente de postulaciones laborales, diseñado y construido desde cero combinando un motor relacional avanzado en **PostgreSQL**, una interfaz web interactiva en **Streamlit** y automatización cognitiva mediante la **API de Gemini**. 

Este proyecto forma parte de un entorno **End-to-End** enfocado en optimizar la toma de decisiones basada en datos para procesos de selección en tecnología, permitiendo automatizar el filtrado de ofertas, el cálculo de compatibilidad y el análisis cualitativo en segundos.

---

## 🖥️ Interfaz en Ejecución (Streamlit + Gemini)

Así es como luce el panel de control interactivo en tiempo real al procesar una vacante con el método QA80:

![ATS Ingesta](ats%20ingesta.png)

---

## 📐 Base de Datos y Modelo Entidad-Relación (PostgreSQL)

El diseño se estructuró bajo buenas prácticas de bases de datos relacionales en un esquema dedicado (`qa80`), garantizando la integridad de los datos, la automatización y la lógica de negocio a nivel de motor:

* **Diagrama Entidad-Relación (ER):** Estructura relacional completa en pgAdmin que conecta las tablas de candidatos, vacantes, evaluaciones, interacciones y el módulo de migración.
![Diagrama ER](Captura%20de%20pantalla%202026-08-16%20191842.png)

* **Ejecución y Consultas SQL:** Vista en tiempo real de los datos consolidados mediante consultas avanzadas sobre las tablas del esquema.
![Datos y Consultas PostgreSQL](Captura%20de%20pantalla%202026-08-16%20191646.png)

---

## 📊 Características Principales

* **Esquema Dedicado (`qa80`):** Organización limpia y modular independiente del esquema por defecto.
* **Evaluación Automatizada por Ponderación (Vistas Avanzadas):** Cuenta con una vista analítica (`vw_evaluacion_80qa`) que calcula automáticamente un puntaje de compatibilidad para cada vacante usando la siguiente fórmula ponderada:
  * **Tecnologías:** 35%
  * **Experiencia:** 25%
  * **Herramientas Complementarias:** 25%
  * **Nivel de Inglés:** 15%
* **Veredictos Automáticos:** Clasificación dinámica de ofertas mediante estructuras condicionales (`CASE`) para arrojar estados como *"APLICAMOS"*, *"REVISAR excepción"* o *"NO APLICAMOS"*.
* **Restricciones de Integridad (Constraints):** Validaciones estrictas a nivel de esquema para asegurar rangos porcentuales válidos (0 a 100) y coherencia salarial.
* **Triggers y Automatización:** Funciones en PL/pgSQL para el control automático de marcas de tiempo de actualización (`actualizado_en`).
* **Migración de Datos Históricos:** Integración de una tabla ETL (`migracion_excel`) para estructurar y normalizar datos de postulaciones previas.

---

## 🧠 Flujo de Funcionamiento 

1. **Ingreso de la Oferta:** El usuario pega la descripción completa de la vacante en un área de texto interactiva en la interfaz de Streamlit.
2. **Carga del Perfil:** El sistema consulta de manera segura la tabla `qa80.perfil_candidato` en PostgreSQL para obtener el contexto actual del candidato.
3. **Análisis Cognitivo (Gemini):** Se envía un prompt estructurado al modelo `gemini-3.5-flash` aplicando las reglas del **Método QA80** (validación estricta de barreras con *Filter 0*, extracción de metadatos y asignación preliminar de puntajes). El modelo responde estrictamente en formato JSON válido.
4. **Persistencia Transaccional:** La aplicación procesa el JSON recibido y ejecuta inserciones seguras con manejo de transacciones en las tablas `vacante` y `evaluacion_80qa`.
5. **Cálculo Oficial y Renderizado:** Streamlit consulta la vista analítica oficial de PostgreSQL (`vw_evaluacion_80qa`) y muestra dinámicamente:
   * 🛡️ **Estado del Filter 0** (Aprobado / Barrera detectada).
   * 📊 **Métricas Ponderadas** por categoría.
   * 🎯 **Porcentaje QA80 Global y Veredicto Automático**.
   * 📝 **Análisis Cualitativo:** Fortalezas, Brechas y Riesgos en columnas estructuradas.
   * 📌 **Próxima Acción** recomendada para el seguimiento del proceso.

---

## 🛠️ Tecnologías y Herramientas Utilizadas

* **PostgreSQL 13+:** Motor de base de datos relacional.
* **Streamlit:** Desarrollo de la interfaz web interactiva y cliente de visualización.
* **Google GenAI SDK (`google-genai` / `gemini-3.5-flash`):** Motor de inteligencia artificial para tracción y análisis de lenguaje natural.
* **pgAdmin 4:** Herramienta de gestión, diseño de esquemas y generación de diagramas ER.
* **SQL / PL/pgSQL:** Vistas complejas, funciones, triggers y lógica transaccional.
