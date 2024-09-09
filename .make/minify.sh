#!/bin/bash

find "${BUILD_DIR}" -type f | while read -r fname; do
	fname_base="$(basename "${fname}")"
	case "${fname##*.}" in
	html | css | js | json | svg | xml)
		minify "${fname}" -o "/tmp/${fname_base}" &&
			mv -f "/tmp/${fname_base}" "${fname}"
		;;
		# png)
		#     optipng -strip all -silent -o7 "${fname}" -out "/tmp/${fname_base}" && \
		#         mv -f "/tmp/${fname_base}" "${fname}"
		#     ;;
		# jpg|jpeg) \
		#     jpegoptim -osqf "${fname}" -d /tmp && \
		#         mv -f "/tmp/${fname_base}" "${fname}"
		#     ;;
		# *)
		#     ;;
	esac
done
