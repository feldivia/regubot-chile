"""Cliente para datos en vivo: UF, UTM, TPM, TMC, dólar, IPC."""

import logging
from datetime import date, datetime

import httpx

from app.config import settings
from app.utils.cache import cache_get, cache_set

logger = logging.getLogger(__name__)

# Endpoints del Banco Central (API SI3)
BCCH_API_BASE = "https://si3.bcentral.cl/SieteRestWS/SieteRestWS.ashx"

# Series del Banco Central
SERIES_BCCH = {
    "uf": "F073.UFF.PRE.Z.D",
    "dolar": "F073.TCO.PRE.Z.D",
    "tpm": "F022.TPM.TIN.D001.NO.Z.D",
    "ipc": "F074.IPC.VAR.Z.Z.M",
    "utm": "F073.UTR.PRE.Z.M",
}

# TTL de cache por tipo de dato (en segundos)
TTL_CACHE = {
    "uf": 3600,         # 1 hora
    "utm": 86400,       # 24 horas
    "tpm": 3600,        # 1 hora
    "dolar": 3600,      # 1 hora
    "ipc": 86400,       # 24 horas
    "tmc": 43200,       # 12 horas
    "sueldo_minimo": 604800,  # 7 días
}


async def obtener_dato_vivo(tipo: str) -> dict:
    """Obtiene un dato financiero en vivo, con cache."""
    clave_cache = f"dato_vivo:{tipo}"

    # Intentar cache primero
    cached = await cache_get(clave_cache)
    if cached:
        logger.debug("Cache hit para %s", tipo)
        return cached

    # Obtener dato fresco
    resultado = await _obtener_dato_fresco(tipo)

    # Guardar en cache
    if resultado and "error" not in resultado:
        await cache_set(clave_cache, resultado, TTL_CACHE.get(tipo, 3600))

    return resultado


async def _obtener_dato_fresco(tipo: str) -> dict:
    """Obtiene el dato directamente de la fuente."""
    if tipo in SERIES_BCCH:
        # BCCh requiere credenciales; si no están configuradas, retornar no disponible
        if not settings.bcch_user or not settings.bcch_password:
            return {
                "tipo": tipo,
                "error": "API del Banco Central no configurada (BCCH_USER/BCCH_PASSWORD)",
                "fuente": "Banco Central de Chile",
            }
        return await _consultar_bcch(tipo, SERIES_BCCH[tipo])
    elif tipo == "tmc":
        return await _obtener_tmc()
    elif tipo == "sueldo_minimo":
        return _obtener_sueldo_minimo()
    else:
        return {"error": f"Tipo de dato no soportado: {tipo}"}


async def _consultar_bcch(tipo: str, serie: str) -> dict:
    """Consulta una serie del Banco Central de Chile."""
    hoy = date.today()
    fecha_str = hoy.strftime("%Y-%m-%d")

    params = {
        "user": settings.bcch_user,
        "pass": settings.bcch_password,
        "firstdate": fecha_str,
        "lastdate": fecha_str,
        "timeseries": serie,
        "function": "GetSeries",
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(BCCH_API_BASE, params=params)
            response.raise_for_status()
            data = response.json()

            # Parsear respuesta del BCCh
            series = data.get("Series", {})
            obs = series.get("Obs", [])

            if obs:
                ultimo = obs[-1] if isinstance(obs, list) else obs
                valor = ultimo.get("value", "")
                fecha = ultimo.get("indexDateString", fecha_str)

                return {
                    "tipo": tipo,
                    "valor": valor,
                    "fecha": fecha,
                    "fuente": "Banco Central de Chile",
                    "serie": serie,
                }

            # Si no hay datos para hoy, buscar últimos 7 días
            return await _consultar_bcch_rango(tipo, serie, 7)

    except Exception as e:
        logger.warning("Error consultando BCCh para %s: %s", tipo, e)
        return {"tipo": tipo, "error": str(e), "fuente": "Banco Central de Chile"}


async def _consultar_bcch_rango(tipo: str, serie: str, dias: int) -> dict:
    """Consulta con rango de fechas para encontrar el último dato disponible."""
    from datetime import timedelta

    hoy = date.today()
    inicio = (hoy - timedelta(days=dias)).strftime("%Y-%m-%d")
    fin = hoy.strftime("%Y-%m-%d")

    params = {
        "user": settings.bcch_user,
        "pass": settings.bcch_password,
        "firstdate": inicio,
        "lastdate": fin,
        "timeseries": serie,
        "function": "GetSeries",
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(BCCH_API_BASE, params=params)
            response.raise_for_status()
            data = response.json()

            series = data.get("Series", {})
            obs = series.get("Obs", [])

            if obs:
                ultimo = obs[-1] if isinstance(obs, list) else obs
                return {
                    "tipo": tipo,
                    "valor": ultimo.get("value", ""),
                    "fecha": ultimo.get("indexDateString", ""),
                    "fuente": "Banco Central de Chile",
                    "serie": serie,
                }

    except Exception as e:
        logger.warning("Error consultando BCCh rango para %s: %s", tipo, e)

    return {"tipo": tipo, "error": "No se encontraron datos", "fuente": "Banco Central de Chile"}


async def _obtener_tmc() -> dict:
    """Obtiene la Tasa Máxima Convencional desde la CMF."""
    url = "https://www.cmfchile.cl/portal/estadisticas/606/w3-propertyvalue-28658.html"

    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(url)
            response.raise_for_status()

            from selectolax.parser import HTMLParser

            html = HTMLParser(response.text)
            # Buscar tablas con datos de TMC
            tablas = html.css("table")

            for tabla in tablas:
                celdas = tabla.css("td")
                for i, celda in enumerate(celdas):
                    texto = celda.text(strip=True)
                    if "%" in texto:
                        return {
                            "tipo": "tmc",
                            "valor": texto,
                            "fecha": date.today().strftime("%Y-%m-%d"),
                            "fuente": "CMF Chile",
                        }

    except Exception as e:
        logger.warning("Error obteniendo TMC: %s", e)

    return {"tipo": "tmc", "error": "No se pudo obtener TMC", "fuente": "CMF Chile"}


def _obtener_sueldo_minimo() -> dict:
    """Retorna el sueldo mínimo vigente (actualización manual)."""
    return {
        "tipo": "sueldo_minimo",
        "valor": "500.000",
        "fecha": "2025-07-01",
        "fuente": "Dirección del Trabajo",
        "nota": "Valor vigente desde julio 2025. Verificar actualizaciones.",
    }


async def obtener_multiples_datos(tipos: list[str]) -> dict[str, dict]:
    """Obtiene múltiples datos en vivo."""
    resultados = {}
    for tipo in tipos:
        resultados[tipo] = await obtener_dato_vivo(tipo)
    return resultados
