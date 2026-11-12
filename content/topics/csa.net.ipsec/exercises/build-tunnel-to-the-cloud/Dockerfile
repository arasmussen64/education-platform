FROM lab-base-net
# The network (machines, cables, addresses), and each machine's own files:
# the provider's gateway, cloud, with its IPsec connection and BGP
# configured and saved; vpn, the office's gateway, with FRR running and
# only a default route; the app's web server. The provider's gateway is
# ordered to start before the office's; the provider's console stand-ins
# (cloud-vpn-status, cloud-vpn-log, cloud-maintenance) and its
# configuration sheet; the app's pages. Then every machine gets its own
# copy of what its services need, they start at every boot, and what isn't
# the learner's (the network and the provider's side) is sealed.
COPY topology /etc/netlab/topology
COPY machines/ /etc/netns/
COPY cloud-first.conf /etc/systemd/system/strongswan@cloud.service.d/cloud-first.conf
COPY cloud-vpn-status cloud-vpn-log cloud-maintenance /usr/local/bin/
COPY vpn-config.txt /srv/provider/vpn-config.txt
RUN chmod 644 /etc/systemd/system/strongswan@cloud.service.d/cloud-first.conf /srv/provider/vpn-config.txt \
 && chmod 755 /usr/local/bin/cloud-vpn-status /usr/local/bin/cloud-vpn-log /usr/local/bin/cloud-maintenance \
 && chmod 600 /etc/netns/cloud/swanctl/conf.d/office.conf \
 && mkdir -p /var/www/app \
 && printf 'The shop in the cloud: orders, stock and the daily report.\n' > /var/www/app/index.html \
 && yes 'shop report: orders, stock and takings, one line after another' | head -c 303030 > /var/www/app/report.txt \
 && netlab enable \
 && netlab seal /etc/netlab/topology /etc/netns/cloud/frr/frr.conf /etc/netns/cloud/swanctl/conf.d/office.conf \
      /srv/provider/vpn-config.txt /usr/local/bin/cloud-vpn-status /usr/local/bin/cloud-vpn-log /usr/local/bin/cloud-maintenance \
      /var/www/app/index.html /var/www/app/report.txt
