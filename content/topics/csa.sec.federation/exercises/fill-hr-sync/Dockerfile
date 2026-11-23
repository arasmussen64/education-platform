FROM lab-base-id
# The network, each machine's own files, the HR system's staff file, the
# connector with its gaps, and the checks' own scenario.
COPY topology /etc/netlab/topology
COPY machines/ /etc/netns/
COPY base-fix hr-check /usr/local/lib/shop/
COPY staff.csv /srv/hr/staff.csv
COPY hr-sync /home/learner/bin/hr-sync
# Everything secret is made here, at build: the lab's CA, the connector's
# client secret (in the realm's secrets.env, and in the HR server's own
# /etc/hr-sync/secret, which only root reads) and four people's passwords.
# /etc/hr-sync must exist on the lab machine too, for the HR server's copy
# to be laid over it.
RUN chmod 755 /usr/local/lib/shop/hr-check /home/learner/bin/hr-sync \
 && chown -R learner:learner /home/learner/bin \
 && python3 /usr/local/lib/shop/base-fix \
 && netlab enable \
 && idlab idp idp https://login.shop.test \
 && idlab names login.shop.test=10.0.5.10 hr.shop.test=10.0.5.50 \
 && idlab secret HR_SYNC_SECRET \
 && idlab account ana ben dan eve \
 && idlab key shop 2025 passive \
 && idlab key shop 2026 \
 && mkdir -p /etc/hr-sync /etc/netns/hr/hr-sync \
 && (umask 077; idlab secret-of HR_SYNC_SECRET > /etc/netns/hr/hr-sync/secret) \
 && idlab bake \
 && netlab seal /etc/netlab/topology /etc/netns/idp/keycloak/realms/shop.json /srv/hr/staff.csv
