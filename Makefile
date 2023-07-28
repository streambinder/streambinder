ROOT_DIR	:= $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
MAKE_DIR	:= $(ROOT_DIR)/.make
BUILD_DIR	:= $(ROOT_DIR)/build

export BUILD_DIR

.PHONY: generate
generate: init pages facade dynimages strip assets minify

.PHONY: init
init:
	@mkdir -p $(BUILD_DIR)

.PHONY: assets
assets: init
	@cp -rf src/static/* $(BUILD_DIR)/

.PHONY: wikis
wikis:
	@git submodule update --init --recursive --remote

.PHONY: pages
pages: init
	@python3 $(MAKE_DIR)/pages.py

.PHONY: facade
facade: init pages
	@python3 $(MAKE_DIR)/facade.py

.PHONY: strip
strip: init
	@find $(BUILD_DIR) -type f \
		-not -name 'index.html' \
		-not -name '*.jpg' \
		-not -name '*.png' \
		-not -name '*.gif' \
		-not -name '*.svg' -delete

.PHONY: minify
minify: facade strip assets
	@bash $(MAKE_DIR)/minify.sh

.PHONY: dynimages
dynimages: pages
	@python3 $(MAKE_DIR)/dynimages.py

.PHONY: docker
docker:
	@bash $(MAKE_DIR)/docker.sh

.PHONY: clean
clean:
	@rm -rf $(BUILD_DIR)
