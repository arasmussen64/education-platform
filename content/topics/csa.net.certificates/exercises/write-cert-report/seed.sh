#!/bin/bash
# The scenery of "Certificate report", made once, when the image is built:
#   - the lab's certificate authority: a root, "Report Lab Root CA", whose
#     certificate is the trust file, /etc/lab/trust.pem, and an
#     intermediate it signs, "Report Lab Intermediate" (the checks make
#     intermediates of their own under the same root as they run);
#   - an empty ~/bin for the script.
# The example servers' certificates are made from that intermediate each
# time the lab starts (make-examples, which start runs), not here.
set -euo pipefail
. /usr/local/lib/lab/tls-servers
ca=/usr/local/lib/lab/ca
make_root "$ca" "Report Lab Root CA"
make_inter "$ca/inter" "Report Lab Intermediate" "$ca"
mkdir -p /etc/lab
cp "$ca/root.pem" /etc/lab/trust.pem
chmod 644 /etc/lab/trust.pem
chmod -R go-rwx "$ca"

mkdir -p /home/learner/bin
chown learner:learner /home/learner/bin
