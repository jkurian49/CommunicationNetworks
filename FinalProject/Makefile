SHELL := /bin/bash

INPUT ?= ./file_1MB.txt
OUTPUT ?= ./output.txt

test:
	python2 -u receiver.py > $(OUTPUT) & time python2 -u sender.py < $(INPUT) > $(OUTPUT) &
diff:
	diff $(INPUT) $(OUTPUT)
kill:
	pkill python2
clean:
	rm *.log $(OUTPUT) *.pyc
