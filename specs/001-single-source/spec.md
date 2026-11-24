# Una sola fuente y un repositorio publicable

## Contexto y límites

Career Kit genera CV en LaTeX por idioma y perfil, y adapta uno a una vacante con
Groq. Hoy el contenido vive dos veces (`sections/*.tex` para LaTeX y
`data/cv-data.json` para la IA, que además está incompleto), los datos personales
reales están mezclados con el código, nunca se ha compilado en esta máquina y no
hay control de versiones.

Fuera de alcance: cambiar el diseño visual, añadir plantillas nuevas, publicar el
repositorio como público (lo decide la persona).

## Objetivo

Un solo `cv.json` por persona del que salen todas las variantes y la adaptación con
IA; un perfil de ejemplo ficticio que se puede publicar; y una compilación
reproducible que cualquiera puede comprobar.

## Requisitos

- RF-01: EL SISTEMA leerá todo el contenido de un CV de un único archivo
  `content/<persona>/cv.json` y lo validará con un validador propio, sin
  dependencias, que informe el campo exacto que falla.
- RF-02: CUANDO se renderiza una persona, EL SISTEMA generará un `.tex` completo por
  cada variante de la lista `variants` de su `cv.json` (pares idioma y perfil
  explícitos, no su producto), sin contenido del CV escrito a mano en LaTeX. Las
  etiquetas de la plantilla («Experiencia», «Actualidad») siguen en `lang/*.tex`.
- RF-03: EL SISTEMA escapará los caracteres especiales de LaTeX en una sola pasada
  por carácter, y pasará correos y URL a `\href` sin escaparlos como texto.
- RF-04: EL SISTEMA incluirá en el repositorio sólo la persona `content/example/`,
  ficticia; cualquier otra carpeta de `content/` quedará fuera de git.
- RF-05: CUANDO se adapta un CV a una vacante, EL SISTEMA partirá del mismo
  `cv.json` y de una variante concreta, y el resultado se renderizará con el mismo
  renderizador.
- RF-06: SI Groq falla o responde algo inválido, ENTONCES EL SISTEMA usará la
  adaptación local y lo marcará como `FALLBACK` en la propuesta JSON y en la
  consola, nunca dentro del PDF. Las notas de revisión tampoco van al PDF.
- RF-07: CUANDO no hay XeLaTeX local, EL SISTEMA compilará dentro de un contenedor
  de TeX Live con la imagen fijada por un digest escrito en un archivo del repo, y
  sin red.
- RF-08: EL SISTEMA usará la fuente Liberation Sans incluida en el repo (SIL OFL
  1.1), así que el PDF es igual en cualquier máquina.
- RF-09: CUANDO se comprueba un PDF, EL SISTEMA extraerá su texto e informará qué
  keywords del perfil no aparecen y si el texto sale vacío o desordenado.
- RF-10: CUANDO se sube código a GitHub, EL SISTEMA ejecutará los tests, buscará
  correos y teléfonos reales en los archivos versionados, compilará las variantes
  del ejemplo y dejará los PDF como artefacto.

## Criterios de aceptación

- [ ] `py -m unittest discover -s tests` pasa, con tests del renderizador, del escape
      carácter por carácter, de la validación, del camino `FALLBACK` y de la
      comprobación ATS.
- [ ] Las variantes de `content/example/` compilan a PDF en el contenedor.
- [ ] Antes de migrar se congela una línea base: las cuatro variantes reales
      compiladas desde las fuentes LaTeX actuales y su texto con `pdftotext`. Después,
      el texto de las variantes generadas desde `cv.json` coincide con esa línea base,
      salvo estas diferencias aceptadas: espacios y saltos de línea.
- [ ] Ningún archivo versionado contiene el teléfono, el correo, la ubicación, los
      enlaces personales ni las empresas del CV real. El nombre del autor sí puede
      aparecer, en la firma y la licencia.
- [ ] La comprobación ATS no informa keywords faltantes en las variantes del ejemplo.
- [ ] El workflow de CI pasa en el primer push a un repositorio privado.
- [ ] El README describe el flujo nuevo y muestra una captura de un PDF del ejemplo.
