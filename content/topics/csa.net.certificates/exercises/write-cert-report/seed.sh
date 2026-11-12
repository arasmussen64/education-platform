#!/bin/bash
# The scenery of "Certificate report", made once, when the image is built:
#   - the lab's certificate authority: a root, "Report Lab Root CA", whose
#     certificate is the trust file, /etc/lab/trust.pem, and an
#     intermediate it signs, "Report Lab Intermediate" (the checks make
#     intermediates of their own under the same root as they run);
#   - the certificates of the lab's two example servers (start runs them):
#     on port 8443, www.shop.test's (and shop.test's), sent with the
#     intermediate; on port 9443, legacy.shop.test's, sent alone, and
#     api.shop.test's for a client that asks for that name, sent alone too;
#   - an empty ~/bin for the script.
set -euo pipefail
. /usr/local/lib/lab/tls-servers
ca=/usr/local/lib/lab/ca
make_root "$ca" "Report Lab Root CA"
make_inter "$ca/inter" "Report Lab Intermediate" "$ca"
mkdir -p /etc/lab
cp "$ca/root.pem" /etc/lab/trust.pem
chmod 644 /etc/lab/trust.pem
chmod -R go-rwx "$ca"

d=/usr/local/lib/lab/example
mkdir -p "$d"
i=$ca/inter
make_leaf "$d" www "$i" "$i/inter.pem" "$i/inter.key" $((90 * 24)) www.shop.test shop.test
make_leaf "$d" legacy "$i" "$i/inter.pem" "$i/inter.key" $((400 * 24)) legacy.shop.test old.shop.test
make_leaf "$d" api "$i" "$i/inter.pem" "$i/inter.key" $((30 * 24)) partners.shop.test api.shop.test
cp "$i/inter.pem" "$d/chain.pem"
chmod -R a+rX "$d"

mkdir -p /home/learner/bin
chown learner:learner /home/learner/bin
