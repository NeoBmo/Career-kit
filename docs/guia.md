# Guía paso a paso: tu hoja de vida en PDF, sin instalar nada

Esta guía es para quien no programa. Vas a crear tu propia copia de Career Kit en
GitHub, escribir tus datos en un archivo y descargar tus hojas de vida en PDF. Todo
se hace desde el navegador.

Qué necesitas:

- Una cuenta de GitHub (es gratis).
- Tus datos a la mano: experiencia, estudios y habilidades. Si dudas de qué poner o
  qué dejar fuera, lee antes la [guía de hoja de vida para Colombia](hoja-de-vida-colombia.md).

Los nombres de los botones de GitHub se escriben aquí en inglés, entre comillas. Si
tu GitHub está en otro idioma, o si GitHub cambia un botón, busca el equivalente. Donde
no estamos seguros del nombre exacto, lo decimos.

## Paso 1. Crea tu copia privada

1. Entra a <https://github.com/NeoBmo/Career-kit> e inicia sesión.
2. Arriba a la derecha, junto al botón verde «Code», pulsa el botón «Use this
   template» (el nombre puede variar) y elige «Create a new repository».
3. En el formulario:
   - **Owner:** déjalo en tu usuario.
   - **Repository name:** el que quieras, por ejemplo `mi-hoja-de-vida`.
   - **Description:** opcional.
   - **Visibility:** marca **Private**.
   - «Include all branches»: déjalo sin marcar.
4. Pulsa el botón verde «Create repository». Quedas dentro de tu copia.

**Por qué Private.** Tu `cv.json` va a llevar tu teléfono, tu correo y tu historial de
trabajo. En un repositorio público cualquiera puede leerlo, y los buscadores y los
programas que recorren GitHub también. En uno privado sólo lo ves tú. Los PDF que
descargas después son tuyos y los envías tú.

**Qué comprobar:** arriba del nombre de tu copia aparece la etiqueta «Private».

## Paso 2. Crea tu carpeta y edita tu `cv.json`

Tu hoja de vida vive en `content/<tu-nombre>/cv.json`. Partes de la del ejemplo.

### 2.1 Copia el ejemplo

1. En la pestaña «Code» de tu copia, abre la carpeta `content`, luego `example` y
   luego el archivo `cv.json`.
2. En la barra del archivo (arriba a la derecha del contenido) pulsa el ícono «Copy
   raw file» (dos cuadritos superpuestos). Ya tienes el texto copiado.
3. Vuelve a la raíz de tu copia (clic en el nombre del repositorio, arriba a la
   izquierda). Pulsa «Add file» y luego «Create new file».
4. En el cuadro de nombre escribe `content/tu-nombre/cv.json`. Al escribir la `/` GitHub
   crea la carpeta. Usa minúsculas, sin tildes ni espacios (`ana-perez`, no `Ana Pérez`).
   **No** llames la carpeta `private`: ese nombre se salta la compilación en GitHub y
   no obtendrías PDF.
5. Haz clic en el área grande de texto y pega con Ctrl+V.

### 2.2 Escribe tus datos

Con el archivo abierto en el editor, cambia el contenido del ejemplo por el tuyo.
Reglas para no romper el archivo (es formato JSON):

- Cada texto va entre comillas dobles `"..."`. Si necesitas unas comillas dentro del
  texto, escríbelas como `\"`.
- Entre un elemento y el siguiente va una coma. El último de una lista no lleva coma.
- No cambies los nombres de los campos (`person`, `experience`...), sólo lo que va a
  su derecha, entre comillas.
- Puedes escribir `&`, `%`, `#` y similares sin problema.
- Cada texto que dice `{"es": "...", "en": "..."}` tiene una versión por idioma. Si
  sólo quieres español, mira «Borrar o mantener las variantes» más abajo.

El significado de cada campo está en la siguiente sección. No dejes datos del
ejemplo: Alex Rivera es una persona ficticia.

### 2.3 Guarda

1. Arriba a la derecha pulsa el botón verde «Commit changes...» (el nombre puede
   variar: en archivos nuevos puede decir «Commit changes»).
2. En la ventana que aparece, deja marcada la opción «Commit directly to the main
   branch» (el nombre puede variar) y pulsa el botón verde «Commit changes».

Para corregir algo después: abre tu `cv.json`, pulsa el lápiz («Edit this file», arriba
a la derecha), cambia el texto y repite 2.3.

**Qué comprobar:** tu archivo aparece en `content/tu-nombre/cv.json` y, en la pestaña
«Actions», arranca una ejecución nueva.

## Paso 3. Descarga tus PDF

Cada vez que guardas un cambio, GitHub compila tus hojas de vida solo.

1. Entra a la pestaña «Actions», en la fila de pestañas de arriba de tu repositorio.
   Si GitHub muestra un aviso para activar los flujos de trabajo («workflows»),
   acéptalo (el nombre puede variar).
2. En la lista aparece una ejecución del flujo «CI», con el título del último cambio
   que guardaste. Un círculo amarillo significa que está corriendo; una palomita
   verde, que terminó bien; una equis roja, que falló. La primera vez puede tardar
   varios minutos, porque descarga el programa que arma los PDF. (No verificado: el
   tiempo depende de GitHub.)
3. Haz clic en el título de la ejecución. Verás tres trabajos: «Tests», «Privacidad»
   y «Hojas de vida». «Privacidad» sale como omitido en tu copia: es normal.
4. Baja hasta la sección «Artifacts», al final de la página. Haz clic en
   `hojas-de-vida`. Se descarga un archivo `.zip`.
5. Descomprímelo (en Windows: clic derecho, «Extraer todo»). Dentro hay una carpeta
   por cada persona de `content/` (la tuya y `example`) con los PDF en su subcarpeta
   `out`. Los nombres son `cv-<idioma>-<perfil>.pdf`, por ejemplo
   `cv-es-software-developer.pdf`. (No verificado: la estructura exacta del `.zip`
   puede variar.)

Los PDF quedan 30 días en GitHub. Pasado ese tiempo, para generarlos otra vez: pestaña
«Actions», clic en «CI» en la lista de la izquierda, botón «Run workflow» (el nombre
puede variar) y «Run workflow» de nuevo.

**Qué comprobar:** abre el PDF, lee todo con calma y revisa ortografía, fechas y
cifras. Antes de enviarlo, repasa la sección «Antes de enviar» de la
[guía de hoja de vida](hoja-de-vida-colombia.md).

## Qué significa cada campo

Los nombres de los campos van en inglés porque son los que lee el programa. El
contenido que escribes va en español.

| Campo | Qué es | Dónde sale en el PDF |
|---|---|---|
| `person.name` | Tu nombre | Encabezado |
| `person.location` | Ciudad y país, por ejemplo «Medellín, Colombia». Sin calle ni barrio | Debajo del nombre |
| `person.phone` | Un solo teléfono, el que contestas | Debajo del nombre |
| `person.email` | Un solo correo | Debajo del nombre, como enlace |
| `more.label` y `more.url` | Un enlace a tu portafolio o perfil, con el texto que se ve y la dirección | Pie de la página: «Conoce más sobre mí y mis proyectos» |
| `profiles` | Los perfiles que quieres mostrar. Cada uno tiene un nombre (por ejemplo `software-developer`) y tres campos: | |
| `profiles.<nombre>.title` | El cargo que buscas | Debajo del nombre |
| `profiles.<nombre>.summary` | Quién eres, qué sabes hacer y qué buscas, en 3 a 5 líneas | Sección «Perfil» |
| `profiles.<nombre>.keywords` | Las palabras clave de ese perfil: herramientas y temas. Deben aparecer escritas en el texto de tu hoja de vida | Metadatos del PDF; el ATS las busca |
| `experience` | Tus trabajos, del más reciente al más antiguo | Sección «Experiencia» |
| `experience[].role` | Tu cargo | Título de la entrada |
| `experience[].organization` | La organización | Debajo del cargo |
| `experience[].start`, `end` | Años o fechas, por ejemplo `"2021"`. Con `end` en `null`, sale «Presente» | A la derecha del cargo |
| `experience[].highlights` | Tus logros, uno por elemento. Mínimo uno. Estructura: situación, acción y resultado | Lista de viñetas |
| `skills` | Grupos de habilidades | Sección «Habilidades» |
| `skills[].label` | Nombre del grupo, por ejemplo «Herramientas» | En negrita |
| `skills[].items` | Las habilidades del grupo, separadas por comas, en un solo texto | Después del nombre del grupo |
| `education` | Estudios y cursos | Sección «Educación» |
| `education[].title` | Título o curso | Título de la entrada |
| `education[].organization` | Institución | Debajo del título |
| `education[].start`, `end` | Años; pueden ir en `null`. Con los dos en `null`, sale «Presente» | A la derecha |
| `education[].details` | Una descripción corta | Bajo la entrada |
| `variants` | Los PDF que se generan: cada elemento es un idioma (`es` o `en`) y un perfil de `profiles` | Un PDF por elemento |

`experience` y `education` aceptan además `subtitle`, un texto opcional que va después
de la organización.

Cómo se escriben los logros, con ejemplos antes y después, está en la
[guía de hoja de vida](hoja-de-vida-colombia.md#cómo-escribir-logros).

**Textos en dos idiomas.** Donde veas `{"es": "...", "en": "..."}`, escribes una
versión por idioma. Si un texto es igual en todos los idiomas (un nombre propio), basta
con una sola cadena: `"organization": "Freelance"`.

## Borrar o mantener las variantes

Cada línea de `variants` es un PDF. Ejemplo de la persona ficticia:

```json
"variants": [
  {"lang": "es", "profile": "software-developer"},
  {"lang": "en", "profile": "software-developer"},
  {"lang": "es", "profile": "frontend-developer"}
]
```

- **Para quitar un PDF,** borra su línea. Si borras la última, quita también la coma
  de la línea anterior.
- **Para quitar el inglés,** borra las líneas con `"lang": "en"`. Los textos en
  `"en"` pueden quedarse: no estorban.
- **Para un perfil nuevo,** agrega un bloque dentro de `profiles` con su nombre, y
  una línea en `variants` que lo use.
- **Para mantener una variante en inglés,** todo texto con `{"es": ..., "en": ...}`
  que use esa variante debe tener su versión en `"en"`. Si falta alguna, la ejecución
  sale en rojo y te dice cuál.

No borres la carpeta `content/example` ni cambies su `cv.json`: los tests de
Career Kit la usan, y si falta o cambia, el trabajo «Tests» sale en rojo. Que esté ahí
no te perjudica: sus PDF salen junto a los tuyos en el artefacto.

## Si la haces para otra persona

Si ayudas a un familiar o a un amigo, pídele permiso antes de guardar sus datos en tu
copia, dile dónde quedan y bórralos cuando ya no los necesite. Es su información, no
la tuya. Lo mejor es que cree su propia copia privada desde la plantilla.

## Si sale en rojo

Una equis roja no daña tu archivo: sólo te avisa que algo hay que corregir.

1. Pestaña «Actions» y clic en la ejecución que salió en rojo.
2. A la izquierda, clic en el trabajo «Hojas de vida».
3. Busca el paso con la equis roja y ábrelo con un clic. Lo que dice ese paso es la
   pista.

Tres casos:

### Un error de validación: dice el campo exacto

El paso «Compilar las hojas de vida» falla con un mensaje como:

```
Error: cv.json inválido:
  - experience[0].highlights.en: falta el texto en 'en' (variante en/software-developer)
```

Léelo así: `experience[0]` es la **primera** experiencia (se cuenta desde 0, así que la
segunda es `experience[1]`); `highlights.en` es el campo de logros en inglés. Aquí falta
la versión en inglés. Otros mensajes que puedes ver:

| Mensaje | Qué hacer |
|---|---|
| `person.phone: falta el campo` | Agrega el campo, con su nombre exacto y entre comillas |
| `person.email: debe ser una cadena no vacía` | El campo está vacío o no es texto entre comillas |
| `variants[1].profile: el perfil 'x' no existe en profiles` | Escribe el nombre de un perfil que exista en `profiles` |
| `experience[0].highlights: debe tener al menos un logro` | Agrega un logro |
| `... JSON inválido en la línea 12: Expecting ',' delimiter` | El archivo está mal escrito cerca de esa línea. Casi siempre falta una coma, una comilla o un corchete. El final del mensaje viene en inglés |

Corrige el archivo (lápiz, «Edit this file») y guarda con «Commit changes». Corre de nuevo.
Si hay varios errores, aparecen todos juntos en la lista.

### Una keyword faltante

El paso «Comprobar que un ATS puede leerlas» falla con un resultado como:

```
cv-es-software-developer: FALLA (2860 caracteres, 1 keywords faltantes)
  Keywords faltantes: Kubernetes
```

El PDF sí se generó y puedes descargarlo (Paso 3). Lo que pasa es que esa palabra está
en `keywords` de tu perfil pero no aparece escrita en el texto del PDF. La comprobación
no distingue mayúsculas ni tildes, pero busca la palabra completa. Dos salidas:

- Si de verdad tienes esa experiencia, escribe la palabra en tu resumen, en un logro o
  en tus habilidades.
- Si no la tienes, quítala de `keywords`.

Más sobre por qué las keywords deben ser reales:
[Keywords y ATS](hoja-de-vida-colombia.md#keywords-y-ats).

### El trabajo «Tests» o «Compilar» falla por otra razón

Si cambiaste archivos fuera de tu carpeta en `content/`, devuélvelos a como estaban. Si
el paso «Compilar las hojas de vida» muestra `Error: falló la compilación` y unas
líneas de LaTeX, copia ese texto y abre un «issue» en
<https://github.com/NeoBmo/Career-kit/issues>.

<!-- TODO: confirmar con el repo ya publicado que el botón «Use this template» existe (Settings > «Template repository» activado) y que el repositorio es público. -->
