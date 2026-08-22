import streamlit as st
import psycopg2
import json
import time
from google import genai


# ============================================================
# CONFIGURACIÓN
# ============================================================

st.set_page_config(
    page_title="ATS Pipeline - Método QA80",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 ATS Pipeline - Método QA80")

st.write(
    "Pega el texto de una vacante. Gemini analizará la oferta, "
    "la comparará contra tu perfil QA80, evaluará el Filter 0, "
    "guardará la evaluación en PostgreSQL y mostrará el resultado final."
)


# ============================================================
# GEMINI
# ============================================================

client = genai.Client(
    api_key=st.secrets["GEMINI_API_KEY"]
)


# ============================================================
# FUNCIONES
# ============================================================

def conectar_db():
    """
    Crea conexión con PostgreSQL.
    """

    return psycopg2.connect(
        dbname="pruebas",
        user="postgres",
        password="admin123",
        host="localhost",
        port="5433"
    )


def obtener_perfil():
    """
    Obtiene el perfil actual del candidato desde PostgreSQL.
    """

    conexion = conectar_db()

    try:

        cursor = conexion.cursor()

        cursor.execute("""
            SELECT
                id,
                nivel_ingles,
                tecnologias,
                herramientas,
                experiencia_resumen
            FROM qa80.perfil_candidato
            ORDER BY id DESC
            LIMIT 1;
        """)

        perfil = cursor.fetchone()

        if not perfil:
            raise Exception(
                "No existe ningún perfil en qa80.perfil_candidato."
            )

        return {
            "id": perfil[0],
            "nivel_ingles": perfil[1],
            "tecnologias": perfil[2],
            "herramientas": perfil[3],
            "experiencia_resumen": perfil[4]
        }

    finally:

        cursor.close()
        conexion.close()


def analizar_vacante(texto_vacante, perfil):
    """
    Gemini analiza la vacante y compara contra el perfil QA80.
    """

    prompt = f"""
Eres el motor de análisis del Método QA80 para selección de vacantes QA.

Debes analizar la oferta laboral y compararla EXCLUSIVAMENTE
contra el perfil del candidato proporcionado.

IMPORTANTE:

1. No inventes información.
2. Si una información no aparece en la oferta, utiliza null
   o un valor conservador.
3. Diferencia entre requisitos OBLIGATORIOS y requisitos DESEABLES.
4. Un requisito deseable NO debe generar Filter 0.
5. Filter 0 solamente debe ser FALSE cuando exista una barrera
   real que impida aplicar según el perfil.
6. Si Filter 0 es FALSE, las cuatro puntuaciones deben ser 0.
7. Las puntuaciones deben estar entre 0 y 100.
8. El resultado final será calculado posteriormente por PostgreSQL.
9. No calcules porcentaje_80qa.
10. No calcules el veredicto final.

============================================================
PERFIL DEL CANDIDATO
============================================================

Nivel de inglés:
{perfil["nivel_ingles"]}

Tecnologías y conocimientos:
{perfil["tecnologias"]}

Herramientas:
{perfil["herramientas"]}

Experiencia / formación:
{perfil["experiencia_resumen"]}

============================================================
OFERTA LABORAL
============================================================

{texto_vacante}

============================================================
REGLAS DEL MÉTODO QA80
============================================================

FILTER 0

Busca barreras obligatorias o excluyentes.

Ejemplos de posibles barreras:

- Inglés obligatorio superior al nivel del candidato.
- Residencia obligatoria en otro país.
- Experiencia obligatoria que el candidato claramente no posee.
- Título profesional obligatorio cuando realmente sea excluyente.
- Una tecnología o certificación declarada explícitamente como
  requisito obligatorio y excluyente que el candidato no posee.
- Modalidad o ubicación imposible para el candidato.
- Cualquier otra condición expresamente obligatoria que haga
  inviable la candidatura.

NO uses Filter 0 para:

- requisitos deseables
- conocimientos "plus"
- tecnologías nice to have
- certificaciones deseables
- experiencia deseable
- herramientas complementarias deseables

============================================================
PUNTUACIONES
============================================================

TECNOLOGÍAS
Evalúa coincidencia entre tecnologías requeridas y las que posee
el candidato.

EXPERIENCIA
Evalúa experiencia requerida frente a experiencia real/práctica
del candidato.

INGLÉS
Compara el nivel requerido explícitamente con el nivel del candidato.

HERRAMIENTAS COMPLEMENTARIAS
Evalúa herramientas, metodologías y conocimientos adicionales
que aporten al cargo.

============================================================
FORMATO DE RESPUESTA
============================================================

Devuelve ÚNICAMENTE JSON válido.

Formato exacto:

{{
    "empresa": "string o null",
    "cargo": "string o null",
    "nivel": "string o null",
    "pais": "string o null",
    "ciudad": "string o null",
    "modalidad": "string o null",
    "url": null,
    "salario_min_cop": null,
    "salario_max_cop": null,
    "moneda": "COP",
    "filtro_0_aprobado": true,
    "motivo_barrera": null,

    "tecnologias": 0,
    "experiencia": 0,
    "ingles": 0,
    "herramientas_complementarias": 0,

    "fortalezas": "string",
    "brechas": "string",
    "riesgos": "string",

    "proxima_accion": "string"
}}

Las puntuaciones deben ser números entre 0 y 100.

Si Filter 0 es FALSE:

"filtro_0_aprobado": false

y obligatoriamente:

"tecnologias": 0,
"experiencia": 0,
"ingles": 0,
"herramientas_complementarias": 0

Además debes explicar la barrera en:

"motivo_barrera"

No agregues texto fuera del JSON.
"""

    reintentos = 3
    response = None

    for intento in range(reintentos):

        try:

            response = client.models.generate_content(
                model="gemini-3.5-flash",
                contents=prompt
            )

            break

        except Exception as error:

            if (
                "503" in str(error)
                and intento < reintentos - 1
            ):

                time.sleep(2)

            else:

                raise error

    if response is None:
        raise Exception("Gemini no devolvió respuesta.")

    texto = response.text.strip()

    # Limpiar posibles bloques Markdown
    texto = texto.replace("```json", "")
    texto = texto.replace("```", "")
    texto = texto.strip()

    return json.loads(texto)


def guardar_vacante_y_evaluacion(datos, texto_vacante):
    """
    Guarda la vacante y su evaluación QA80.
    """

    conexion = conectar_db()

    try:

        cursor = conexion.cursor()

        # ----------------------------------------------------
        # 1. INSERTAR VACANTE
        # ----------------------------------------------------

        sql_vacante = """
            INSERT INTO qa80.vacante (
                fecha_registro,
                empresa,
                cargo,
                nivel,
                pais,
                ciudad,
                modalidad,
                url,
                salario_min_cop,
                salario_max_cop,
                moneda,
                filtro_0_aprobado,
                motivo_barrera,
                estado_analisis,
                proxima_accion,
                notas,
                descripcion,
                creado_en,
                actualizado_en
            )
            VALUES (
                CURRENT_DATE,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                'Analizada',
                %s,
                %s,
                %s,
                CURRENT_TIMESTAMP,
                CURRENT_TIMESTAMP
            )
            RETURNING id;
        """
        pais = datos.get("pais") or "Sin dato"
        ciudad = datos.get("ciudad") or "Sin dato"
        modalidad = datos.get("modalidad") or "Sin dato"


        cursor.execute(
            sql_vacante,
            (
                datos.get("empresa"),
                datos.get("cargo"),
                datos.get("nivel"),
                pais,
                ciudad,
                modalidad,
                datos.get("url"),
                datos.get("salario_min_cop"),
                datos.get("salario_max_cop"),
                datos.get("moneda") or "COP",
                datos.get("filtro_0_aprobado"),
                datos.get("motivo_barrera"),
                datos.get("proxima_accion"),
                (
                    f"Fortalezas: {datos.get('fortalezas')}\n"
                    f"Brechas: {datos.get('brechas')}\n"
                    f"Riesgos: {datos.get('riesgos')}"
                ),
                texto_vacante
            )
        )

        vacante_id = cursor.fetchone()[0]

        # ----------------------------------------------------
        # 2. INSERTAR EVALUACIÓN QA80
        # ----------------------------------------------------

        sql_evaluacion = """
            INSERT INTO qa80.evaluacion_80qa (
                vacante_id,
                tecnologias,
                experiencia,
                ingles,
                herramientas_complementarias,
                fortalezas,
                brechas,
                riesgos,
                evaluado_en
            )
            VALUES (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                CURRENT_TIMESTAMP
            )
            RETURNING id;
        """

        cursor.execute(
            sql_evaluacion,
            (
                vacante_id,
                datos.get("tecnologias", 0),
                datos.get("experiencia", 0),
                datos.get("ingles", 0),
                datos.get("herramientas_complementarias", 0),
                datos.get("fortalezas"),
                datos.get("brechas"),
                datos.get("riesgos")
            )
        )

        evaluacion_id = cursor.fetchone()[0]

        conexion.commit()

        return vacante_id, evaluacion_id

    except Exception:

        conexion.rollback()
        raise

    finally:

        cursor.close()
        conexion.close()


def obtener_resultado_qa80(vacante_id):
    """
    Obtiene el resultado final desde la vista oficial QA80.
    """

    conexion = conectar_db()

    try:

        cursor = conexion.cursor()

        cursor.execute("""
            SELECT
                vacante_id,
                empresa,
                cargo,
                pais,
                ciudad,
                modalidad,
                filtro_0_aprobado,
                motivo_barrera,
                tecnologias,
                experiencia,
                ingles,
                herramientas_complementarias,
                porcentaje_80qa,
                veredicto,
                salario_min_cop,
                salario_max_cop,
                umbral_cop,
                compatibilidad_salarial,
                prioridad,
                proxima_accion,
                proxima_fecha,
                fortalezas,
                brechas,
                riesgos
            FROM qa80.vw_evaluacion_80qa
            WHERE vacante_id = %s;
        """, (vacante_id,))

        resultado = cursor.fetchone()

        if not resultado:
            raise Exception(
                "No se encontró la evaluación en vw_evaluacion_80qa."
            )

        columnas = [
            "vacante_id",
            "empresa",
            "cargo",
            "pais",
            "ciudad",
            "modalidad",
            "filtro_0_aprobado",
            "motivo_barrera",
            "tecnologias",
            "experiencia",
            "ingles",
            "herramientas_complementarias",
            "porcentaje_80qa",
            "veredicto",
            "salario_min_cop",
            "salario_max_cop",
            "umbral_cop",
            "compatibilidad_salarial",
            "prioridad",
            "proxima_accion",
            "proxima_fecha",
            "fortalezas",
            "brechas",
            "riesgos"
        ]

        return dict(zip(columnas, resultado))

    finally:

        cursor.close()
        conexion.close()


# ============================================================
# INTERFAZ
# ============================================================

texto_vacante = st.text_area(
    "📄 Pega aquí la descripción completa de la vacante:",
    height=350,
    placeholder="Pega aquí la oferta laboral..."
)


# ============================================================
# BOTÓN PRINCIPAL
# ============================================================

if st.button(
    "🤖 Analizar vacante con Método QA80",
    type="primary"
):

    if not texto_vacante.strip():

        st.warning(
            "⚠️ Primero debes pegar la descripción de la vacante."
        )

        st.stop()

    try:

        # ----------------------------------------------------
        # PASO 1 - PERFIL
        # ----------------------------------------------------

        with st.spinner(
            "👤 Cargando perfil QA80..."
        ):

            perfil = obtener_perfil()

        # ----------------------------------------------------
        # PASO 2 - GEMINI
        # ----------------------------------------------------

        with st.spinner(
            "🔎 Gemini está analizando y evaluando la vacante..."
        ):

            datos = analizar_vacante(
                texto_vacante,
                perfil
            )

        st.success(
            "✅ Análisis de Gemini completado."
        )

        # ----------------------------------------------------
        # DATOS EXTRAÍDOS
        # ----------------------------------------------------

        st.subheader(
            "📋 Información detectada"
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            st.write(
                "**Empresa:**",
                datos.get("empresa") or "Sin dato"
            )

            st.write(
                "**Cargo:**",
                datos.get("cargo") or "Sin dato"
            )

        with col2:

            st.write(
                "**Modalidad:**",
                datos.get("modalidad") or "Sin dato"
            )

            st.write(
                "**Ciudad:**",
                datos.get("ciudad") or "Sin dato"
            )

        with col3:

            st.write(
                "**País:**",
                datos.get("pais") or "Sin dato"
            )

            st.write(
                "**Nivel:**",
                datos.get("nivel") or "Sin dato"
            )

        # ----------------------------------------------------
        # FILTER 0 PREVIO
        # ----------------------------------------------------

        st.subheader(
            "🛡️ Filter 0"
        )

        if datos.get("filtro_0_aprobado"):

            st.success(
                "✅ FILTER 0 APROBADO"
            )

        else:

            st.error(
                "❌ FILTER 0 NO APROBADO"
            )

            st.warning(
                f"Motivo: {datos.get('motivo_barrera') or 'No especificado'}"
            )

        # ----------------------------------------------------
        # GUARDAR EN BASE DE DATOS
        # ----------------------------------------------------

        with st.spinner(
            "🗄️ Guardando vacante y evaluación QA80..."
        ):

            vacante_id, evaluacion_id = (
                guardar_vacante_y_evaluacion(
                    datos,
                    texto_vacante
                )
            )

        st.success(
            "✅ Vacante y evaluación guardadas correctamente."
        )

        # ----------------------------------------------------
        # CONSULTAR VISTA OFICIAL
        # ----------------------------------------------------

        with st.spinner(
            "🧮 Calculando resultado final del Método QA80..."
        ):

            resultado = obtener_resultado_qa80(
                vacante_id
            )

        # ----------------------------------------------------
        # RESULTADO FINAL
        # ----------------------------------------------------

        st.divider()

        st.subheader(
            "🧮 Resultado Método QA80"
        )

        # Filter 0
        if resultado["filtro_0_aprobado"]:

            st.success(
                "🟢 Filter 0: APROBADO"
            )

        else:

            st.error(
                "🔴 Filter 0: NO APROBADO"
            )

            if resultado["motivo_barrera"]:

                st.warning(
                    f"**Barrera:** {resultado['motivo_barrera']}"
                )

        # ----------------------------------------------------
        # PUNTAJES
        # ----------------------------------------------------

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.metric(
                "Tecnologías",
                f"{resultado['tecnologias']:.2f}%"
            )

        with col2:

            st.metric(
                "Experiencia",
                f"{resultado['experiencia']:.2f}%"
            )

        with col3:

            st.metric(
                "Inglés",
                f"{resultado['ingles']:.2f}%"
            )

        with col4:

            st.metric(
                "Complementarias",
                f"{resultado['herramientas_complementarias']:.2f}%"
            )

        # ----------------------------------------------------
        # RESULTADO QA80
        # ----------------------------------------------------

        st.divider()

        porcentaje = resultado["porcentaje_80qa"]

        if porcentaje is None:

            porcentaje = 0

        st.metric(
            "🎯 PORCENTAJE QA80",
            f"{porcentaje:.2f}%"
        )

        veredicto = resultado["veredicto"]

        if veredicto.startswith(
            "APLICAMOS · prioritaria"
        ):

            st.success(
                f"🚀 {veredicto}"
            )

        elif veredicto.startswith(
            "APLICAMOS"
        ):

            st.success(
                f"🟢 {veredicto}"
            )

        elif veredicto.startswith(
            "REVISAR"
        ):

            st.warning(
                f"🟡 {veredicto}"
            )

        else:

            st.error(
                f"🔴 {veredicto}"
            )

        # ----------------------------------------------------
        # INFORMACIÓN ADICIONAL
        # ----------------------------------------------------

        st.divider()

        col1, col2, col3 = st.columns(3)

        with col1:

            st.write(
                "**Prioridad:**",
                resultado["prioridad"]
            )

        with col2:

            st.write(
                "**Compatibilidad salarial:**",
                resultado["compatibilidad_salarial"]
            )

        with col3:

            st.write(
                "**Vacante ID:**",
                resultado["vacante_id"]
            )

        # ----------------------------------------------------
        # ANÁLISIS CUALITATIVO
        # ----------------------------------------------------

        st.divider()

        st.subheader(
            "📝 Análisis cualitativo"
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            st.markdown("### 💪 Fortalezas")

            st.write(
                resultado["fortalezas"] or "Sin información"
            )

        with col2:

            st.markdown("### 📉 Brechas")

            st.write(
                resultado["brechas"] or "Sin información"
            )

        with col3:

            st.markdown("### ⚠️ Riesgos")

            st.write(
                resultado["riesgos"] or "Sin información"
            )

        # ----------------------------------------------------
        # PRÓXIMA ACCIÓN
        # ----------------------------------------------------

        st.divider()

        st.info(
            f"📌 **Próxima acción:** "
            f"{resultado['proxima_accion'] or 'Sin definir'}"
        )

        # ----------------------------------------------------
        # IDS INTERNOS
        # ----------------------------------------------------

        with st.expander(
            "🔧 Información técnica"
        ):

            st.write(
                f"ID Vacante: {vacante_id}"
            )

            st.write(
                f"ID Evaluación: {evaluacion_id}"
            )

            st.write(
                "Fuente del resultado: "
                "qa80.vw_evaluacion_80qa"
            )

    # ========================================================
    # ERRORES
    # ========================================================

    except json.JSONDecodeError:

        st.error(
            "❌ Gemini no devolvió un JSON válido."
        )

        st.write(
            "Respuesta recibida:"
        )

        if "response" in locals() and response:

            st.code(
                response.text
            )

    except psycopg2.Error as error:

        st.error(
            "❌ Error de PostgreSQL."
        )

        st.code(
            str(error)
        )

    except Exception as error:

        st.error(
            "❌ Ocurrió un error durante el proceso."
        )

        st.code(
            str(error)
        )