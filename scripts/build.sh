#!/usr/bin/env bash
# Uso:
#   ./scripts/build.sh                    -> renderiza y compila content/example
#   ./scripts/build.sh content/<persona>  -> renderiza y compila esa persona
#
# Genera builds/<persona>/cv-<lang>-<profile>.tex y los PDF en builds/<persona>/out/.
# Usa xelatex local si existe; si no, el contenedor de TeX Live fijado por digest en
# scripts/texlive-image.txt, sin red.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PERSON_DIR="${1:-content/example}"
PERSON_DIR="${PERSON_DIR%/}"
TEX_DIR="builds/$(basename "$PERSON_DIR")"
OUT_DIR="$TEX_DIR/out"
IMAGE="$(tr -d '[:space:]' < scripts/texlive-image.txt)"

# Python: PYTHON si está definida; si no, el primero que de verdad se ejecute
# (en Windows `python3` puede ser un acceso directo de la tienda que no funciona).
find_python () {
  local candidate
  for candidate in ${PYTHON:-} python3 python py; do
    if "$candidate" -c "import sys" > /dev/null 2>&1; then
      echo "$candidate"
      return 0
    fi
  done
  echo "Error: no se encontró Python (prueba con PYTHON=/ruta/a/python)." >&2
  return 1
}

# Compilador: xelatex local o Docker. Sin ninguno de los dos no hay forma de compilar.
if command -v xelatex > /dev/null 2>&1; then
  ENGINE="local"
elif command -v docker > /dev/null 2>&1; then
  ENGINE="docker"
else
  echo "Error: no hay XeLaTeX ni Docker. Instala TeX Live (xelatex) o Docker Desktop." >&2
  exit 1
fi

run_xelatex () {
  local tex="$1"
  local args=(xelatex -interaction=nonstopmode -halt-on-error -output-directory="$OUT_DIR" "$tex")
  if [ "$ENGINE" = "local" ]; then
    "${args[@]}"
    return
  fi
  case "$(uname -s)" in
    MINGW*|MSYS*|CYGWIN*)
      # Git Bash reescribe los argumentos que parecen rutas (/work) y Docker
      # necesita la ruta de Windows para montar el volumen.
      MSYS_NO_PATHCONV=1 docker run --rm --network none \
        -v "$(cygpath -w "$PWD"):/work" -w /work "$IMAGE" "${args[@]}"
      ;;
    *)
      docker run --rm --user "$(id -u):$(id -g)" --network none -v "$PWD:/work" -w /work "$IMAGE" "${args[@]}"
      ;;
  esac
}

PY="$(find_python)"
echo "==> Renderizando $PERSON_DIR en $TEX_DIR"
# Se compilan sólo los .tex que acaba de escribir render (no restos de variantes viejas).
# tr quita el \r que añade Python en Windows al final de cada línea.
TEX_FILES="$("$PY" -m scripts.render "$PERSON_DIR" --out "$TEX_DIR" | tr -d '\r')"

mkdir -p "$OUT_DIR"
while IFS= read -r tex; do
  name="$(basename "$tex" .tex)"
  echo "==> Compilando $tex ($ENGINE)"
  if ! run_xelatex "$tex" > "$OUT_DIR/$name.buildlog" 2>&1; then
    echo "Error: falló la compilación de $tex. Últimas líneas de $OUT_DIR/$name.buildlog:" >&2
    tail -n 20 "$OUT_DIR/$name.buildlog" >&2
    exit 1
  fi
  echo "    OK -> $OUT_DIR/$name.pdf"
done <<< "$TEX_FILES"
