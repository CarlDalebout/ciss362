pdf:
	pdflatex --shell-escape main.tex
	pdflatex --shell-escape main.tex
	rm -f *.log
	rm -f *.aux
	rm -f *.idx
	rm -f *.out
	xdg-open main.pdf

noview:
	pdflatex --shell-escape main.tex
	pdflatex --shell-escape main.tex
	rm -f *.log
	rm -f *.aux
	rm -f *.idx
	rm -f *.out

view:
	xdg-open main.pdf

v:
	xdg-open main.pdf

clean:
	rm -rf 'main.pdf'

c:
	rm -rf 'main.pdf'
