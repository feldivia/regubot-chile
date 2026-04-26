# Catálogo de fuentes de datos

## Normativa (RAG)

### Tier 1 - V1
| Fuente | URL | Método | Frecuencia |
|--------|-----|--------|------------|
| leychile.cl | https://www.bcn.cl/leychile/ | Scraping HTML | Semanal |
| CMF Normativa | https://www.cmfchile.cl | Scraping HTML | Semanal |
| BCCh Compendio | https://www.bcentral.cl/web/banco-central/normativa | Scraping PDF | Mensual |

### Leyes prioritarias
- Ley 19.496 - Protección del Consumidor
- Ley 21.521 - Fintec
- Ley 20.712 - Administración de Fondos
- Ley 18.010 - Operaciones de Crédito de Dinero
- Ley 18.045 - Mercado de Valores
- Ley 18.046 - Sociedades Anónimas
- Ley 20.345 - Sistemas de Pagos
- DL 3.500 - Sistema de Pensiones
- Ley 21.000 - CMF

### Tier 2
| Fuente | URL | Método |
|--------|-----|--------|
| SII | https://www.sii.cl/normativa_legislacion/ | Scraping |
| SP | https://www.spensiones.cl | Scraping |
| SERNAC | https://www.sernac.cl | Scraping selectivo |

## Datos en vivo (APIs)

| Dato | Fuente | Serie BCCh | Frecuencia |
|------|--------|-----------|------------|
| UF | BCCh | F073.UFF.PRE.Z.D | Diaria |
| UTM | BCCh | F073.UTR.PRE.Z.M | Mensual |
| TPM | BCCh | F022.TPM.TIN.D001.NO.Z.D | Eventos |
| TMC | CMF | Scraping | Quincenal |
| Dólar | BCCh | F073.TCO.PRE.Z.D | Diaria |
| IPC | BCCh | F074.IPC.VAR.Z.Z.M | Mensual |
| Sueldo mínimo | DT | Hardcode | Anual |
