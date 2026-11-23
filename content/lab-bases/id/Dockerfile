# The identity labs' shared base (ADR-0018, fourth amendment): the network
# base with an identity provider on it. Every identity lab of Module 4
# starts "FROM lab-base-id"; tools/labcheck.py builds lab-base-net first,
# then this, then the lab. So an identity lab's machines are netlab's
# machines, and this adds what runs on them: Keycloak (the identity
# provider), Apache with its OpenID Connect, SAML and OAuth 2.0 modules (a
# site or an API that relies on it), a stand-in API that checks tokens, a
# clock a machine can have wrong with a time sync that sets it, and the
# helpers learners and checks use.
# README.md, beside this file, is what an author reads before writing one.
FROM lab-base-net
ENV DEBIAN_FRONTEND=noninteractive

# Layer 1: Ubuntu's archive only. Java for Keycloak; Apache and the three
# modules; xmlsec1 (SAML signatures by hand); jq; oathtool (one-time codes);
# faketime (libfaketime: a machine's own clock, and certificates dated two
# days back); chrony (a lab's time server, only ever run with -x);
# python3-fido2 (the software security key in "signin"; it brings
# python3-cryptography, which the checks' token maker uses);
# ca-certificates (for the download below, and the bundle the lab's own CA
# joins). The packages switch Apache's and chrony's own services on; they
# are switched off again here and replaced below by units that never start
# the daemon: chrony's own service would set the clock, and a lab's clock is
# the real clock of Docker's whole machine.
RUN apt-get update \
 && apt-get install -y --no-install-recommends ca-certificates openjdk-21-jre-headless apache2 libapache2-mod-auth-openidc libapache2-mod-auth-mellon libapache2-mod-oauth2 xmlsec1 jq faketime chrony python3-fido2 oathtool \
 && rm -rf /var/lib/apt/lists/* \
 && systemctl disable apache2 chrony

# Layer 2: Keycloak, the base's one download from outside the archive,
# pinned by version and checksum (README.md records the pin: the newest
# release at least two weeks old on the day this was built).
RUN curl -fsSLo /tmp/keycloak.tar.gz https://github.com/keycloak/keycloak/releases/download/26.8.2/keycloak-26.8.2.tar.gz \
 && echo 'dd124787283918bc597628887168333465ee2a811a389e0003569e52be7e487f  /tmp/keycloak.tar.gz' | sha256sum -c - \
 && mkdir -p /opt/keycloak \
 && tar -xzf /tmp/keycloak.tar.gz -C /opt/keycloak --strip-components=1 \
 && rm /tmp/keycloak.tar.gz

# Layer 3: the base's own files. Keycloak is built for its file database
# (H2, in /opt/keycloak/data) and started once, so the image already holds
# its master realm and an administrator whose password is made here, at
# build, and is in no repository. A lab's own realm is added by "idlab
# bake" in its Dockerfile. The folders made on the lab machine are the ones
# "ip netns exec" lays a machine's own copy over (it can only lay a copy
# over something that exists).
COPY lib/ /usr/local/lib/idlab/
COPY bin/ /usr/local/bin/
COPY units/ /etc/systemd/system/
RUN chmod 755 /usr/local/lib/idlab/* /usr/local/bin/* \
 && chmod 644 /etc/systemd/system/keycloak@.service /etc/systemd/system/apache2@.service /etc/systemd/system/stock-api@.service \
      /etc/systemd/system/timesync@.service /etc/systemd/system/chrony@.service /etc/systemd/system/machine-clocks.service \
      /usr/local/lib/idlab/idlib.sh /usr/local/lib/idlab/jwtlib.py /usr/local/lib/idlab/kcapi.py \
 && /usr/local/lib/idlab/plain-units \
 && groupadd -r tlskey && useradd -r -d /opt/keycloak -s /usr/sbin/nologin -G tlskey keycloak \
 && usermod -a -G tlskey www-data \
 && mkdir -p /etc/idlab /etc/keycloak /etc/tls /etc/clock /etc/stock-api && touch /etc/faketimerc \
 && a2enmod -q ssl cgid headers && a2dismod -q auth_openidc auth_mellon oauth2 \
 && /opt/keycloak/bin/kc.sh build --db=dev-file \
 && /usr/local/lib/idlab/first-start \
 && systemctl enable machine-clocks.service
CMD ["/sbin/init"]
