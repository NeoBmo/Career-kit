# Plan: una sola fuente y un repositorio publicable

## Decisiones

- `content/<persona>/cv.json` con textos por idioma (`{"es": ..., "en": ...}`).
  Por qué: un solo archivo alimenta LaTeX y la IA, y se valida.
- Renderizador en Python sin dependencias (`scripts/render.py`), que produce
  `builds/<persona>/cv-<lang>-<profile>.tex`. Por qué: la plantilla actual ya es
  modular; generarla desde datos elimina la copia a mano.
- Se conservan `styles/modern.tex` y `lang/*.tex`. Por qué: el diseño no cambia.
- `content/*` ignorado salvo `content/example/`. La persona real vive en
  `content/private/`. Por qué: los datos personales nunca entran en el historial.
- Compilación local con XeLaTeX si existe; si no, `docker run --network none` con
  `texlive/texlive` fijado por digest. Por qué: reproducible y sin instalar nada.
- Fuente con respaldo (`\IfFontExistsTF`). Por qué: Liberation Sans no viene en TeX
  Live; TeX Gyre Heros sí y es métricamente cercana.
- `scripts/ats_check.py` con `pdftotext`. Por qué: un ATS lee texto; si el texto no
  sale, el CV no existe para él.
- CI en GitHub Actions con acciones oficiales fijadas por SHA y el mismo contenedor.
- Licencia MIT, como el resto de repos de la persona.

## Formato de `cv.json`

Un texto traducible es un objeto `{"es": "...", "en": "..."}`; basta con los idiomas
que usen las variantes. `null` en `end` significa «Presente».

```json
{
  "person": {
    "name": "Alex Rivera",
    "location": {"es": "Medellín, Colombia", "en": "Medellín, Colombia"},
    "phone": "+00 000 000 0000",
    "email": "alex@example.com"
  },
  "more": {"label": "Portafolio", "url": "https://example.com"},
  "profiles": {
    "software-developer": {
      "title": {"es": "Desarrollador de Software", "en": "Software Developer"},
      "summary": {"es": "...", "en": "..."},
      "keywords": {"es": ["React", "SQL"], "en": ["React", "SQL"]}
    }
  },
  "experience": [
    {"role": {"es": "...", "en": "..."}, "organization": "...", "start": "2023",
     "end": null, "highlights": {"es": ["..."], "en": ["..."]}}
  ],
  "skills": [{"label": {"es": "Frontend", "en": "Frontend"}, "items": {"es": "...", "en": "..."}}],
  "education": [
    {"title": {"es": "...", "en": "..."}, "organization": "...", "start": null,
     "end": "2021", "details": {"es": "...", "en": "..."}}
  ],
  "variants": [{"lang": "es", "profile": "software-developer"}]
}
```

Orden de secciones fijo, el de `main.tex`: perfil, experiencia, habilidades,
educación y el pie «Conoce más». Las keywords van a `pdfkeywords` y se comprueban
en el texto con `ats_check`.

## Ajustes tras el ataque del pez dorado (2026-11-24)

Aceptados: esquema definido antes del renderizador y variantes explícitas; línea base
congelada compilando las fuentes actuales en el contenedor (no los PDF de julio);
escape en una pasada con correo y URL fuera del escape; `FALLBACK` y notas fuera del
PDF; criterio de datos personales acotado y comprobado en CI; digest en
`scripts/texlive-image.txt`; criterio de CI; README como tarea.

Cambiado respecto a la propuesta: en lugar de TeX Gyre Heros, Liberation Sans 2.1.5
va en `assets/fonts/` (SIL OFL 1.1, tarball oficial con SHA-256
`7191c669bf38899f73a2094ed00f7b800553364f90e2637010a69c0e268f25d0`), así que el
diseño no cambia y el PDF es igual en todas partes.

Descartado: validar con JSON Schema y `jsonschema`, porque añade una dependencia; un
validador propio con tests da el mismo resultado.

## Archivos afectados

- `content/example/cv.json` (nuevo, ficticio) y `content/private/cv.json` (nuevo,
  ignorado; migra `config/personal.tex`, `config/profile-*.tex`, `sections/**`).
- `schemas/cv.schema.json` (nuevo); `scripts/render.py`, `scripts/ats_check.py`
  (nuevos); `scripts/generate_cv.py`, `scripts/cli.py`, `scripts/build.sh`,
  `Makefile` (adaptados).
- `styles/modern.tex` (respaldo de fuente).
- Se retiran `main.tex`, `config/`, `sections/`, `builds/*.tex` y `data/cv-data.json`.
- `tests/` (ampliados), `.github/workflows/ci.yml`, `README.md`, `LICENSE`,
  `.gitignore`.

## Riesgos

- Perder o alterar contenido real al migrar: copia de seguridad previa y comparación
  del texto de los PDF antes y después.
- Filtrar datos personales a git: `.gitignore` antes del primer commit y búsqueda de
  los datos reales en `git ls-files` y en el historial.
- Imagen de TeX Live grande: se descarga una vez y se fija por digest.
