
all: sdist bdist py2app

sdist:
	python setup.py sdist
	
bdist:
	python setup.py bdist
	
py2app:
	python setup.py py2app
	
clean:
	rm -rf build dist *.egg-info
	rm -rf `find . -name "*.pyc"`
	rm -rf `find . -name "\.DS_Store"`