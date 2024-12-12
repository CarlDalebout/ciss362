run:
	pdflatex --shell-escape main.tex
	pdflatex --shell-escape main.tex
	make cleantmp

student:
	make pdf
	rm -rf student
	rm -f student.tar
	rm -f student.tar.gz
	mkdir student
	rsync -rv --exclude '*~' --exclude 'auto' --exclude 'student' . student
	tar -cvf student.tar student
	gzip student.tar
cc:
	make c
	rm -rf main.pdf
view:
	xdg-open main.pdf

v:
	xdg-open main.pdf
        
plain:
	python ../setstyle.py main.tex --style=plain
	make

fancy:
	python ../setstyle.py main.tex --style=fancy
	make

commit:
	svn commit -m ''

s:
	make sync

sync:
	rsync -avz --delete --exclude=".svn" /home/student/svnproject/n/ /home/student/host-symlinks/360/n
	make diff

diff:
        # only works for ciss360
	diff -r -x ".svn"  . ~/host-symlinks/360/n

cleantmp:
	rm -rf abc.outut
	rm -rf 'main.log' 
	rm -rf 'main.aux'
	rm -rf 'main.toc'
	rm -rf 'main.out'
	rm -rf 'main.idx'
	rm -rf 'main.ilg'
	rm -rf 'texput.log'
	rm -rf 'shEsc.tmp'
	rm -rf 'main.vrb'
	rm -rf 'main.snm'
	rm -rf 'main.nav'
	rm -rf 'abc.output'

clean:
	rm -rf 'main.pdf'
	make cleantmp
        
c:
	rm -rf 'main.pdf'
	make cleantmp
    
mail:
	sendgmail --attach=main.pdf

g:
	cp *.pdf /mnt/hgfs/yliow/Google\ Drive/toprint/

