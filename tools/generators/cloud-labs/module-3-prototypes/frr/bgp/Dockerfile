FROM frrproto-base:ubuntu
COPY network.sh /usr/local/lib/lab/network.sh
COPY lab-network.service /etc/systemd/system/
COPY frr-dropin/lab.conf /etc/systemd/system/frr@.service.d/lab.conf
COPY on router /usr/local/bin/
COPY frr/ /etc/frr/
RUN chmod 755 /usr/local/lib/lab/network.sh /usr/local/bin/on /usr/local/bin/router \
 && chown -R frr:frr /etc/frr && chmod -R u=rwX,g=rwX,o= /etc/frr \
 && systemctl disable frr \
 && mkdir -p /etc/systemd/system/multi-user.target.wants \
 && ln -s /etc/systemd/system/lab-network.service /etc/systemd/system/multi-user.target.wants/lab-network.service \
 && for r in edge ispa ispb cloud; do ln -s /usr/lib/systemd/system/frr@.service /etc/systemd/system/multi-user.target.wants/frr@$r.service; done
CMD ["/sbin/init"]
