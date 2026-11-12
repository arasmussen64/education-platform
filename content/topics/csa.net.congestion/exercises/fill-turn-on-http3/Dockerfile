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
# The network and each machine's own files (shop's firewall and Caddyfile,
# each with gaps, and the office's hosts file); Caddy on shop and the HTTP/3
# client. Then every machine gets its own copy of what its services need,
# they start at every boot, and the scenery is sealed: the topology and the
# HTTP/3 client.
COPY topology /etc/netlab/topology
COPY machines/ /etc/netns/
COPY caddy@.service /etc/systemd/system/
COPY h3get /usr/local/bin/
COPY trust-shop-ca /usr/local/sbin/
RUN chmod 644 /etc/systemd/system/caddy@.service \
 && chmod 755 /usr/local/bin/h3get /usr/local/sbin/trust-shop-ca \
 && netlab enable \
 && systemctl enable caddy@shop \
 && netlab seal /etc/netlab/topology /usr/local/bin/h3get
