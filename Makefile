ROOT_DIR	:= $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
BUILD_DIR	:= $(ROOT_DIR)/build

export BUILD_DIR

.PHONY: generate
generate: init pages facade strip assets sitemap minify

.PHONY: init
init:
	@mkdir -p $(BUILD_DIR)

.PHONY: assets
assets: init
	@cp -rf site/static/* $(BUILD_DIR)/

.PHONY: wikis
wikis:
	@git submodule update --init --recursive --remote

.PHONY: pages
pages: init
	@uv run python -m streambinder.pages

.PHONY: facade
facade: init pages
	@uv run python -m streambinder.facade

.PHONY: strip
strip: init
	@find $(BUILD_DIR) -type f \
		-not -name 'index.html' \
		-not -name 'index.md' \
		-not -name '*.jpg' \
		-not -name '*.png' \
		-not -name '*.gif' \
		-not -name '*.svg' -delete

.PHONY: sitemap
sitemap: init
	@uv run python -m streambinder.sitemap

.PHONY: minify
minify: facade strip assets
	@bash scripts/minify.sh

.PHONY: docker
docker:
	@bash scripts/docker.sh

.PHONY: clean
clean:
	@rm -rf $(BUILD_DIR)
