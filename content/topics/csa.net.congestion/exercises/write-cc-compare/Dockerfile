FROM lab-base-net
# This topic's tools, the same line in all its labs so Docker builds the
# layer once: Caddy (the web server, with HTTP/3), aioquic (the HTTP/3
# library h3get is built on) and ngtcp2's example client (gtlsclient, which
# prints a QUIC connection's packets). Ubuntu's curl has no HTTP/3. Caddy
# runs on a machine, as caddy@shop, never on the lab machine itself, so its
# plain unit is replaced by one that says what to type.
RUN apt-get update \
 && apt-get install -y --no-install-recommends caddy python3-aioquic ngtcp2-client ca-certificates \
 && rm -rf /var/lib/apt/lists/* \
 && systemctl disable caddy \
 && printf '%s\n' '[Unit]' 'Description=Not on this lab machine: Caddy runs on shop, as caddy@shop' 'CollectMode=inactive-or-failed' '' '[Service]' 'Type=oneshot' 'ExecStart=/usr/local/lib/netlab/not-here caddy' > /etc/systemd/system/caddy.service
# The network, a backup receiver on each DR site, and the checks' reader of
# the learner's script (kept out of the learner's PATH). Then every
# machine gets its own folders, the receivers start at every boot, and the
# topology, which holds the links, is sealed. The learner's script goes in
# ~/bin, which the lab machine and every machine share.
COPY topology /etc/netlab/topology
COPY backup-sink@.service /etc/systemd/system/
COPY cc-compare-check /usr/local/lib/lab/
RUN chmod 644 /etc/systemd/system/backup-sink@.service \
 && chmod 755 /usr/local/lib/lab/cc-compare-check \
 && netlab enable \
 && systemctl enable backup-sink@dr1 backup-sink@dr2 \
 && netlab seal /etc/netlab/topology
