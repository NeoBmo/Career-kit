# Guía paso a paso: tu hoja de vida en PDF, sin instalar nada

Esta guía es para quien no programa. Vas a crear tu propia copia de Career Kit en
GitHub, escribir tus datos en un archivo y descargar tus hojas de vida en PDF. Todo
se hace desde el navegador.

> **Estado al 2026-11-24: la plantilla todavía no está publicada.** Se publicará
> cuando la integración continua (CI) se haya probado en GitHub. Hasta entonces el
> botón «Use this template» de los pasos 1 a 3 no existe y esos pasos no funcionan.
> Mientras tanto, el camino es compilar en tu equipo: mira la sección
> [En tu equipo](../README.md#en-tu-equipo) del README. Necesita Python y Docker, así
> que es más técnico.

## Glosario

| Palabra | Qué es |
|---|---|
| Repositorio | Una carpeta de proyecto que vive en GitHub, con todos sus archivos |
| Commit | Guardar un cambio en el repositorio. Queda registrado con su fecha |
| Actions | La pestaña de GitHub donde un programa compila tus PDF cada vez que guardas |
| Artefacto | El archivo `.zip` con los PDF que deja una ejecución de Actions |
| Issue | Un mensaje público en el repositorio de Career Kit para reportar un problema |
| JSON | El formato de texto en que escribes tus datos (mira «Qué es JSON» más abajo) |
| ATS | El sistema que usan las empresas para filtrar hojas de vida leyendo su texto |

## Qué necesitas

- Un computador. Se puede hacer desde el celular, pero es incómodo: el editor de
  archivos es pequeño y es fácil dañar el JSON.
- Una cuenta de GitHub (es gratis). Si no la tienes, es el paso 0.
- Tus datos a la mano: experiencia, estudios y habilidades. Si dudas de qué poner o
  qué dejar fuera, lee antes la [guía de hoja de vida para Colombia](hoja-de-vida-colombia.md).

Los nombres de los botones de GitHub se escriben aquí en inglés, entre comillas. Si
tu GitHub está en otro idioma, o si GitHub cambia un botón, busca el equivalente. Donde
no estamos seguros del nombre exacto, lo decimos.

En esta guía, `content/<tu-nombre>/` significa una carpeta con tu nombre, por ejemplo
`content/maria-gomez/`.

## Paso 0. Crea tu cuenta de GitHub

1. Entra a <https://github.com/signup>.
2. Escribe tu correo, una contraseña y un nombre de usuario. Sigue los pasos que te pide.
3. GitHub te enviará un código al correo. Escríbelo para confirmar la cuenta.
4. GitHub puede pedirte además una verificación en dos pasos (un código extra desde una
   aplicación o por mensaje). Hazla: protege tu cuenta, y en ella van a estar tus datos.

**Qué comprobar:** puedes iniciar sesión en <https://github.com> y ves tu página de inicio.

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
5. **Comprueba que dice Private.** Arriba del nombre de tu copia debe aparecer la
   etiqueta «Private». Si dice «Public», cámbiala: pestaña «Settings» → «General» →
   baja hasta «Danger Zone» → «Change visibility» → «Make private» (el nombre puede
   variar).

### Qué significa «privada» (y qué no)

Tu `cv.json` va a llevar tu teléfono, tu correo y tu historial de trabajo.

- En un repositorio **público** cualquiera puede leerlo, y los buscadores y los
  programas que recorren GitHub también.
- En uno **privado** lo ve quien tenga acceso: tú y las personas que invites. No es
  «sólo tú» si le das acceso a alguien.
- Aun privado, vive en los servidores de GitHub, que están fuera de Colombia. Si no
  quieres eso, trabaja en tu equipo: mira [Si prefieres no subir tu hoja de vida](#si-prefieres-no-subir-tu-hoja-de-vida).
- Si tu copia es pública, el trabajo «Copia pública» de la CI sale en **rojo** y el
  mensaje te dice cómo volverla privada. Un rojo en ese trabajo no es un error de tu
  `cv.json`: es el aviso de que cualquiera puede ver tu hoja de vida.

**Borrar un dato no lo borra del todo.** Si quitas tu teléfono de `cv.json`, la versión
anterior sigue en el historial de commits de tu copia, y los PDF viejos siguen en los
artefactos, que GitHub guarda 30 días. Si necesitas que desaparezca de verdad, borra
la copia entera: «Settings» → «General» → «Danger Zone» → «Delete this repository» (el
nombre puede variar). Eso elimina el historial. Los artefactos de ese repositorio
también deberían desaparecer con él (no verificado). Luego crea una copia nueva desde la
plantilla.

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

**Qué es JSON.** Es un formato de texto para guardar datos con orden. Cada dato tiene
un nombre y un valor: `"name": "Ana Pérez"`. Los textos van entre comillas dobles, los
datos de una lista van entre corchetes `[ ]` y los grupos de datos entre llaves `{ }`.
Es estricto: un solo símbolo mal puesto y el programa no entiende el archivo.

Con el archivo abierto en el editor, cambia el contenido del ejemplo por el tuyo.
Reglas para no romper el archivo:

- Cada texto va entre comillas dobles `"..."`. Si necesitas unas comillas dentro del
  texto, escríbelas como `\"`.
- Entre un elemento y el siguiente va una coma. El último de una lista no lleva coma.
- No cambies los nombres de los campos (`person`, `experience`...), sólo lo que va a
  su derecha, entre comillas.
- Cada texto va en una sola línea. No pulses Enter dentro de un texto: el PDF ajusta
  las líneas solo.
- Los años van entre comillas: `"2021"`, no `2021`.
- Puedes escribir `&`, `%`, `#` y similares sin problema.
- Cada texto que dice `{"es": "...", "en": "..."}` tiene una versión por idioma. Si
  sólo quieres español, mira «Borrar o mantener las variantes» más abajo.

El significado de cada campo está en la sección [Qué significa cada campo](#qué-significa-cada-campo).
No dejes datos del ejemplo: Alex Rivera es una persona ficticia.

#### Errores que vas a cometer

Los mensajes aparecen en la pestaña «Actions» (mira [Si sale en rojo](#si-sale-en-rojo)).

| Error | Cómo se ve en el archivo | Mensaje |
|---|---|---|
| Falta la comilla de apertura | `"name": Ana Pérez",` | `JSON inválido en la línea 3: Expecting value` |
| Falta la comilla de cierre | `"name": "Ana Pérez,` | `JSON inválido en la línea 3: Invalid control character at` |
| Coma de más al final de un grupo | `"email": "ana@example.com",` y luego `}` | `JSON inválido en la línea 6: Expecting property name enclosed in double quotes` |
| Coma de más al final de una lista | `"es": ["Git", "SQL",]` | `JSON inválido en la línea 12: Expecting value` |
| Falta una coma entre dos elementos | `"phone": "+00 000 000 0000"` y en la línea siguiente `"email": ...` | `JSON inválido en la línea 5: Expecting ',' delimiter` |
| Un Enter dentro de un texto | El texto se parte en dos líneas | `JSON inválido en la línea 8: Invalid control character at` |
| Un año sin comillas | `"start": 2021,` | `experience[0].start: debe ser una cadena no vacía o null` |

Cómo leerlos:

- Los seis primeros son errores de sintaxis. El mensaje empieza con la ruta del
  archivo (por ejemplo `content/ana-perez/cv.json: JSON inválido en la línea 3:`) y
  termina en inglés. La línea que da es donde el programa se dio cuenta, que a veces es
  la siguiente a la del error real: mira también la línea de arriba.
- **Un error de sintaxis muestra sólo el primero.** Corrígelo, guarda y espera la
  ejecución nueva: puede salir otro. Los errores de datos (el último de la tabla)
  salen todos juntos, pero sólo después de que la sintaxis esté bien.
- Los mensajes de la tabla son los de GitHub Actions. Si compilas en tu equipo con
  Python 3.13 o más nuevo, la coma de más dice `Illegal trailing comma before end of
  object` (o `end of array`). Significa lo mismo: quita esa coma.
- Los mensajes de sintaxis salen del módulo `json` de Python; los de datos, de
  `scripts/cv_model.py`. Los de sintaxis de esta tabla no los ejecutamos: son los que
  el módulo da para esos casos.

### 2.3 Quita o adapta el perfil del ejemplo

El ejemplo trae dos perfiles. Si dejas el segundo, saldrá un PDF con un texto de
presentación que no es tuyo. Haz esto:

1. Dentro de `profiles`, busca el bloque `frontend-developer`. Empieza en la línea
   `"frontend-developer": {` y termina en su llave `}` de cierre.
2. Borra ese bloque entero. Después borra la coma que quedó al final del bloque
   anterior (`software-developer`), porque ahora es el último:

   ```json
   "profiles": {
     "software-developer": {
       ...
     }
   }
   ```

3. En `variants`, borra la línea que lo usa:

   ```json
   {"lang": "es", "profile": "frontend-developer"}
   ```

   Si esa era la última línea de la lista, quita también la coma de la línea de arriba.
4. Cambia el bloque `software-developer` por el tuyo: el cargo (`title`), el resumen
   (`summary`) y las palabras clave (`keywords`). Si cambias el nombre del perfil, cámbialo
   igual en las líneas de `variants`. Los nombres de perfil sólo admiten minúsculas,
   números y guiones (`desarrollo-web`, no `Desarrollo Web`).

Si prefieres quedarte con `frontend-developer`, haz lo mismo al revés: borra el otro
bloque y su línea en `variants`, y adapta el que queda.

### 2.4 Guarda

1. Arriba a la derecha pulsa el botón verde «Commit changes...» (el nombre puede
   variar: en archivos nuevos puede decir «Commit changes»).
2. En la ventana que aparece, deja marcada la opción «Commit directly to the main
   branch» (el nombre puede variar) y pulsa el botón verde «Commit changes».

Para corregir algo después: abre tu `cv.json`, pulsa el lápiz («Edit this file», arriba
a la derecha), cambia el texto y repite 2.4.

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
3. Haz clic en el título de la ejecución. Verás cuatro trabajos: «Tests», «Privacidad»,
   «Copia pública» y «Hojas de vida». «Privacidad» sale como omitido en tu copia: es
   normal. «Copia pública» debe salir en verde; si sale en rojo, tu copia es pública
   (mira el paso 1).
4. Baja hasta la sección «Artifacts», al final de la página. Haz clic en
   `hojas-de-vida`. Se descarga un archivo `.zip`.
5. Descomprímelo (en Windows: clic derecho, «Extraer todo»). Dentro hay una carpeta
   por cada persona de `content/`, con los PDF en su subcarpeta `out`. Los tuyos están
   en la carpeta con tu nombre. La carpeta `example` es la de Alex Rivera, la persona
   ficticia: no es tuya y no la envíes. Los nombres son `cv-<idioma>-<perfil>.pdf`, por
   ejemplo `cv-es-software-developer.pdf`. (No verificado: la estructura exacta del
   `.zip` puede variar.)

Los PDF quedan 30 días en GitHub. Pasado ese tiempo, para generarlos otra vez: pestaña
«Actions», clic en «CI» en la lista de la izquierda, botón «Run workflow» (el nombre
puede variar) y «Run workflow» de nuevo.

**Qué comprobar:** abre el PDF, lee todo con calma y revisa ortografía, fechas y
cifras. Antes de enviarlo, repasa la sección «Antes de enviar» de la
[guía de hoja de vida](hoja-de-vida-colombia.md).

## Si prefieres no subir tu hoja de vida

`content/private/` es la carpeta para quien trabaja **en su equipo** y no quiere subir
su hoja de vida a ningún lado: git la ignora y GitHub no la compila. Sirve con los
comandos del [README](../README.md#en-tu-equipo).

En una copia privada de la plantilla es al revés: tu carpeta lleva tu nombre
(`content/maria-gomez/`) y **sí se sube** a tu copia, porque es lo que la CI necesita
para darte los PDF. Por eso la copia debe ser privada.

## Qué significa cada campo

Los nombres de los campos van en inglés porque son los que lee el programa. El
contenido que escribes va en español.

| Campo | Qué es | Dónde sale en el PDF |
|---|---|---|
| `person.name` | Tu nombre | Encabezado |
| `person.location` | Ciudad y país, por ejemplo «Medellín, Colombia». Sin calle ni barrio | Debajo del nombre |
| `person.phone` | Un solo teléfono, el que contestas | Debajo del nombre |
| `person.email` | Un solo correo | Debajo del nombre, como enlace |
| `more.label` y `more.url` | Opcional. Un enlace a tu portafolio o perfil: `label` es el texto que se ve y `url`, la dirección | Pie de la página |
| `profiles` | Los perfiles que quieres mostrar. Cada uno tiene un nombre (por ejemplo `software-developer`) y tres campos: | |
| `profiles.<nombre>.title` | El cargo que buscas | Debajo del nombre |
| `profiles.<nombre>.summary` | Quién eres, qué sabes hacer y qué buscas, en 3 a 5 líneas | Sección «Perfil» |
| `profiles.<nombre>.keywords` | Las palabras clave de ese perfil: herramientas y temas. Deben aparecer escritas en el texto de tu hoja de vida | Metadatos del PDF; el ATS las busca |
| `experience` | Tus trabajos, del más reciente al más antiguo. Puede ir vacía: `[]` | Sección «Experiencia» |
| `experience[].role` | Tu cargo | Título de la entrada |
| `experience[].organization` | La organización | Debajo del cargo |
| `experience[].start`, `end` | Años o fechas, siempre entre comillas, por ejemplo `"2021"`. Con `end` en `null`, sale «Presente» | A la derecha del cargo |
| `experience[].highlights` | Tus logros, uno por elemento. Mínimo uno. Estructura: situación, acción y resultado | Lista de viñetas |
| `skills` | Grupos de habilidades | Sección «Habilidades» |
| `skills[].label` | Nombre del grupo, por ejemplo «Herramientas» | En negrita |
| `skills[].items` | Las habilidades del grupo, separadas por comas, en un solo texto | Después del nombre del grupo |
| `education` | Estudios y cursos | Sección «Educación» |
| `education[].title` | Título o curso | Título de la entrada |
| `education[].organization` | Institución | Debajo del título |
| `education[].start`, `end` | Años; pueden ir en `null`. Con los dos en `null`, sale «Presente» | A la derecha |
| `education[].details` | Una descripción corta. **Obligatorio** en cada estudio que pongas | Bajo la entrada |
| `variants` | Los PDF que se generan: cada elemento es un idioma (`es` o `en`) y un perfil de `profiles` | Un PDF por elemento |

`experience` y `education` aceptan además `subtitle`, un texto opcional que va después
de la organización.

Cómo se escriben los logros, con ejemplos antes y después, está en la
[guía de hoja de vida](hoja-de-vida-colombia.md#cómo-escribir-logros).

**Textos en dos idiomas.** Donde veas `{"es": "...", "en": "..."}`, escribes una
versión por idioma. Si un texto es igual en todos los idiomas (un nombre propio), basta
con una sola cadena: `"organization": "Freelance"`.

## El pie «more»

`more` es opcional. Pon ahí un enlace que lleve a más información tuya:

- tu perfil de LinkedIn,
- tu GitHub,
- un portafolio, o
- una carpeta de Drive con permiso de lectura para quien tenga el enlace.

```json
"more": {"label": "linkedin.com/in/tu-usuario", "url": "https://www.linkedin.com/in/tu-usuario"}
```

La frase del pie («Conoce más sobre mí y mis proyectos») la pone la plantilla.
`label` es sólo el texto del enlace.

Si no tienes nada que enlazar, **borra el bloque `more` entero** (la línea que empieza
con `"more":`). No saldrá el pie. Cuida la coma de la línea de arriba o de abajo para
que no queden dos seguidas ni una sobrando.

## Si no tienes experiencia

Es normal en un primer empleo. Puedes dejar la lista vacía:

```json
"experience": [],
```

La sección «Experiencia» no se imprime, ni su título. Para que la hoja no quede floja,
refuerza lo demás:

- **Educación:** pon tus estudios y cursos, y cuenta en `details` un proyecto o un
  trabajo de grado. `education[].details` es obligatorio cuando hay educación.
- **Proyectos:** ponlos como una entrada de `education` (un curso con proyecto) o en tu
  resumen.
- **Trabajo informal o voluntario:** cuenta como experiencia. Ponlo en `experience`
  con la organización real (una junta de acción comunal, el negocio familiar, una
  fundación) y un logro.

Un logro de ejemplo, de trabajo informal:

```json
"highlights": {
  "es": ["El negocio familiar perdía pedidos porque los anotaba en cuadernos; armé una hoja de cálculo compartida y los pedidos dejaron de repetirse o perderse."]
}
```

Más sobre cómo escribirlo: [cómo escribir logros](hoja-de-vida-colombia.md#cómo-escribir-logros).

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
no te perjudica: sus PDF salen en el artefacto, en su propia carpeta `example`.

## Si la haces para otra persona

Si ayudas a un familiar o a un amigo, pídele permiso antes de guardar sus datos en tu
copia, dile dónde quedan y bórralos cuando ya no los necesite. Es su información, no
la tuya. Lo mejor es que cree su propia copia privada desde la plantilla.

## Si sale en rojo

Una equis roja no daña tu archivo: sólo te avisa que algo hay que corregir.

1. Pestaña «Actions» y clic en la ejecución que salió en rojo.
2. A la izquierda, clic en el trabajo que salió en rojo (por ejemplo «Hojas de vida»).
3. Busca el paso con la equis roja y ábrelo con un clic. Lo que dice ese paso es la
   pista.

**Antes de pedir ayuda:** no pegues tu `cv.json` ni el registro completo en un issue
público si tiene datos tuyos (teléfono, correo, empresas). Los issues los lee todo el
mundo. Copia sólo la línea del error, sin datos personales. Si el error trae un dato
tuyo (un nombre de carpeta, un correo), reemplázalo por `...`.

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
| `experience[0].start: debe ser una cadena no vacía o null` | El año va entre comillas: `"2021"` |
| `education[0].details: falta el campo` | Cada estudio necesita `details`, una descripción corta |
| `variants[1].profile: el perfil 'x' no existe en profiles` | Escribe el nombre de un perfil que exista en `profiles` |
| `profiles.Mi Perfil: sólo admite minúsculas, números y guiones (^[a-z0-9-]+$)` | Renombra el perfil, por ejemplo `mi-perfil`, y cámbialo también en `variants` |
| `experience[0].highlights: debe tener al menos un logro` | Agrega un logro |
| `... JSON inválido en la línea 12: Expecting ',' delimiter` | El archivo está mal escrito cerca de esa línea. Mira la tabla de [errores que vas a cometer](#errores-que-vas-a-cometer) |

Corrige el archivo (lápiz, «Edit this file») y guarda con «Commit changes». Corre de nuevo.
Si hay varios errores de datos, aparecen todos juntos en la lista. Los de sintaxis salen
de uno en uno.

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

Esa misma comprobación también verifica que las secciones salgan en su orden. Si falla,
dice `Las secciones no aparecen en el orden esperado: el texto está desordenado.` Eso no
lo causa tu `cv.json`: es un problema del PDF. Abre un issue con esa línea.

Más sobre por qué las keywords deben ser reales:
[Keywords y ATS](hoja-de-vida-colombia.md#keywords-y-ats).

### El trabajo «Tests» o «Compilar» falla por otra razón

Si cambiaste archivos fuera de tu carpeta en `content/`, devuélvelos a como estaban. Si
el paso «Compilar las hojas de vida» muestra `Error: falló la compilación` y unas
líneas de LaTeX, copia sólo las líneas del error (sin datos tuyos) y abre un «issue» en
<https://github.com/NeoBmo/Career-kit/issues>.

### Cómo deshacer un cambio

Si un cambio rompió tu archivo y no sabes dónde:

1. Abre tu `cv.json` y pulsa «History» (arriba a la derecha del archivo; el nombre
   puede variar). Verás la lista de commits del archivo.
2. Abre el último commit que sabes que funcionaba.
3. Ve a esa versión del archivo: menú de los tres puntos «...» → «View file» (el nombre
   puede variar).
4. Pulsa «Copy raw file», vuelve a tu `cv.json` actual, pulsa el lápiz, selecciona todo
   (Ctrl+A), pega (Ctrl+V) y guarda con «Commit changes».

En algunos commits GitHub ofrece un botón «Revert» que lo hace por ti. No siempre
aparece: si no lo ves, usa la copia de arriba.
