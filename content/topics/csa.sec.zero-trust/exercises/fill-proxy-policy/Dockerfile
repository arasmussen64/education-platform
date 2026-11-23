FROM lab-base-id
# oauth2-proxy, the access proxy's sign-in half: one of Module 4's six
# pinned downloads from outside Ubuntu's archive. v7.15.6, released
# 2026-11-05, MIT licence: the newest release at least two weeks old on
# 2026-11-23 (github.com/oauth2-proxy/oauth2-proxy/releases, read that day).
# The checksums are GitHub's digests for the two release assets. This RUN is
# the same in every zero-trust lab that has the proxy, so Docker builds it
# once.
RUN arch=$(dpkg --print-architecture) \
 && case $arch in \
      amd64) sum=91b3e86d9c2de679a516e6696704e3fd1acf67e8b8f7be77b618f086f72fb1f0 ;; \
      arm64) sum=3593e50daa517eaa8f8d0966b95786a61a4cdf491694dc9091b8cd32daa85d56 ;; \
      *) echo "no oauth2-proxy pinned for $arch"; exit 1 ;; \
    esac \
 && curl -fsSLo /tmp/oauth2-proxy.tar.gz https://github.com/oauth2-proxy/oauth2-proxy/releases/download/v7.15.6/oauth2-proxy-v7.15.6.linux-$arch.tar.gz \
 && echo "$sum  /tmp/oauth2-proxy.tar.gz" | sha256sum -c - \
 && tar -xzf /tmp/oauth2-proxy.tar.gz -C /tmp \
 && install -m 755 /tmp/oauth2-proxy-v7.15.6.linux-$arch/oauth2-proxy /usr/local/bin/oauth2-proxy \
 && rm -rf /tmp/oauth2-proxy.tar.gz /tmp/oauth2-proxy-v7.15.6.linux-$arch
# The network, each machine's own files, the stand-in database's unit and
# oauth2-proxy's, and the zero-trust labs' shared tools (zt/).
COPY topology /etc/netlab/topology
COPY machines/ /etc/netns/
COPY zt/ /usr/local/lib/zt/
COPY units/shop-db@.service units/oauth2-proxy@.service /etc/systemd/system/
# Everything secret is made here, at build: the lab's CA and the proxy's
# certificate, the proxy's client secret and cookie secret, three people's
# passwords, the realm's signing keys, the device CA and the managed
# laptop's certificate. The proxy and the three firewalls start at boot.
# What isn't the learner's is sealed.
RUN chmod 644 /etc/systemd/system/shop-db@.service /etc/systemd/system/oauth2-proxy@.service \
 && netlab enable \
 && systemctl enable shop-db@db oauth2-proxy@zt \
 && idlab idp idp https://login.shop.test \
 && idlab names login.shop.test=203.0.113.90 apps.shop.test=203.0.113.80 \
 && idlab cert zt apps.shop.test \
 && idlab secret ACCESS_PROXY_SECRET \
 && idlab account ana ben hana \
 && idlab key shop 2025 passive \
 && idlab key shop 2026 \
 && bash /usr/local/lib/zt/setup \
 && (umask 077; openssl rand -hex 16 | tr -d '\n' > /etc/netns/zt/oauth2-proxy/cookie-secret) \
 && idlab bake \
 && netlab seal /etc/netlab/topology /etc/netns/idp/keycloak/realms/shop.json \
      /etc/netns/laptop/device/device.crt \
      /etc/netns/wiki/nftables.conf /etc/netns/payroll/nftables.conf /etc/netns/db/nftables.conf \
      /etc/netns/wiki/nginx/sites-enabled/default /etc/netns/payroll/nginx/sites-enabled/default \
      /etc/netns/zt/nginx/tls/device-ca.crt /etc/netns/zt/oauth2-proxy/client-secret
