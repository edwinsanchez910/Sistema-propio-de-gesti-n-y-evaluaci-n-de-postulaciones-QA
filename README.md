# 🚀 ATS & Job Application Tracking System (PostgreSQL + Streamlit + Gemini AI)

Sistema integral de gestión, seguimiento y evaluación inteligente de postulaciones laborales, diseñado y construido desde cero combinando un motor relacional avanzado en **PostgreSQL**, una interfaz web interactiva en **Streamlit** y automatización cognitiva mediante la **API de Gemini**. 

Este proyecto forma parte de un entorno **End-to-End** enfocado en optimizar la toma de decisiones basada en datos para procesos de selección en tecnología, permitiendo automatizar el filtrado de ofertas, el cálculo de compatibilidad y el análisis cualitativo en segundos.

---

## 📐 Modelo Entidad-Relación (ER)

El diseño se estructuró bajo buenas prácticas de bases de datos relacionales, garantizando la integridad de los datos, la automatización y la lógica de negocio a nivel de motor:
* **`qa80.perfil_candidato`**: Almacena las competencias base del candidato (tecnologías, herramientas, nivel de inglés y resumen de experiencia).
* **`qa80.vacante`**: Contiene la información detallada de cada oferta laboral extraída y registrada.
* **`qa80.evaluacion_80qa`**: Almacena las puntuaciones técnicas cualitativas y cuantitativas emitidas tras la evaluación.
* **Vistas avanzadas (`qa80.vw_evaluacion_80qa`)**: Ejecutan la lógica de negocio central (cálculo ponderado, veredictos automáticos y compatibilidad salarial) directamente en la base de datos.
*(Esquema relacional en pgAdmin mostrando las tablas perfil_candidato, vacante, evaluacion_80qa, postulacion, interaccion y migracion_excel)*

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

## 🧠 Flujo de Funcionamiento (Streamlit + Gemini AI)

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
