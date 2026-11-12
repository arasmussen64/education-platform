FROM lab-base-net
# The network and each machine's own files (edge's firewall, dr's and app's
# /etc/sysctl.d, the replication agent's settings); the replication agent
# on app, and the DR site's status API and replication receiver on dr.
# Then every machine gets its own copy of what its services need, they
# start at every boot, and the scenery is sealed: the topology, which holds
# the link and edge's idle timer. (/etc/repl is made empty on the lab
# machine so that app's own copy can be laid over it.)
COPY topology /etc/netlab/topology
COPY machines/ /etc/netns/
COPY repl-agent repl-status /usr/local/bin/
COPY repl-agent@.service repl-status@.service repl-sink@.service /etc/systemd/system/
RUN chmod 755 /usr/local/bin/repl-agent /usr/local/bin/repl-status \
 && chmod 644 /etc/systemd/system/repl-agent@.service /etc/systemd/system/repl-status@.service /etc/systemd/system/repl-sink@.service \
 && mkdir -p /etc/repl \
 && netlab enable \
 && systemctl enable repl-agent@app repl-status@dr repl-sink@dr \
 && netlab seal /etc/netlab/topology
