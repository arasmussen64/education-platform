FROM lab-base-id
# Four machines: the staff laptop, the identity provider, the phishing host
# (a lookalike name, login.shop-help.test, with its own valid certificate from
# the lab CA) and the attacker's machine. The relay passes a sign-in through
# to the real provider; the people, their keys and app secrets are made here.
COPY topology /etc/netlab/topology
COPY machines/ /etc/netns/
COPY --chmod=755 bin/relay /usr/local/bin/relay
COPY --chmod=755 bin/attacker-replay /usr/local/bin/attacker-replay
COPY units/relay@.service /etc/systemd/system/relay@.service
RUN netlab enable \
 && idlab idp idp https://login.shop.test \
 && idlab names login.shop.test=10.0.5.10 login.shop-help.test=10.0.5.50 \
 && idlab cert phish login.shop-help.test \
 && idlab account alice ana \
 && idlab seckey alice 0a000000-0000-4000-8000-000000000031 \
 && idlab otp ana \
 && install -d -m 755 /etc/shop \
 && idlab bake \
 && systemctl enable relay@phish \
 && netlab seal /etc/netlab/topology /etc/netns/idp/shop/ca/20-admins-phishing-resistant.json
