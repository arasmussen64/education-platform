FROM lab-base-net
# The network (with the long, lossy link as scenery), dr1's receiver, and
# archive-push, the nightly job's stand-in. Then every machine gets its own
# folders, the receiver starts at every boot, and the network is sealed.
COPY topology /etc/netlab/topology
COPY backup-sink.service /etc/systemd/system/
COPY archive-push /usr/local/bin/
RUN chmod 644 /etc/systemd/system/backup-sink.service \
 && chmod 755 /usr/local/bin/archive-push \
 && netlab enable \
 && systemctl enable backup-sink \
 && netlab seal /etc/netlab/topology /usr/local/bin/archive-push
