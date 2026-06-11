#!/bin/bash

find "${BUILD_DIR}" -type f | while read -r fname; do
	fname_base="$(basename "${fname}")"
	case "${fname##*.}" in
	html)
		minify --html-keep-quotes "${fname}" -o "/tmp/${fname_base}" &&
			mv -f "/tmp/${fname_base}" "${fname}"
		;;
	css | js | json | svg | xml)
		minify "${fname}" -o "/tmp/${fname_base}" &&
			mv -f "/tmp/${fname_base}" "${fname}"
		;;
	esac
done
