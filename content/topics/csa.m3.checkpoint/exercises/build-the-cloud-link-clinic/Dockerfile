FROM lab-base-net
# The network (machines, cables, addresses), and each machine's own files:
# the cloud's router and VPN gateway, with its BGP and its IPsec connection
# configured and saved; edge, the data centre's router, with FRR running
# and only a default route. The cloud's gateway is ordered to start before
# edge's; the cloud's console stand-ins (cloud-vpn-status, cloud-vpn-log)
# and the provider's sheet; and a helper for the checks, out of the
# learner's PATH. Then every machine gets its own copy of what
# its services need, they start at every boot, and what isn't the
# learner's (the network and the cloud's side) is sealed.
COPY topology /etc/netlab/topology
COPY machines/ /etc/netns/
COPY cloud-first.conf /etc/systemd/system/strongswan@cloud.service.d/cloud-first.conf
COPY cloud-vpn-status cloud-vpn-log /usr/local/bin/
COPY link-sheet.txt /srv/provider/link-sheet.txt
COPY same-as-its-files /usr/local/lib/lab-checks/same-as-its-files
RUN chmod 644 /etc/systemd/system/strongswan@cloud.service.d/cloud-first.conf /srv/provider/link-sheet.txt \
 && chmod 755 /usr/local/bin/cloud-vpn-status /usr/local/bin/cloud-vpn-log /usr/local/lib/lab-checks/same-as-its-files \
 && chmod 600 /etc/netns/cloud/swanctl/conf.d/clinic.conf \
 && netlab enable \
 && netlab seal /etc/netlab/topology /etc/netns/cloud/frr/frr.conf /etc/netns/cloud/swanctl/conf.d/clinic.conf \
      /srv/provider/link-sheet.txt /usr/local/bin/cloud-vpn-status /usr/local/bin/cloud-vpn-log
