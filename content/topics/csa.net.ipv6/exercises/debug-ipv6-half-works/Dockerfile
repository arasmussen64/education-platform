FROM lab-base-net
# The network, and r1's own files (addresses, forwarding, firewall and NAT,
# router advertisements); web runs the base's test server.
COPY topology /etc/netlab/topology
COPY machines/ /etc/netns/
# A 2 MB file to upload from the laptops (the checks send it to web's byte
# counter); then every machine gets its own copy of what its services
# need, the services start at every boot, and the network itself is sealed
# as scenery.
RUN mkdir -p /var/lib/lab \
 && head -c 2000000 /dev/urandom > /var/lib/lab/upload.bin \
 && chmod 644 /var/lib/lab/upload.bin \
 && netlab enable \
 && netlab seal /etc/netlab/topology
