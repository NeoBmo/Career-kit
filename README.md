<p align="center">
  <img src="assets/banner.svg" width="100%" alt="Career Kit: una hoja fuente se ramifica en cuatro CV, en español e inglés y para distintos perfiles.">
</p>

# Career Kit

**No es un CV: es un generador de CVs.** El contenido se escribe una vez, y cada
variante (idioma, perfil, palabras clave ATS) sale de ahí sin copiar y pegar entre
documentos.

Hay dos caminos. El **LaTeX modular** es el principal: genera las cuatro variantes
que hay hoy en `builds/`. El **flujo con IA** en Python, que adapta el CV a una
vacante con Groq, es experimental y tiene fallos conocidos: ver
[Estado](#estado).

<!-- TODO: captura de la primera página de un PDF de builds/out/, sin datos de contacto. -->

## Generar un CV con LaTeX

Requiere XeLaTeX, por la tipografía con `fontspec`. `make` usa además `latexmk`.

| Comando | Qué hace |
|---|---|
| `./scripts/build.sh cv-es-software-developer` | Compila una variante en `builds/out/` |
| `./scripts/build.sh` | Compila todas las de `builds/` |
| `make build NAME=cv-es-frontend-developer` | Lo mismo con `make` y `latexmk` |
| `make all` | Todas, con `make` |
| `make list` | Lista las variantes disponibles |
| `make clean` | Borra `builds/out/` y los auxiliares de LaTeX |

«Todas» es cada `builds/*.tex`, así que incluye `builds/generated-cv.tex` si el
flujo con IA lo generó.

### Añadir una variante

- **Nuevo perfil**, por ejemplo Full Stack Developer:
  1. `config/profile-full-stack-developer.tex`, que define con `\newcommand` tres
     macros: `\ckProfileTitle` (el título), `\ckKeywords` (las keywords ATS) y
     `\ckSummaryFile` (`full-stack-developer`, el nombre del resumen del paso 2).
     Sin `\ckSummaryFile`, `main.tex` no encuentra el resumen y la compilación
     falla.
  2. `sections/summary/full-stack-developer-es.tex`, y `-en.tex` si aplica.
  3. `builds/cv-es-full-stack-developer.tex`:
     ```latex
     \def\ckLang{es}
     \def\ckProfile{full-stack-developer}
     \input{main.tex}
     ```
  4. Compilar.
- **Nuevo idioma:** `lang/xx.tex` con las etiquetas traducidas y la versión `-xx.tex`
  de cada sección de `sections/`.
- **Nueva experiencia:** `sections/experience/nueva-es.tex`, y `-en.tex`, incluida
  en `main.tex`.

## Adaptar a una vacante con IA (experimental)

Lee `data/cv-data.json`, pide a Groq un resumen y un objetivo alineados con la
vacante, y escribe `builds/generated-cv.tex` y una propuesta
`generated-cv.proposal.json`. Con vacante, el LaTeX incluye una sección de notas
para revisar a mano. Si Groq falla o responde algo inválido, usa una adaptación local sin IA y lo
anota como `FALLBACK`.

Copia `.env.example` a `.env`:

| Variable | Qué es |
|---|---|
| `GROQ_API_KEY` | Tu clave de API de Groq. Va sólo en `.env`, nunca en el repo |
| `GROQ_MODEL` | Opcional. Por defecto, `llama-3.1-8b-instant` |
| `GROQ_API_URL` | Opcional. Por defecto, el endpoint de chat de Groq |

Desde la raíz del proyecto:

| Comando | Qué hace |
|---|---|
| `py -m scripts.cli` | Menú: generar el CV base o adaptarlo a una vacante |
| `py -m scripts.generate_cv` | CV base desde `data/cv-data.json` |
| `py -m scripts.generate_cv --job-description "…"` | CV adaptado a la vacante, más la propuesta JSON |
| `py -m unittest tests/test_generate_cv.py tests/test_groq_client.py` | Tests del flujo |

Hay que lanzarlo con `-m`: los scripts importan `scripts.…`, y por ruta directa
(`py scripts/generate_cv.py`) fallan con `ModuleNotFoundError`.

## Estado

Comprobado el 2026-11-19:

- **LaTeX:** sin verificar en esta máquina, porque no tiene XeLaTeX instalado. Los
  cuatro PDF de `builds/out/` son del 2026-07-09.
- **Tests:** los 6 pasan. Uno de ellos impide que vuelva el fallo de la doble barra.
- **CLI:** la opción 1 genera el CV base. La opción 2 no se probó, porque llama a
  Groq.
- **Arreglado ese día:** el `.tex` generado escribía `\\documentclass`, con dos
  barras, e `\input{../styles/modern.tex}`, una ruta que no existe desde la raíz:
  no podía compilar. La CLI llamaba a `generate_cv.py` por ruta directa y fallaba
  siempre, y en la consola de Windows se caía al pintar el menú.
- **Sin verificar:** que el `.tex` generado compile, por falta de XeLaTeX.
- Hoy conviven dos fuentes de contenido: `sections/*.tex` para LaTeX y
  `data/cv-data.json` para el flujo con IA.

## Decisiones de diseño

- Contenido, diseño, configuración y salida separados: una variante nueva no toca
  el contenido.
- Todo el diseño vive en `styles/modern.tex`: tinta `#1A1A1A`, acento `#1F5FBF` y
  Liberation Sans, métricamente compatible con Arial.
- Las keywords ATS van en los metadatos del PDF (`pdfkeywords`) y también en la
  prosa de cada sección.
- Cada experiencia está redactada como logros (situación → acción → impacto), no
  como lista de tareas.

<details>
<summary>Estructura</summary>

```
main.tex          orquestador: config → lang → style → sections; no se compila directo
Makefile          build, all, list y clean con latexmk
config/           personal.tex (datos fijos) y un profile-*.tex por perfil
lang/             es.tex y en.tex: etiquetas de la plantilla, no contenido
styles/           modern.tex: tipografía, color y espaciado
sections/         summary/, experience/, skills/ y education/, un archivo por idioma disponible
builds/           un .tex por variante; out/ con los PDF compilados
data/             cv-data.json: contenido para el flujo con IA
prompts/          prompt de sistema y plantilla del prompt de usuario para Groq
schemas/          esquema de la respuesta que se espera de Groq
scripts/          build.sh, generate_cv.py, groq_client.py, cli.py y utilidades
tests/            tests de unittest del flujo con IA
```

</details>

---

Hecho por Luis Rodríguez · [neobmo.github.io](https://neobmo.github.io)
