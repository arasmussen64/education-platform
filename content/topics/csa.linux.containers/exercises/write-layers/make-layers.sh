#!/bin/bash
# Three layers of a small "image", as plain folders, made at image build:
# base (the OS), deps (a library), app (the program, and a newer version
# file that should win over base's).
set -euo pipefail
mkdir -p /srv/layers/base/etc /srv/layers/base/app /srv/layers/deps/app /srv/layers/app/app /srv/layers/app/etc
echo 1 > /srv/layers/base/etc/version
echo "the shop's app, built from three layers" > /srv/layers/base/app/README
echo "def lib(): ..." > /srv/layers/deps/app/lib.txt
printf '#!/bin/sh\necho "the shop app"\n' > /srv/layers/app/app/main.sh
echo 2 > /srv/layers/app/etc/version
