FROM l1proto-net:1
COPY netlab-up netlab-down netlab-state /usr/local/sbin/
COPY on /usr/local/bin/
COPY netlab /etc/netlab
COPY netlab.service web-http.service files-http.service /etc/systemd/system/
RUN chmod 755 /usr/local/sbin/netlab-* /usr/local/bin/on \
 && mkdir -p /srv/web /srv/files && head -c 2000000 /dev/urandom > /srv/web/pricelist.csv && echo shop > /srv/web/index.html && echo files > /srv/files/index.html \
 && sha256sum /srv/web/pricelist.csv | cut -d' ' -f1 > /var/lib/pricelist.sha256 \
 && for u in netlab web-http files-http; do ln -s /etc/systemd/system/$u.service /etc/systemd/system/multi-user.target.wants/$u.service; done
CMD ["/sbin/init"]
