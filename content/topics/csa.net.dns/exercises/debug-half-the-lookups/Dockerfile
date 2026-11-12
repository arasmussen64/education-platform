FROM lab-base-net
# The network (machines, cables, addresses) and each machine's own files;
# then every machine gets its own copy of what its services need, and they
# are enabled. dnssec-setup gives each signed zone its key and links the
# chain of trust: each child's DS record in its parent's zone (broken.test's
# matching none of its keys, on purpose), and the root's key as every
# resolver's trust anchor. pay.shop.test is signed by hand, with signatures
# that ran from 31 days before the build to the day before it. The story
# (lab-story.service) runs once at the first boot. Then the scenery is
# sealed: the network, the root's and test.'s servers, and the public
# resolvers.
COPY topology /etc/netlab/topology
COPY machines/ /etc/netns/
COPY dnssec-setup story.sh /usr/local/lib/lab/
COPY lab-story.service /etc/systemd/system/lab-story.service
RUN chmod 755 /usr/local/lib/lab/dnssec-setup /usr/local/lib/lab/story.sh \
 && chmod 644 /etc/systemd/system/lab-story.service \
 && find /etc/netns -type f -perm /111 -exec chmod 644 {} + \
 && netlab enable \
 && /usr/local/lib/lab/dnssec-setup .@root test@tld@root shop.test@ns1@tld pay.shop.test@ns1@ns1 'broken.test@tld@tld!' \
 && cd /etc/netns/ns1/bind \
 && dnssec-signzone -q -S -K keys -z -P -s now-31d -e now-1d -o pay.shop.test -f db.pay.shop.test db.pay.shop.test.unsigned \
 && systemctl enable lab-story.service \
 && netlab seal /etc/netlab/topology /etc/netns/root/bind/db.root /etc/netns/tld/bind/db.test \
      /etc/netns/tld/bind/db.broken.test /etc/netns/tld/bind/named.conf.local \
      /etc/netns/isp1/unbound/unbound.conf /etc/netns/isp2/unbound/unbound.conf /etc/netns/isp3/unbound/unbound.conf
