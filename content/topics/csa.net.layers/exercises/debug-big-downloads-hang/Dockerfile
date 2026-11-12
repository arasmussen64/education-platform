FROM lab-base-net
# The cables, and each machine's own files: its addresses, routes and
# tunnel (/etc/network/up), web's firewall, and the two sites.
COPY topology /etc/netlab/topology
COPY machines/ /etc/netns/
# The shop's site and its price list (about 2 MB) on web, the file server's
# page on files (each machine's nginx serves its own folder under /srv), and
# the price list's checksum, which a check compares with what arrives. Then
# every machine gets its own copy of what its services need, and the
# scenery is sealed: the cables and the office laptop's settings.
RUN mkdir -p /srv/web /srv/files /var/lib/lab \
 && echo "The shop's site" > /srv/web/index.html \
 && awk 'BEGIN { print "sku,item,price"; for (i = 1; i <= 80000; i++) printf "SKU-%06d,item %d,%d.%02d\n", i, i, i % 500, i % 100 }' > /srv/web/pricelist.csv \
 && sha256sum /srv/web/pricelist.csv | cut -d' ' -f1 > /var/lib/lab/pricelist.sha256 \
 && echo "The shop's file server" > /srv/files/index.html \
 && netlab enable \
 && netlab seal /etc/netlab/topology /etc/netns/office/network/up
