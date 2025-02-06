# Zoek alle markdown presentaties in de huidige map
MARKDOWN := $(filter-out README.md, $(wildcard *.md))

# Zorg ervoor dat slidev is geïnstalleerd in path
# Er is een bug met playwright headless & WSL2, dat is waarom we DISPLAY unsetten
# Dat kostte me maar een paar uur om te vinden.
SLIDEV := env -u DISPLAY slidev
SLIDEV_OPTIONS ?= \
	--with-toc

# Genereer een lijst van <input.md>:<output.pdf> paren
# We gebruiken grep om de regel met 'output:' op te halen, en cut voor het pad.
# Formaat: "les-foo.md:./programma/les-foo.pdf"
FILES = $(shell \
	for f in $(MARKDOWN); do \
	  OUT=$$(grep '^output:' $$f | cut -d ' ' -f 2); \
	  if [ -n "$$OUT" ]; then \
	    echo $$f:$$OUT; \
	  fi; \
	done \
)

# Hier extraheren we de output-paden als losse targets
TARGETS = $(foreach pair,$(FILES),$(word 2,$(subst :, ,$(pair))))

.PHONY: all
all: $(TARGETS)

# Automatisch een recipe genereren voor elk (md,output)-paar
# $(word 1,...) is het .md-bestand, $(word 2,...) is het output-pad
# We roepen 'slidev export' aan met $(SLIDEV_OPTIONS).
define build_presentation
$(2): $(1)
	@echo "Exporting $(1) to $(2) (intermediate: $(2).temp.pdf)"
	$(SLIDEV) export $(1) --output $(2).temp.pdf $(SLIDEV_OPTIONS)
	@echo "Optimising PDF with Ghostscript..."
	gs -q \
	   -dNOPAUSE -dBATCH \
	   -sDEVICE=pdfwrite \
	   -dPDFSETTINGS=/ebook \
	   -dCompatibilityLevel=1.4 \
	   -sOutputFile=$(2) \
	   $(2).temp.pdf
	@rm -f $(2).temp.pdf
	@echo "Done -> $(2)"
endef

# Voor elke entry in FILES maken we een rule
$(foreach pair,$(FILES),$(eval $(call build_presentation,$(word 1,$(subst :, ,$(pair))),$(word 2,$(subst :, ,$(pair))))))

# Optioneel: opruimen van de gegenereerde bestanden
.PHONY: clean
clean:
	rm -f $(TARGETS)
