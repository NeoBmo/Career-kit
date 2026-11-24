#!/usr/bin/env bash
# Uso:
#   ./scripts/build.sh                       -> compila todas las variantes en builds/
#   ./scripts/build.sh cv-es-software-developer  -> compila solo esa variante
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

OUT_DIR="builds/out"
mkdir -p "$OUT_DIR"

build_one () {
  local name="$1"
  echo "==> Compilando builds/${name}.tex"
  xelatex -interaction=nonstopmode -halt-on-error \
    -output-directory="$OUT_DIR" "builds/${name}.tex" > "$OUT_DIR/${name}.buildlog" 2>&1
  echo "    OK -> $OUT_DIR/${name}.pdf"
}

if [ "$#" -eq 0 ]; then
  for f in builds/*.tex; do
    name="$(basename "$f" .tex)"
    build_one "$name"
  done
else
  build_one "$1"
fi
