# Datos disponibles en ReguBot Chile

Ultima actualizacion: 2026-04-27

Este documento lista toda la informacion que el chatbot tiene disponible para responder consultas.

---

## Normativa en la base de datos (5 leyes, 17 articulos)

### Ley 19.496 — Proteccion de los Derechos de los Consumidores (4 articulos)

| Articulo | Ubicacion | Contenido |
|----------|-----------|-----------|
| Art. 1 | Titulo I | Definicion de consumidor y proveedor. Objeto de la ley. |
| Art. 3 | Titulo I | 6 derechos basicos del consumidor: libre eleccion, informacion veraz, no discriminacion, seguridad, reparacion/indemnizacion, educacion para consumo responsable. |
| Art. 12 | Titulo III, Parrafo 1 | Obligacion del proveedor de respetar terminos ofrecidos/convenidos. |
| Art. 16 | Titulo III, Parrafo 4 | Clausulas abusivas en contratos de adhesion (7 tipos que no producen efecto). |

### Ley 21.521 — Ley Fintec (4 articulos)

| Articulo | Ubicacion | Contenido |
|----------|-----------|-----------|
| Art. 1 | Titulo I | Objeto: promover competencia e inclusion financiera via tecnologia. |
| Art. 2 | Titulo I | Definiciones: 7 tipos de servicios financieros regulados, plataforma tecnologica. |
| Art. 5 | Titulo II | Registro de Prestadores de Servicios Financieros (CMF). |
| Art. 12 | Titulo II | Sistema de finanzas abiertas: intercambio de informacion con consentimiento del cliente. |

### Ley 18.045 — Mercado de Valores (5 articulos)

| Articulo | Ubicacion | Contenido |
|----------|-----------|-----------|
| Art. 1 | Titulo I | Ambito: oferta publica de valores, bolsas, corredores, agentes, emisores. |
| Art. 4 | Titulo I | Definicion de oferta publica de valores. |
| Art. 9 | Titulo II | Obligacion de divulgar informacion esencial al inscribirse en Registro de Valores. |
| Art. 164 | Titulo XXI | Definicion de informacion privilegiada. |
| Art. 165 | Titulo XXI | Prohibicion de uso de informacion privilegiada (insider trading). |

### Ley 18.010 — Operaciones de Credito de Dinero (3 articulos)

| Articulo | Ubicacion | Contenido |
|----------|-----------|-----------|
| Art. 1 | Titulo I | Definicion de operacion de credito de dinero. |
| Art. 6 | Titulo I | Interes maximo convencional (50% sobre corriente). Tasa de interes corriente. |
| Art. 8 | Titulo I | Sancion por pacto de intereses que exceda el maximo: se reduce a interes corriente. |

### Ley 20.345 — Sistemas de Compensacion y Liquidacion de Instrumentos Financieros (1 articulo)

| Articulo | Ubicacion | Contenido |
|----------|-----------|-----------|
| Art. 1 | Titulo I | Objeto: marco legal para sistemas de compensacion y liquidacion, reducir riesgos sistemicos. |

---

## Temas que el chatbot PUEDE responder

Con los datos actuales, el chatbot puede responder preguntas sobre:

- Derechos del consumidor (libre eleccion, informacion, no discriminacion, seguridad, reparacion)
- Clausulas abusivas en contratos
- Obligaciones del proveedor
- Que es la Ley Fintec y finanzas abiertas
- Servicios financieros regulados (plataformas, crowdfunding, etc.)
- Registro de prestadores fintech en la CMF
- Oferta publica de valores
- Informacion privilegiada e insider trading
- Tasa maxima de interes (interes maximo convencional)
- Operaciones de credito de dinero
- Sistemas de pago y compensacion

## Temas que el chatbot NO puede responder (faltan datos)

- Sociedades Anonimas (Ley 18.046) — no esta en la DB
- Administracion de Fondos (Ley 20.712) — no esta en la DB
- Sistema de Pensiones (DL 3.500) — no esta en la DB
- Comision para el Mercado Financiero (Ley 21.000) — no esta en la DB
- Normativa secundaria CMF (NCG, circulares)
- Normativa SII, SP, SERNAC
- Articulos no incluidos de las 5 leyes que si estan

## Datos en vivo (configurados pero requieren credenciales)

| Dato | Estado | Requisito |
|------|--------|-----------|
| UF | No disponible | Credenciales API BCCh |
| UTM | No disponible | Credenciales API BCCh |
| TPM | No disponible | Credenciales API BCCh |
| Dolar observado | No disponible | Credenciales API BCCh |
| IPC | No disponible | Credenciales API BCCh |
| TMC | No disponible | Scraper CMF (no probado) |
| Sueldo minimo | Hardcodeado en codigo | Actualizar manualmente |

---

## Como agregar mas datos

1. **Agregar articulos**: editar `backend/scripts/seed_demo.py`, agregar entradas al array `NORMAS_SEED`
2. **Ejecutar seed**: `DATABASE_URL=... OPENAI_API_KEY=... python backend/scripts/seed_demo.py`
3. **Nota**: el seed no es idempotente — si se ejecuta dos veces, duplica los datos. Hacer DROP de las tablas antes de re-ejecutar si es necesario.
