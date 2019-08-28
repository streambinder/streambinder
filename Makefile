.PHONY: all
all: minify

.PHONY: prepare
prepare:
	@mkdir -p public

.PHONY: minify
minify: prepare
	@ ( \
		cp -rfp src/* public/ && \
		cd src && \
		find -type f | while read -r fname; do \
			case "$${fname##*.}" in \
				html|css|js|json|svg|xml) \
					minify "$${fname}" -o "../public/$${fname}"; \
					;; \
				png) \
					optipng -strip all -silent -o7 "$${fname}" -out "../public/$${fname}"; \
					;; \
				jpg|jpeg) \
					jpegoptim -osqf "$${fname}" -d "../public/$$(dirname "$${fname}")"; \
					;; \
				*) \
					;; \
			esac; \
		done; \
	);

.PHONY: clean
clean:
	@rm -rf public