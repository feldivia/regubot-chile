"""Seed de datos demo: artículos clave de regulación financiera chilena.

Sin scraping. Textos reales de leyes chilenas para una demo funcional.
"""

import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import settings  # noqa: E402
from app.db.session import async_session, engine  # noqa: E402
from app.ingestion.chunker import chunkear_articulo  # noqa: E402
from app.ingestion.parser import ArticuloParsed  # noqa: E402
from app.models import Articulo, Chunk, Norma  # noqa: E402
from app.models.base import Base  # noqa: E402
from app.utils.embeddings import generar_embeddings  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

# ============================================================
# Datos de semilla: artículos representativos
# ============================================================

NORMAS_SEED = [
    {
        "tipo": "ley",
        "numero": "19496",
        "titulo": "Ley de Protección de los Derechos de los Consumidores",
        "organismo": "Congreso Nacional",
        "url_oficial": "https://www.bcn.cl/leychile/navegar?idNorma=61438",
        "articulos": [
            {
                "numero": "1",
                "path": "Título I > Art. 1",
                "texto": (
                    "Artículo 1°.- La presente ley tiene por objeto normar las relaciones entre "
                    "proveedores y consumidores, establecer las infracciones en perjuicio del consumidor "
                    "y señalar el procedimiento aplicable en estas materias. Para los efectos de esta ley "
                    "se entenderá por: 1.- Consumidores o usuarios: las personas naturales o jurídicas que, "
                    "en virtud de cualquier acto jurídico oneroso, adquieren, utilizan, o disfrutan, como "
                    "destinatarios finales, bienes o servicios. 2.- Proveedores: las personas naturales o "
                    "jurídicas, de carácter público o privado, que habitualmente desarrollen actividades de "
                    "producción, fabricación, importación, construcción, distribución o comercialización de "
                    "bienes o de prestación de servicios a consumidores, por las que se cobre precio o tarifa."
                ),
            },
            {
                "numero": "3",
                "path": "Título I > Art. 3",
                "texto": (
                    "Artículo 3°.- Son derechos y deberes básicos del consumidor: a) La libre elección del "
                    "bien o servicio. El silencio no constituye aceptación en los actos de consumo; b) El "
                    "derecho a una información veraz y oportuna sobre los bienes y servicios ofrecidos, su "
                    "precio, condiciones de contratación y otras características relevantes de los mismos, "
                    "y el deber de informarse responsablemente de ellos; c) El no ser discriminado "
                    "arbitrariamente por parte de proveedores de bienes y servicios; d) La seguridad en el "
                    "consumo de bienes y servicios, la protección de la salud y el medio ambiente y el deber "
                    "de evitar los riesgos que puedan afectarles; e) El derecho a la reparación e "
                    "indemnización adecuada y oportuna de todos los daños materiales y morales en caso de "
                    "incumplimiento de cualquiera de las obligaciones contraídas por el proveedor, y el deber "
                    "de accionar de acuerdo a los medios que la ley le franquea; f) La educación para un "
                    "consumo responsable, y el deber de celebrar operaciones de consumo con el comercio "
                    "establecido."
                ),
            },
            {
                "numero": "12",
                "path": "Título III > Párrafo 1° > Art. 12",
                "texto": (
                    "Artículo 12.- Todo proveedor de bienes o servicios estará obligado a respetar los "
                    "términos, condiciones y modalidades conforme a las cuales se hubiere ofrecido o "
                    "convenido con el consumidor la entrega del bien o la prestación del servicio."
                ),
            },
            {
                "numero": "16",
                "path": "Título III > Párrafo 4° > Art. 16",
                "texto": (
                    "Artículo 16.- No producirán efecto alguno en los contratos de adhesión las cláusulas "
                    "o estipulaciones que: a) Otorguen a una de las partes la facultad de dejar sin efecto "
                    "o modificar a su solo arbitrio el contrato o de suspender unilateralmente su ejecución, "
                    "salvo cuando ella se conceda al comprador en las modalidades de venta por correo, a "
                    "domicilio, por muestrario, usando medios audiovisuales, u otras análogas; b) Establezcan "
                    "incrementos de precio por servicios, accesorios, financiamiento o recargos, salvo que "
                    "dichos incrementos correspondan a prestaciones adicionales que sean susceptibles de ser "
                    "aceptadas o rechazadas en cada caso y estén consignadas por separado en forma específica; "
                    "c) Pongan de cargo del consumidor los efectos de deficiencias, omisiones o errores "
                    "administrativos, cuando ellos no le sean imputables; d) Inviertan la carga de la prueba "
                    "en perjuicio del consumidor; e) Contengan limitaciones absolutas de responsabilidad "
                    "frente al consumidor que puedan privar a éste de su derecho a resarcimiento frente a "
                    "deficiencias que afecten la utilidad o finalidad esencial del producto o servicio; "
                    "f) Incluyan espacios en blanco, que no hayan sido llenados o inutilizados antes de que "
                    "se suscriba el contrato; g) En contra de las exigencias de la buena fe, atendiendo para "
                    "estos efectos a parámetros objetivos, causen en perjuicio del consumidor, un desequilibrio "
                    "importante en los derechos y obligaciones que para las partes se deriven del contrato."
                ),
            },
        ],
    },
    {
        "tipo": "ley",
        "numero": "21521",
        "titulo": "Ley Fintec - Promueve la Competencia e Inclusión Financiera a través de la Innovación y Tecnología en la Prestación de Servicios Financieros",
        "organismo": "Congreso Nacional",
        "url_oficial": "https://www.bcn.cl/leychile/navegar?idNorma=21521",
        "articulos": [
            {
                "numero": "1",
                "path": "Título I > Art. 1",
                "texto": (
                    "Artículo 1.- Objeto. La presente ley tiene por objeto promover la competencia e "
                    "inclusión financiera a través de la innovación y tecnología en la prestación de "
                    "servicios financieros, estableciendo un marco regulatorio para las empresas que "
                    "presten dichos servicios mediante el uso de plataformas tecnológicas, y proteger "
                    "los intereses de los clientes de estas empresas."
                ),
            },
            {
                "numero": "2",
                "path": "Título I > Art. 2",
                "texto": (
                    "Artículo 2.- Definiciones. Para los efectos de esta ley se entenderá por: "
                    "a) Servicios financieros regulados por esta ley: los siguientes servicios prestados "
                    "habitualmente a terceros mediante plataformas tecnológicas: 1. Plataformas de "
                    "financiamiento colectivo; 2. Sistemas alternativos de transacción; 3. Intermediación "
                    "de instrumentos financieros; 4. Asesoría crediticia y de inversión; 5. Custodia de "
                    "instrumentos financieros; 6. Enrutamiento de órdenes; y 7. Los demás servicios que "
                    "determine la Comisión para el Mercado Financiero mediante norma de carácter general. "
                    "b) Plataforma tecnológica: la infraestructura tecnológica que permite la prestación "
                    "de los servicios financieros regulados por esta ley, incluyendo sitios web, "
                    "aplicaciones móviles y otros medios tecnológicos."
                ),
            },
            {
                "numero": "5",
                "path": "Título II > Art. 5",
                "texto": (
                    "Artículo 5.- Registro. Las personas que pretendan prestar los servicios financieros "
                    "regulados por esta ley deberán inscribirse en el Registro de Prestadores de Servicios "
                    "Financieros que la Comisión para el Mercado Financiero mantendrá para estos efectos. "
                    "La inscripción en el Registro será condición necesaria para iniciar la prestación de "
                    "los servicios regulados."
                ),
            },
            {
                "numero": "12",
                "path": "Título II > Art. 12",
                "texto": (
                    "Artículo 12.- Sistema de finanzas abiertas. Créase un sistema de finanzas abiertas "
                    "que permitirá, con el consentimiento del cliente, el intercambio de información y la "
                    "iniciación de pagos y otros servicios entre las instituciones participantes. Las "
                    "instituciones proveedoras de información deberán poner a disposición de las "
                    "instituciones basadas en información, a través de interfaces estandarizadas, la "
                    "información de sus clientes que estos hayan autorizado compartir. El sistema de "
                    "finanzas abiertas tiene por objeto fomentar la competencia, la inclusión financiera "
                    "y la innovación en el mercado financiero."
                ),
            },
        ],
    },
    {
        "tipo": "ley",
        "numero": "18045",
        "titulo": "Ley de Mercado de Valores",
        "organismo": "Congreso Nacional",
        "url_oficial": "https://www.bcn.cl/leychile/navegar?idNorma=18045",
        "articulos": [
            {
                "numero": "1",
                "path": "Título I > Art. 1",
                "texto": (
                    "Artículo 1°.- A las disposiciones de la presente ley queda sometida la oferta "
                    "pública de valores y sus respectivos mercados e intermediarios, los que comprenden "
                    "las bolsas de valores, los corredores de bolsa y los agentes de valores; los "
                    "emisores e instrumentos de oferta pública y las operaciones con valores de oferta "
                    "pública. Quedan también sometidos a esta ley los mercados secundarios de valores "
                    "fuera de bolsa y las empresas de auditoría externa."
                ),
            },
            {
                "numero": "4",
                "path": "Título I > Art. 4",
                "texto": (
                    "Artículo 4°.- Se entiende por oferta pública de valores la dirigida al público en "
                    "general o a ciertos sectores o a grupos específicos de éste. Sólo se considerará "
                    "pública la oferta de valores que cumpliere los requisitos que disponga esta ley."
                ),
            },
            {
                "numero": "9",
                "path": "Título II > Art. 9",
                "texto": (
                    "Artículo 9°.- La inscripción en el Registro de Valores obliga al emisor a divulgar "
                    "en forma veraz, suficiente y oportuna toda información esencial respecto de sí mismo, "
                    "de los valores ofrecidos y de la oferta. Se entiende por información esencial aquella "
                    "que un hombre juicioso consideraría importante para sus decisiones sobre inversión."
                ),
            },
            {
                "numero": "164",
                "path": "Título XXI > Art. 164",
                "texto": (
                    "Artículo 164.- Para los efectos de esta ley, se entiende por información privilegiada "
                    "cualquier información referida a uno o varios emisores de valores, a sus negocios o a "
                    "uno o varios valores por ellos emitidos, no divulgada al mercado y cuyo conocimiento, "
                    "por su naturaleza, sea capaz de influir en la cotización de los valores emitidos, como "
                    "asimismo, la información reservada a que se refiere el artículo 10 de esta ley. "
                    "También se entenderá por información privilegiada, la que se tiene de las operaciones "
                    "de adquisición o enajenación a realizar por un inversionista institucional en el "
                    "mercado de valores."
                ),
            },
            {
                "numero": "165",
                "path": "Título XXI > Art. 165",
                "texto": (
                    "Artículo 165.- Cualquier persona que en razón de su cargo, posición, actividad o "
                    "relación tenga acceso a información privilegiada, deberá guardar reserva y no podrá "
                    "utilizarla en beneficio propio o ajeno, ni adquirir o enajenar, para sí o para "
                    "terceros, directamente o a través de otras personas los valores sobre los cuales "
                    "posea información privilegiada. Asimismo, se les prohíbe valerse de la información "
                    "privilegiada para obtener beneficios o evitar pérdidas, mediante cualquier tipo de "
                    "operación con los valores a que ella se refiera o con instrumentos cuyo precio o "
                    "resultado dependa o esté condicionado, en todo o en parte significativa, por dichos "
                    "valores."
                ),
            },
        ],
    },
    {
        "tipo": "ley",
        "numero": "18010",
        "titulo": "Ley sobre Operaciones de Crédito de Dinero",
        "organismo": "Congreso Nacional",
        "url_oficial": "https://www.bcn.cl/leychile/navegar?idNorma=18010",
        "articulos": [
            {
                "numero": "1",
                "path": "Título I > Art. 1",
                "texto": (
                    "Artículo 1°.- Son operaciones de crédito de dinero aquéllas por las cuales una de "
                    "las partes entrega o se obliga a entregar una cantidad de dinero y la otra a pagarla "
                    "en un momento distinto de aquel en que se celebra la convención. Constituye también "
                    "operación de crédito de dinero el descuento de documentos representativos de dinero, "
                    "sea que lleve o no envuelta la responsabilidad del cedente."
                ),
            },
            {
                "numero": "6",
                "path": "Título I > Art. 6",
                "texto": (
                    "Artículo 6°.- No puede estipularse un interés que exceda en más de un 50% al "
                    "corriente que rija al momento de la convención, ya sea que se pacte tasa fija o "
                    "variable. Este límite de interés se denomina interés máximo convencional. "
                    "La tasa de interés corriente es el promedio ponderado por montos de las tasas "
                    "cobradas por los bancos establecidos en Chile, en las operaciones que realicen "
                    "en el país. Corresponde a la Superintendencia de Bancos e Instituciones Financieras "
                    "determinar las tasas de interés corriente."
                ),
            },
            {
                "numero": "8",
                "path": "Título I > Art. 8",
                "texto": (
                    "Artículo 8°.- Se tendrá por no escrito todo pacto de intereses que exceda al máximo "
                    "convencional, y en tal caso los intereses se reducirán al interés corriente que rija "
                    "al momento de la convención. En todo caso, cuando corresponda devolver intereses en "
                    "virtud de lo dispuesto en esta ley, las cantidades percibidas en exceso deberán "
                    "reajustarse en la forma señalada en el artículo 3°, inciso primero."
                ),
            },
        ],
    },
    {
        "tipo": "ley",
        "numero": "20345",
        "titulo": "Ley sobre Sistemas de Compensación y Liquidación de Instrumentos Financieros",
        "organismo": "Congreso Nacional",
        "url_oficial": "https://www.bcn.cl/leychile/navegar?idNorma=20345",
        "articulos": [
            {
                "numero": "1",
                "path": "Título I > Art. 1",
                "texto": (
                    "Artículo 1°.- La presente ley tiene por objeto establecer el marco legal que regule "
                    "los sistemas de compensación y liquidación de instrumentos financieros y las entidades "
                    "que los administren, con el fin de asegurar su correcto funcionamiento y reducir los "
                    "riesgos sistémicos asociados a dichas actividades."
                ),
            },
        ],
    },
]


async def main():
    logger.info("=== Iniciando seed de datos demo ===")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Tablas creadas/verificadas")

    async with async_session() as db:
        total_chunks = 0

        for norma_data in NORMAS_SEED:
            logger.info("Procesando: %s %s - %s", norma_data["tipo"], norma_data["numero"], norma_data["titulo"])

            # Crear hash simple del contenido
            import hashlib
            contenido_total = "".join(a["texto"] for a in norma_data["articulos"])
            hash_contenido = hashlib.sha256(contenido_total.encode()).hexdigest()

            # Crear norma
            norma_db = Norma(
                tipo=norma_data["tipo"],
                numero=norma_data["numero"],
                titulo=norma_data["titulo"],
                organismo=norma_data["organismo"],
                url_oficial=norma_data["url_oficial"],
                hash_contenido=hash_contenido,
            )
            db.add(norma_db)
            await db.flush()

            # Crear artículos y recopilar chunks
            todos_textos = []
            chunks_info = []

            for i, art_data in enumerate(norma_data["articulos"]):
                articulo_db = Articulo(
                    norma_id=norma_db.id,
                    path=art_data["path"],
                    numero=art_data["numero"],
                    texto=art_data["texto"],
                    orden=i + 1,
                    vigente=True,
                )
                db.add(articulo_db)
                await db.flush()

                # Cada artículo es un chunk (son cortos para la demo)
                todos_textos.append(art_data["texto"])
                chunks_info.append({
                    "articulo_id": articulo_db.id,
                    "texto": art_data["texto"],
                    "metadata": {
                        "norma": norma_data["titulo"],
                        "articulo": art_data["numero"],
                        "path": art_data["path"],
                    },
                })

            # Generar embeddings en batch
            logger.info("  Generando embeddings para %d chunks...", len(todos_textos))
            try:
                embeddings = await generar_embeddings(todos_textos)
            except Exception as e:
                logger.error("  Error generando embeddings: %s", e)
                embeddings = [None] * len(todos_textos)

            # Almacenar chunks
            for i, info in enumerate(chunks_info):
                chunk_db = Chunk(
                    articulo_id=info["articulo_id"],
                    texto=info["texto"],
                    embedding=embeddings[i] if embeddings[i] else None,
                    metadata_=info["metadata"],
                    tokens=len(info["texto"].split()),
                )
                db.add(chunk_db)
                total_chunks += 1

            logger.info("  OK: %d artículos, %d chunks", len(norma_data["articulos"]), len(todos_textos))

        await db.commit()
        logger.info("=== Seed completado: %d normas, %d chunks ===", len(NORMAS_SEED), total_chunks)

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
