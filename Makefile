.PHONY: build
build: html

%:
	cd docs && make $@
