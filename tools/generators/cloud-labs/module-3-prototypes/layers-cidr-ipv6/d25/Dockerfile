FROM l1proto-net:1
COPY netlab-up netlab-down netlab-state /usr/local/sbin/
COPY on web-svc /usr/local/bin/
COPY netlab /etc/netlab
COPY netlab.service web-svc.service radvd-r1.service /etc/systemd/system/
RUN chmod 755 /usr/local/sbin/netlab-* /usr/local/bin/on /usr/local/bin/web-svc \
 && head -c 2000000 /dev/urandom > /var/lib/upload.bin && chmod 644 /var/lib/upload.bin \
 && for u in netlab web-svc radvd-r1; do ln -s /etc/systemd/system/$u.service /etc/systemd/system/multi-user.target.wants/$u.service; done
CMD ["/sbin/init"]
