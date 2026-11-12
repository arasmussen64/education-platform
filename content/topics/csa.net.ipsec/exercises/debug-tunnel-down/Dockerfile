FROM lab-base-net
# The network (machines, cables, the new line's MTU), and each machine's
# own files: vpn, the office's gateway, with its tunnel interface, IPsec
# connection, firewall and BGP, all saved; the two routers between, isp
# and internet, with their firewalls; the provider's gateway, cloud,
# configured and saved, and ordered to start before vpn's; the provider's
# console stand-ins and its configuration sheet; the app's pages and its
# upload counter (web-svc, port 9000). Then every machine gets its own copy
# of what its services need, they start at every boot, and what isn't the
# learner's (the network, the routers between and the provider's side) is
# sealed.
COPY topology /etc/netlab/topology
COPY machines/ /etc/netns/
COPY cloud-first.conf /etc/systemd/system/strongswan@cloud.service.d/cloud-first.conf
COPY cloud-vpn-status cloud-vpn-log cloud-maintenance /usr/local/bin/
COPY vpn-config.txt /srv/provider/vpn-config.txt
RUN chmod 644 /etc/systemd/system/strongswan@cloud.service.d/cloud-first.conf /srv/provider/vpn-config.txt \
 && chmod 755 /usr/local/bin/cloud-vpn-status /usr/local/bin/cloud-vpn-log /usr/local/bin/cloud-maintenance \
 && chmod 600 /etc/netns/cloud/swanctl/conf.d/office.conf /etc/netns/vpn/swanctl/conf.d/cloud.conf \
 && mkdir -p /var/www/app \
 && printf 'The shop in the cloud: orders, stock and the daily report.\n' > /var/www/app/index.html \
 && yes 'shop report: orders, stock and takings, one line after another' | head -c 303030 > /var/www/app/report.txt \
 && netlab enable \
 && netlab seal /etc/netlab/topology /etc/netns/cloud/frr/frr.conf /etc/netns/cloud/swanctl/conf.d/office.conf \
      /etc/netns/isp/nftables.conf /etc/netns/internet/nftables.conf \
      /srv/provider/vpn-config.txt /usr/local/bin/cloud-vpn-status /usr/local/bin/cloud-vpn-log /usr/local/bin/cloud-maintenance \
      /var/www/app/index.html /var/www/app/report.txt
