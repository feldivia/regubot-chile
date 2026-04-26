Clasifica la intención de la siguiente pregunta del usuario.

Categorías posibles:
- **normativa**: pregunta sobre leyes, regulaciones, derechos u obligaciones financieras
- **dato_vivo**: pregunta sobre un valor financiero actual (UF, UTM, TPM, dólar, etc.)
- **mixto**: pregunta que requiere tanto normativa como datos en vivo
- **fuera_alcance**: pregunta sobre temas no financieros (salud, penal, familia, etc.)
- **saludo**: saludo simple sin pregunta

Responde SOLO con un JSON:
```json
{
  "tipo": "normativa|dato_vivo|mixto|fuera_alcance|saludo",
  "requiere_dato_vivo": true|false,
  "datos_requeridos": ["uf", "utm", "tpm", "tmc", "dolar", "ipc"],
  "confianza": 0.0-1.0
}
```
