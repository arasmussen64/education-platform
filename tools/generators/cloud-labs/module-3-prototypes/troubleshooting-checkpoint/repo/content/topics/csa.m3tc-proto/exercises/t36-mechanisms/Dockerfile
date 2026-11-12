FROM lab-base-m3tc
COPY topology /etc/netlab/topology
COPY machines/ /etc/netns/
COPY scenery/db-api scenery/old-lb scenery/lb-garp /usr/local/bin/
COPY scenery/db-api.service scenery/old-lb.service scenery/lb-garp.service /etc/systemd/system/
RUN chmod 755 /usr/local/bin/db-api /usr/local/bin/old-lb /usr/local/bin/lb-garp \
 && netlab enable && systemctl enable db-api old-lb lb-garp
