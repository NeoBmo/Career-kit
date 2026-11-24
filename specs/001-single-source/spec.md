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

### Producto abierto para Colombia (añadido el 2026-11-24)

Career Kit pasa a ser un producto gratuito y de código abierto, en español, pensado
para personas en Colombia que no programan.

- RF-11: CUANDO alguien crea su copia desde la plantilla de GitHub y edita su
  `content/<persona>/cv.json` en el navegador, EL SISTEMA compilará sus variantes en
  GitHub Actions y dejará los PDF para descargar, sin instalar nada en su equipo.
- RF-12: EL SISTEMA ignorará en git sólo `content/private/`; cualquier otra persona
  de `content/` se puede versionar en una copia privada.
- RF-13: EL SISTEMA tendrá la documentación, los mensajes de la CLI y los errores de
  validación en español.
- RF-14: EL SISTEMA incluirá una guía de hoja de vida para Colombia que diga qué
  datos no hacen falta (documento de identidad, foto, fecha de nacimiento, estado
  civil) y por qué.
- RF-15: ANTES de enviar un CV a Groq, EL SISTEMA avisará de que el contenido sale a
  un tercero y pedirá confirmación en la CLI.

### Añadidos en el cierre (2026-11-24)

- RF-16: SI una copia de la plantilla es pública, ENTONCES EL SISTEMA hará fallar la
  CI con un aviso en español que explica cómo volverla privada.
- RF-17: EL SISTEMA no imprimirá el pie si no hay `more`, ni una sección vacía, ni
  su título: así sirve también a quien busca su primer empleo.
- RF-18: EL SISTEMA sólo aceptará minúsculas, números y guiones en los nombres de
  idioma y perfil, porque forman rutas de archivo.

## Criterios de aceptación

- [ ] `py -m unittest discover -s tests` pasa, con tests del renderizador, del escape
      carácter por carácter, de la validación, del camino `FALLBACK` y de la
      comprobación ATS.
- [ ] Las variantes de `content/example/` compilan a PDF en el contenedor.
- [ ] Antes de migrar se congela una línea base: las cuatro variantes reales
      compiladas desde las fuentes LaTeX actuales y su texto con `pdftotext`. Después,
      el texto de las variantes generadas desde `cv.json` coincide con esa línea base,
      salvo estas diferencias aceptadas: espacios y saltos de línea; el guionado de
      una palabra en inglés; y dos fechas que en la línea base se salían de la página
      («Presente» cortado y un año que no se veía) y ahora aparecen completas.
- [ ] Ningún archivo versionado contiene el teléfono, el correo, la ubicación, los
      enlaces personales ni las empresas del CV real. El nombre del autor sí puede
      aparecer, en la firma y la licencia.
- [ ] La comprobación ATS no informa keywords faltantes en las variantes del ejemplo.
- [ ] El workflow de CI pasa en el primer push a un repositorio privado.
- [ ] El README describe el flujo nuevo y muestra una captura de un PDF del ejemplo.
- [ ] `docs/guia.md` lleva a alguien sin experiencia de la plantilla al PDF, paso a
      paso, con la ruta exacta de cada botón de GitHub.
- [ ] La skill `legal-compliance` revisa el aviso del flujo con IA y la guía de
      Colombia, y su tabla no tiene `FALTA`.
