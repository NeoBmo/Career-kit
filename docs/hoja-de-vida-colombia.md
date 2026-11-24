# Guía de hoja de vida para Colombia

> Esta es una guía práctica, no asesoría legal. Las normas se citan para que sepas
> de dónde sale cada recomendación. Si tienes una duda jurídica concreta, consulta
> a una persona abogada. Normas revisadas por última vez el 2026-11-22.

Una hoja de vida circula sin control: la reenvían, la guardan en carpetas
compartidas y la leen personas que no conoces. Por eso conviene que lleve lo que
sirve para que te llamen y nada más. Esta guía te dice qué poner, qué dejar fuera
y cómo escribirla para que la lea una persona y también un ATS (el sistema que
filtra hojas de vida de forma automática).

## Qué datos sí poner

| Dato | Cómo ponerlo |
|---|---|
| Nombre | El que usas en tu vida profesional: «Alex Rivera». |
| Ciudad | Sólo ciudad y país: «Medellín, Colombia». Sin calle ni barrio. |
| Teléfono | Uno solo, el que contestas. |
| Correo | Uno solo, con una dirección seria (nombre y apellido, sin apodos). |
| Perfil | 3 a 5 líneas: quién eres, qué sabes hacer y qué buscas. |
| Experiencia | Cargo, organización, años y logros (ver más abajo). |
| Habilidades | Las que usas de verdad, agrupadas por tema. |
| Educación | Título, institución y años. Cursos si son relevantes para la vacante. |

Con eso una empresa tiene cómo contactarte y cómo juzgar si encajas. La dirección
exacta, si algún día hace falta, se pide más adelante, cuando la oferta ya va en
serio.

En Career Kit estos datos van en tu `cv.json`, en los campos `person`, `profiles`,
`experience`, `skills` y `education`. Puedes ver un ejemplo completo en
`content/example/cv.json`.

## Qué datos no hacen falta, y por qué

No pongas en tu hoja de vida:

- número de cédula;
- foto;
- fecha de nacimiento o edad;
- estado civil;
- dirección de residencia;
- religión;
- información de salud;
- referencias personales con sus teléfonos.

### Por qué

1. **Exponen datos en un documento sin control.** Cada copia de tu hoja de vida
   puede acabar en un correo reenviado, una carpeta compartida o un sistema que no
   conoces. Un teléfono ajeno en una referencia, o tu cédula, quedan expuestos allí.
2. **Algunos datos son sensibles.** La ley colombiana trata aparte los datos
   sensibles: nadie está obligado a responder sobre ellos y ninguna actividad
   puede condicionarse a entregarlos (ver «Qué dice la ley»). Datos como tu
   religión o tu salud no ayudan a que te contraten y sí te exponen.
3. **Pueden llevar a filtrar por lo que no importa.** Con tu edad, tu foto o tu
   estado civil, alguien puede descartarte por aspecto, edad o situación familiar
   antes de leer qué sabes hacer. Si no están, no pueden pesar.
4. **Las referencias no son tuyas solas.** El teléfono de otra persona es un dato
   personal suyo. Escribe «Referencias disponibles a solicitud» o, mejor, no pongas
   nada y ofrécelas cuando te las pidan, avisando antes a cada persona.

### Qué dice la ley

La Ley 1581 de 2012 (habeas data) regula cómo se tratan los datos personales en
Colombia. Para esta guía importan tres ideas, todas de la fuente oficial:

- **Finalidad.** El tratamiento de datos responde a una finalidad informada
  (Ley 1581, art. 4). Una hoja de vida existe para evaluar tu candidatura; datos
  que no sirven para eso no tienen razón de estar ahí.
- **Autorización.** Para tratar tus datos, quien los recibe necesita tu
  autorización previa, expresa e informada, y el silencio no cuenta como
  autorización (Ley 1581, arts. 3 y 9; Decreto 1074 de 2015, art. 2.2.2.25.2.4).
- **Datos sensibles.** Responder sobre ellos es opcional, y ninguna actividad se
  condiciona a entregarlos (Ley 1581, art. 12 y Decreto 1074 de 2015,
  art. 2.2.2.25.2.2 a 2.2.2.25.2.4).

Fuentes oficiales:

- Ley 1581 de 2012: <http://www.secretariasenado.gov.co/senado/basedoc/ley_1581_2012.html>
  y <https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=76608>
- Decreto 1074 de 2015 (reglamenta la ley):
  <https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=53646>

### Poner foto o cédula no es ilegal

Esto es una recomendación, no una prohibición. Si quieres poner una foto, puedes.
Y algunas convocatorias piden datos concretos: las del sector público, ciertos
formatos o procesos de selección con formulario propio. Cuando la convocatoria
pida un dato, **sigue la convocatoria**. Entrega lo que piden, en el formato que
piden, y nada más.

## Cómo escribir logros

Una lista de tareas dice lo que te tocaba hacer. Un logro dice qué cambió gracias
a ti. Usa esta estructura, en una o dos frases:

**situación → acción → resultado**

1. **Situación:** qué problema había.
2. **Acción:** qué hiciste tú, con verbo en pasado.
3. **Resultado:** qué mejoró, con cifras si las tienes (tiempo, dinero, porcentaje,
   cantidad). Si no tienes un número exacto, usa una aproximación honesta
   («cerca de», «unas cuatro horas»).

### Ejemplo 1: auxiliar contable

- **Antes:** «Encargada de conciliaciones bancarias y causación de facturas.»
- **Después:** «Las conciliaciones bancarias se entregaban con cinco días de
  retraso; armé una plantilla de control y un calendario semanal, y el cierre
  mensual pasó de ocho a tres días.»

### Ejemplo 2: persona de ventas

- **Antes:** «Atención a clientes y venta de productos en el punto de venta.»
- **Después:** «Los clientes de una ferretería preguntaban por productos que no
  teníamos y se iban; llevé un registro de esas solicitudes, propuse pedirlos al
  proveedor y las ventas de la sección subieron un 15 % en tres meses.»

Si no encuentras la cifra, pregúntate: ¿cuánto tiempo ahorré?, ¿cuántas personas
atendí?, ¿qué error dejó de pasar? En `content/example/cv.json` tienes más
ejemplos de logros con este formato.

## Keywords y ATS

Muchas empresas pasan las hojas de vida por un ATS, que busca en el texto las
palabras de la vacante. Para que te encuentre:

1. Lee la vacante y subraya los términos que describen lo que pide: herramientas,
   funciones, títulos.
2. Copia, con las mismas palabras de la vacante, **sólo los que describen tu
   experiencia real**. Si la vacante dice «conciliaciones bancarias» y tú las
   hiciste, escribe «conciliaciones bancarias», no «cuadre de cuentas».
3. No rellenes con palabras que no puedas sostener en una entrevista. Si te
   preguntan por ellas y no sabes responder, pierdes más de lo que ganaste.
4. Ponlas en su lugar natural: en el perfil, los logros y las habilidades.
   No las escondas en texto blanco ni en listas sin contexto: la persona que
   lee lo notará.

Para comprobar que tu PDF se lee bien, ejecuta
`py -m scripts.ats_check Tu-PDF.pdf --keywords "palabra uno, palabra dos"`. Te dice
cuántos caracteres extrae y qué keywords no aparecen (necesita `pdftotext`).

## Antes de enviar

1. **Revisa la ortografía.** Lee el texto en voz alta y pásalo por un corrector.
   Revisa nombres propios, tildes, fechas y cifras.
2. **Exporta en PDF.** Es el formato que se ve igual en cualquier equipo.
3. **Nombra el archivo** `Nombre-Apellido-Cargo.pdf`, por ejemplo
   `Alex-Rivera-Desarrolladora-Frontend.pdf`.
4. **Envía la versión adaptada a esa vacante**, no una genérica. Ajusta el perfil
   y las keywords a lo que pide cada oferta.
5. **Comprueba que no quedó ningún dato de la lista de «no hacen falta»**, salvo
   que la convocatoria lo pida.

## Fuentes y qué no se afirma

Las normas de esta guía se contrastaron con su texto oficial el 2026-11-22. La
guía no dice cuáles son exactamente los datos sensibles según la ley, ni cita
artículos que no se hayan podido comprobar. Para eso, consulta el texto de la
Ley 1581 de 2012 en los enlaces de arriba o pregunta a una persona abogada.
