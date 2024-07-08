# Makefile for LaTeX documents

LATEX=latexmk
BIBTEX=biber
LATEX_FLAGS=-xelatex -shell-escape -synctex=1 -interaction=nonstopmode

SOURCE=Main.tex
PDF=$(SOURCE:.tex=.pdf)

all:
	$(LATEX) $(LATEX_FLAGS) $(SOURCE)
	xdg-open $(PDF)

compile:
	$(LATEX) $(LATEX_FLAGS) $(SOURCE)

clean:
	git clean -dfX


.PHONY: all clean