# Makefile for LaTeX documents

LATEX=latexmk
BIBTEX=biber
LATEX_FLAGS=-xelatex -shell-escape -synctex=1 -interaction=nonstopmode

SOURCE=Main.tex
PDF=$(SOURCE:.tex=.pdf)

GERMAN_OUT_DIR=Output/German
ENGLISH_OUT_DIR=Output/English

GERMAN_BUILD_DIR=Build/German
ENGLISH_BUILD_DIR=Build/English

GERMAN_PDF_SOURCE=$(GERMAN_BUILD_DIR)/$(PDF)
ENGLISH_PDF_SOURCE=$(ENGLISH_BUILD_DIR)/$(PDF)

GERMAN_PDF_TARGET=$(GERMAN_OUT_DIR)/$(PDF)
ENGLISH_PDF_TARGET=$(ENGLISH_OUT_DIR)/$(PDF)

all: compile
	xdg-open $(GERMAN_PDF_TARGET)
	xdg-open $(ENGLISH_PDF_TARGET)

compile: german english

clean:
	git clean -dfX

german:
# If not Exists, create 'Build' directory
	[ -d $(GERMAN_BUILD_DIR) ] || mkdir -p $(GERMAN_BUILD_DIR)
# Build the document
	$(LATEX) $(LATEX_FLAGS) -output-directory=$(GERMAN_BUILD_DIR) -pretex="\newcommand{\lang}{de}" -usepretex $(SOURCE)
# If not Exists, create 'Output/German' directory
	[ -d $(GERMAN_OUT_DIR) ] || mkdir -p $(GERMAN_OUT_DIR)
# Copy the PDF to the 'Output/German' directory
	cp $(GERMAN_PDF_SOURCE) $(GERMAN_PDF_TARGET)

english:
# If not Exists, create 'Build' directory
	[ -d $(ENGLISH_BUILD_DIR) ] || mkdir -p $(ENGLISH_BUILD_DIR)
# Build the document
	$(LATEX) $(LATEX_FLAGS) -output-directory=$(ENGLISH_BUILD_DIR) -pretex="\newcommand{\lang}{en}" -usepretex $(SOURCE)
# If not Exists, create 'Output/English' directory
	[ -d $(ENGLISH_OUT_DIR) ] || mkdir -p $(ENGLISH_OUT_DIR)
# Copy the PDF to the 'Output/English' directory
	cp $(ENGLISH_PDF_SOURCE) $(ENGLISH_PDF_TARGET)

.PHONY: all clean