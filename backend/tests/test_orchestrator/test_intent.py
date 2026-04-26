"""Tests para el clasificador de intención."""

from app.orchestrator.intent import clasificar_intencion


class TestIntentClassifier:
    def test_detecta_pregunta_normativa(self):
        intencion = clasificar_intencion(
            "¿Puedo pagar anticipadamente mi crédito de consumo sin multa?"
        )
        assert intencion.tipo in ("normativa", "mixto")

    def test_detecta_dato_vivo(self):
        intencion = clasificar_intencion("¿Cuánto vale la UF hoy?")
        assert intencion.tipo in ("dato_vivo", "mixto")
        assert intencion.requiere_dato_vivo is True

    def test_detecta_mixto(self):
        intencion = clasificar_intencion(
            "¿Cuál es la tasa máxima convencional para créditos de consumo?"
        )
        assert intencion.requiere_dato_vivo is True

    def test_detecta_saludo(self):
        intencion = clasificar_intencion("Hola")
        assert intencion.tipo == "saludo"

    def test_detecta_fuera_alcance(self):
        intencion = clasificar_intencion("¿Cómo puedo tramitar mi divorcio?")
        assert intencion.tipo == "fuera_alcance"

    def test_pregunta_sobre_banco(self):
        intencion = clasificar_intencion(
            "¿Mi banco puede cobrarme comisión por mantención de cuenta?"
        )
        assert intencion.tipo in ("normativa", "mixto")

    def test_pregunta_sobre_pensiones(self):
        intencion = clasificar_intencion("¿Cuánto cotizo para mi AFP cada mes?")
        assert intencion.tipo in ("normativa", "mixto")
