"""Tests para el query planner."""

from app.orchestrator.intent import Intencion
from app.orchestrator.planner import planificar_consulta


class TestPlanner:
    def test_saludo_retorna_respuesta_directa(self):
        intencion = Intencion(tipo="saludo", confianza=0.95)
        plan = planificar_consulta("Hola", intencion)

        assert plan.consultar_rag is False
        assert plan.respuesta_directa is not None
        assert "ReguBot" in plan.respuesta_directa

    def test_fuera_alcance_retorna_respuesta_directa(self):
        intencion = Intencion(tipo="fuera_alcance", confianza=0.8)
        plan = planificar_consulta("¿Cómo tramito mi divorcio?", intencion)

        assert plan.consultar_rag is False
        assert plan.respuesta_directa is not None

    def test_normativa_consulta_rag(self):
        intencion = Intencion(tipo="normativa", confianza=0.8)
        plan = planificar_consulta("¿Puedo pagar mi crédito anticipadamente?", intencion)

        assert plan.consultar_rag is True
        assert plan.consultar_datos_vivos is False

    def test_dato_vivo_incluye_tipo(self):
        intencion = Intencion(tipo="dato_vivo", confianza=0.9, requiere_dato_vivo=True)
        plan = planificar_consulta("¿Cuánto vale la UF hoy?", intencion)

        assert plan.consultar_datos_vivos is True
        assert "uf" in plan.datos_vivos_requeridos

    def test_filtro_por_organismo_cmf(self):
        intencion = Intencion(tipo="normativa", confianza=0.8)
        plan = planificar_consulta("¿Qué dice la CMF sobre cobros?", intencion)

        assert plan.filtros_rag.get("organismo") == "CMF"
