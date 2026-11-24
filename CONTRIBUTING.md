# Cómo contribuir

Gracias por querer mejorar Career Kit.

## Proponer cambios

- Si el cambio es grande (una función nueva, un cambio en el formato de `cv.json`, otro
  diseño), abre primero un issue y cuéntalo. Así evitas trabajar en algo que no
  encaje.
- Si es pequeño (una errata, un fallo claro), puedes ir directo al pull request.
- Haz el cambio en una rama propia y abre el pull request con una descripción que se
  entienda sin abrir el código.

## Antes de abrir el pull request

Desde la raíz del repo (en macOS y Linux, `python3` en lugar de `py`):

| Comando | Qué hace |
|---|---|
| `py -m unittest discover -s tests` | Corre los tests |
| `py -m scripts.privacy_check` | Busca correos y teléfonos reales en los archivos versionados |

`privacy_check` sólo revisa lo que git versiona: añade tus archivos nuevos con
`git add` antes de correrlo.

## Nunca subas datos reales

Ni tuyos ni de otra persona: teléfonos, correos, ubicaciones, enlaces personales o
empresas reales. En ejemplos, tests y documentación usa `+00 000 000 0000` y
`example.com`. La persona de `content/example/` es ficticia; tu hoja de vida real va en
`content/private/`, que git ignora.

La comprobación de privacidad falla con cualquier correo que no sea de `example.com` ni
contenga `noreply`, y con cualquier teléfono de 10 o más dígitos distinto del ficticio.

## Idioma

- El código va en inglés: nombres de variables, funciones, archivos y ramas.
- La documentación va en español: README, guías, comentarios, y los mensajes y errores
  que ve la persona usuaria.
