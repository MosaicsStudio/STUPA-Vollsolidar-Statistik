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

EVALUATE=evaluate.py

# Choose venv folder; Check for .env, .venv, venv, env; If not found, use '.env'
VENV?=$(shell [ -d ".env" ] && echo ".env" || echo $(shell [ -d ".venv" ] && echo ".venv" || echo $(shell [ -d "venv" ] && echo "venv" || echo $(shell [ -d "env" ] && echo "env" || echo ".env"))))

PYTHON=$(VENV)/bin/python3

# Flag to use STUPA-Logo instead of the default one
STUPA?=0

all: compile
	xdg-open $(GERMAN_PDF_TARGET)
	xdg-open $(ENGLISH_PDF_TARGET)

venv:
ifeq ($(shell [ -d "$(VENV)" ] && echo 1 || echo 0), 0)
	python3 -m venv $(VENV)
	source $(VENV)/bin/activate && pip install -r requirements.txt
endif

install-dependencies:
	if [ -z "$(shell dpkg -l | grep texlive-full)" ]; then sudo apt-get install texlive-full; fi
	if [ -z "$(shell dpkg -l | grep latexmk)" ]; then sudo apt-get install latexmk; fi
	if [ -z "$(shell dpkg -l | grep biber)" ]; then sudo apt-get install biber; fi
	if [ -z "$(shell dpkg -l | grep inkscape)" ]; then sudo apt-get install inkscape; fi

actions: install-dependencies compile

compile: german english

clean:
	git clean -dfX

evaluation: venv
	@echo "Using Python from $(PYTHON)"
	$(PYTHON) $(EVALUATE)

german: evaluation
# If not Exists, create 'Build' directory
	[ -d $(GERMAN_BUILD_DIR) ] || mkdir -p $(GERMAN_BUILD_DIR)
# If STUPA is set to 1, set pretex as `-pretex="\newcommand{\logoType}{STUPA}\newcommand{\lang}{de}"`
# Else, set pretex as `-pretex="\newcommand{\lang}{de}"
ifeq ($(STUPA), 1)
	echo "Using STUPA Logo"
	$(LATEX) $(LATEX_FLAGS) -output-directory=$(GERMAN_BUILD_DIR) -pretex="\newcommand{\logoType}{STUPA}\newcommand{\lang}{de}" -usepretex $(SOURCE)
else
	$(LATEX) $(LATEX_FLAGS) -output-directory=$(GERMAN_BUILD_DIR) -pretex="\newcommand{\langType}{de}" -usepretex $(SOURCE)
endif
# If not Exists, create 'Output/German' directory
	[ -d $(GERMAN_OUT_DIR) ] || mkdir -p $(GERMAN_OUT_DIR)
# Copy the PDF to the 'Output/German' directory
	cp $(GERMAN_PDF_SOURCE) $(GERMAN_PDF_TARGET)

english: evaluation
# If not Exists, create 'Build' directory
	[ -d $(ENGLISH_BUILD_DIR) ] || mkdir -p $(ENGLISH_BUILD_DIR)
# If STUPA is set to 1, set pretex as `-pretex="\newcommand{\logoType}{STUPA}\newcommand{\lang}{en}"`
# Else, set pretex as `-pretex="\newcommand{\lang}{en}"
ifeq ($(STUPA), 1)
	echo "Using STUPA Logo"
	$(LATEX) $(LATEX_FLAGS) -output-directory=$(ENGLISH_BUILD_DIR) -pretex="\newcommand{\logoType}{STUPA}\newcommand{\lang}{en}" -usepretex $(SOURCE)
else
	$(LATEX) $(LATEX_FLAGS) -output-directory=$(ENGLISH_BUILD_DIR) -pretex="\newcommand{\langType}{en}" -usepretex $(SOURCE)
endif
# If not Exists, create 'Output/English' directory
	[ -d $(ENGLISH_OUT_DIR) ] || mkdir -p $(ENGLISH_OUT_DIR)
# Copy the PDF to the 'Output/English' directory
	cp $(ENGLISH_PDF_SOURCE) $(ENGLISH_PDF_TARGET)

.PHONY: all clean