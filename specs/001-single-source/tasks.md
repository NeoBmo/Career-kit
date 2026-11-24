# Tareas: una sola fuente y un repositorio publicable

| Tarea | Requisitos | Estado | Intento | Veredicto y evidencia |
|---|---|---|---|---|
| Línea base de las 4 variantes reales, compilada en el contenedor | criterio 3 | validada | 1/3 | 4 PDF y su texto en `content/private/baseline/`, ignorado por git |
| Renderizador, validador, escape, ejemplo ficticio, fuente incluida y `build.sh` con Docker | RF-01 a RF-04, RF-07, RF-08 | validada | 1/3 | 3 PDF del ejemplo de una página; revisión independiente |
| Comprobación ATS con `pdftotext` (OpenCode) | RF-09 | validada | 2/3 | Falsos positivos por subcadena y codificación corregidos en el segundo intento |
| Migrar el contenido real a `content/private/cv.json` y comparar con la línea base | criterio 3 | validada | 1/3 | Texto igual salvo las diferencias aceptadas en el criterio 3 |
| Adaptación con IA sobre el renderizador, `FALLBACK` fuera del PDF | RF-05, RF-06, RF-15 | validada | 1/3 | Tests con mocks; PDF sin «FALLBACK»; Groq no recibe nombre, teléfono, correo ni ubicación |
| CI, comprobación de datos personales, plantilla (OpenCode) | RF-10, RF-11, RF-12 | implementada | 1/3 | Coordinador simplificó `privacy_check` y reordenó los pasos; falta el primer push |
| Guía de Colombia, README, guía paso a paso, LICENSE y CONTRIBUTING | RF-13, RF-14, criterios 6 y 8 | implementada | 1/3 | Revisión de `goldfish` como persona que no programa: 8 hallazgos en curso |
| Revisión con `legal-compliance` | criterio 9 | validada | 1/3 | Sin `FALTA`: herramienta local sin servidor, uso personal excluido de la Ley 1581 (CO-1). Aviso de Groq ampliado; guía: pedir permiso si es el CV de otra persona |
| Cierre: revisión independiente con Opus | todos | en_progreso | 2/3 | CAMBIOS_NECESARIOS: test de privacidad que rompía las copias, orden en ATS, `more` opcional, secciones vacías, rutas de perfil, `https` en Groq |

## Traspaso

- Funcionó, con su evidencia: una sola fuente que compila en Docker (3 PDF del
  ejemplo y las 4 variantes reales); 54 tests; privacidad comprobada en todo el
  historial; delegación en OpenCode para ATS y CI, corregida por el coordinador.
- Falló: el primer intento de ATS de OpenCode (subcadenas y codificación); el test
  de privacidad que rompía la CI de cualquier copia (corregido en el cierre).
- Falta por probar: la CI en GitHub (primer push) y la plantilla con «Use this
  template» desde otra cuenta, que exige un repositorio público.
