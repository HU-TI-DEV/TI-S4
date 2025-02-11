# Makefile in _slidev directory

# Filter out README.md from the list, in case you have one
MARKDOWN := $(filter-out README.md, $(wildcard *.md))

# Slidev command (unsetting DISPLAY for headless export)
SLIDEV := env -u DISPLAY bun --bun node_modules/.bin/slidev

# Default options for Slidev
SLIDEV_OPTIONS ?= \
	--with-toc \
	--timeout 60000

# Ghostscript settings for PDF optimization
GS_DEVICE ?= pdfwrite
GS_PROFILE ?= /ebook
GS_COMPAT ?= 1.4

# We create a list of pairs: "<mdfile>:<pdfpath>"
# from lines starting with `output:` in the frontmatter.
FILES = $(shell \
	for f in $(MARKDOWN); do \
	  OUT=$$(grep '^output:' $$f | cut -d ' ' -f 2); \
	  if [ -n "$$OUT" ]; then \
	    echo $$f:$$OUT; \
	  fi; \
	done \
)

# Extract just the PDF paths from those pairs
TARGETS = $(foreach pair,$(FILES),$(word 2,$(subst :, ,$(pair))))

# By default, make all PDFs
.PHONY: all
all: $(TARGETS)

###
# Next, we auto-generate a rule for each pair:  pdf-file : md-file (+ optional images)
# That way, `make path/to/file.pdf` is recognized by Make, and only rebuilds if needed.
###

define build_presentation
# Grab the two parts: $(1) -> .md file, $(2) -> .pdf output
$(2): $(1)
	@echo "Exporting $(1) -> $(2).temp.pdf"
	$(SLIDEV) export $(1) --output $(2).temp.pdf $(SLIDEV_OPTIONS)

	@echo "Optimizing PDF with Ghostscript..."
	gs -q \
	   -dNOPAUSE -dBATCH \
	   -sDEVICE=$(GS_DEVICE) \
	   -dPDFSETTINGS=$(GS_PROFILE) \
	   -dCompatibilityLevel=$(GS_COMPAT) \
	   -sOutputFile=$(2) \
	   $(2).temp.pdf

	rm -f $(2).temp.pdf
	@echo "Done -> $(2)\n"
endef

# Here we evaluate that rule for each pair
$(foreach pair,$(FILES),$(eval \
  $(call build_presentation,$(word 1,$(subst :, ,$(pair))),$(word 2,$(subst :, ,$(pair))))))

###
# (Optional) Clean target: remove all generated PDFs
###
.PHONY: clean
clean:
	rm -f $(TARGETS)
