FROM frrproto-base:ubuntu
COPY network.sh /usr/local/lib/lab/network.sh
COPY lab-network.service /etc/systemd/system/
COPY on holdconns holdserver /usr/local/bin/
RUN chmod 755 /usr/local/lib/lab/network.sh /usr/local/bin/on /usr/local/bin/holdconns /usr/local/bin/holdserver \
 && systemctl disable frr \
 && mkdir -p /etc/systemd/system/multi-user.target.wants \
 && ln -s /etc/systemd/system/lab-network.service /etc/systemd/system/multi-user.target.wants/lab-network.service
CMD ["/sbin/init"]
