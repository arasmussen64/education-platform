#!/bin/bash
# The scenery of "Handshake report": an empty ~/bin for the script, and the
# certificates of the lab's two example servers (start runs them): one on
# port 8443 for www.shop.test, with a stapled OCSP answer, and one on port
# 9443 for legacy.shop.test, with a second certificate, api.shop.test's,
# for a client that asks for that name.
set -euo pipefail
mkdir -p /home/learner/bin
chown learner:learner /home/learner/bin
. /usr/local/lib/lab/tls-servers
d=/usr/local/lib/lab/example
make_ca "$d" "Example CA"
make_leaf "$d" www www.shop.test shop.test
make_leaf "$d" legacy legacy.shop.test old.shop.test
make_leaf "$d" api api.shop.test partners.shop.test
make_staple "$d" www
chmod -R a+rX "$d"
