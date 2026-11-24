.PHONY: all build list clean

# Persona a compilar: make build PERSON=content/<persona>
PERSON ?= content/example

all: build

# Renderiza las variantes de cv.json y las compila (xelatex local o Docker).
build:
	@bash scripts/build.sh $(PERSON)

# Personas disponibles: cada carpeta de content/ con un cv.json.
list:
	@for f in content/*/cv.json; do dirname "$$f"; done

# Borra los .tex y PDF generados de la persona (se regeneran con make build).
clean:
	@test -n "$(notdir $(PERSON))" || { echo "Error: PERSON vacío"; exit 1; }
	@rm -rf "builds/$(notdir $(PERSON))"
