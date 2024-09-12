TEX := $(shell find . -name '*.tex' -print)
run:
	-python /home/student/.alex/alexrunner.py replaceemail
	pdflatex -halt-on-error -interaction=nonstopmode --shell-escape main.tex 
	make v
main.pdf: $(TEX)
	-python /home/student/.alex/alexrunner.py replaceemail
	pdflatex -halt-on-error -interaction=nonstopmode --shell-escape main.tex 
	pdflatex -halt-on-error -interaction=nonstopmode --shell-escape main.tex
v:
	xdg-open main.pdf
c:
	rm -rf __pycache__ auto desktop.ini \
	abc.output texput.log shEsc.tmp \
	*.log *.aux *.toc *.out *.idx *.ilg \
	*.vrb *.snm *.nav \
	*.py.err *.py.out latex.py *.pytxcode \
	missfont.log traceback.txt *.old \
	submit.tar.gz submit.tar submit *.tex~ \
	a.out *.exe *.o
cc:
	make c
	rm -rf main.pdf
