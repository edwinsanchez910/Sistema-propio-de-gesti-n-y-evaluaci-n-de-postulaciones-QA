# 🚀 ATS & Job Application Tracking System (PostgreSQL)

Sistema relacional de gestión, seguimiento y evaluación inteligente de postulaciones laborales, diseñado y construido desde cero en **PostgreSQL**. Este proyecto forma parte de un entorno End-to-End enfocado en optimizar la toma de decisiones basada en datos para procesos de selección en tecnología.

---

## 📐 Modelo Entidad-Relación (ER)

El diseño se estructuró bajo buenas prácticas de bases de datos relacionales, garantizando la integridad de los datos, la automatización y la lógica de negocio a nivel de motor:

![Modelo Entidad-Relación de la Base de Datos](Captura%20de%20pantalla%202026-08-16%20191842.png)
*(Esquema relacional en pgAdmin mostrando las tablas `perfil_candidato`, `vacante`, `evaluacion_80qa`, `postulacion`, `interaccion` y `migracion_excel`)*

---

## 📊 Características Principales

* **Esquema Dedicado (`qa80`):** Organización limpia y modular independiente del esquema por defecto.
* **Evaluación Automatizada por Ponderación (Vistas Avanzadas):** Cuenta con una vista analítica (`vw_evaluacion_80qa`) que calcula automáticamente un puntaje de compatibilidad para cada vacante usando la siguiente fórmula ponderada:
  * **Tecnologías:** 35%
  * **Experiencia:** 25%
  * **Herramientas Complementarias:** 25%
  * **Nivel de Inglés:** 15%
* **Veredictos Automáticos:** Clasificación dinámica de ofertas mediante estructuras condicionales (`CASE`) para arrojar estados como *"APLICAMOS"*, *"REVISAR excepción"* o *"NO APLICAMOS"*.
* **Restricciones de Integridad (`Constraints`):** Validaciones estrictas a nivel de esquema para asegurar rangos porcentuales válidos ($0$ a $100$) y coherencia salarial.
* **Triggers y Automatización:** Funciones en `PL/pgSQL` para el control automático de marcas de tiempo de actualización (`actualizado_en`).
* **Migración de Datos Históricos:** Integración de una tabla ETL (`migracion_excel`) para estructurar y normalizar datos de postulaciones previas.

---

## 💻 Ejemplo de Consulta y Datos en Ejecución

Aquí se muestra una consulta relacional uniendo la tabla de vacantes con las postulaciones reales gestionadas por el sistema:

![Ejecución de consulta SQL en pgAdmin](Captura%20de%20pantalla%202026-08-16%20191646.png)

---

## 🛠️ Tecnologías y Herramientas Utilizadas
* **PostgreSQL 13+**: Motor de base de datos relacional.
* **pgAdmin 4**: Herramienta de gestión, diseño de esquemas y generación de diagramas ER.
* **SQL / PL/pgSQL**: Vistas complejas, funciones y triggers.
