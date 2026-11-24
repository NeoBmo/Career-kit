.PHONY: all clean list

BUILDS_DIR := builds
OUT_DIR    := builds/out
LATEX      := latexmk -xelatex -interaction=nonstopmode -halt-on-error -outdir=$(OUT_DIR)

# Compila TODAS las variantes en builds/*.tex
all:
	@mkdir -p $(OUT_DIR)
	@for f in $(BUILDS_DIR)/*.tex; do \
		echo "==> Compilando $$f"; \
		$(LATEX) "$$f" || exit 1; \
	done

# Compila una sola variante: make build NAME=cv-es-software-developer
build:
	@mkdir -p $(OUT_DIR)
	$(LATEX) $(BUILDS_DIR)/$(NAME).tex

list:
	@ls $(BUILDS_DIR)/*.tex | sed 's|.*/||; s|\.tex||'

clean:
	@rm -rf $(OUT_DIR)
	@find . -name "*.aux" -o -name "*.log" -o -name "*.fls" -o -name "*.fdb_latexmk" -o -name "*.out" | xargs -r rm -f
