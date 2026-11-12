FROM lab-base-net
# The cables, and each machine's own files: its addresses, routes and
# tunnel (/etc/network/up), and web's site.
COPY topology /etc/netlab/topology
COPY machines/ /etc/netns/
# The shop's site and its price list (about 2 MB) on web, whose nginx
# serves /srv/web. Then every machine gets its own copy of what its
# services need, and the cables are sealed as scenery.
RUN mkdir -p /srv/web \
 && echo "The shop's site" > /srv/web/index.html \
 && awk 'BEGIN { print "sku,item,price"; for (i = 1; i <= 80000; i++) printf "SKU-%06d,item %d,%d.%02d\n", i, i, i % 500, i % 100 }' > /srv/web/pricelist.csv \
 && netlab enable \
 && netlab seal /etc/netlab/topology
