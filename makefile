run:
	py ss.py

setup:
	py -m pip install -r requirements.txt

fmt:
	py -m autopep8 -r -i -a -a --ignore=E402,E721 --max-line-length 150 .

.PHONY: build
build:
	py tools\build.py
