FROM lab-base-id
# The staff laptop and the identity provider. The realm already has the
# strong sign-in flow (admins a key, others a code), but brute-force
# detection is off, the two emergency accounts are in no group, there are no
# conditional-access policies and nobody is watched. The people, their keys
# and their app secrets are made here at build.
COPY topology /etc/netlab/topology
COPY machines/ /etc/netns/
COPY --chmod=755 bin/signin-watch /usr/local/bin/signin-watch
COPY --chmod=755 bin/ca-cases /usr/local/lib/lab-checks/ca-cases
COPY units/signin-watch.service /etc/systemd/system/signin-watch.service
RUN netlab enable \
 && idlab idp idp https://login.shop.test \
 && idlab names login.shop.test=10.0.5.10 \
 && idlab account alice carol ana ben bg-1 bg-2 \
 && idlab seckey alice 0a000000-0000-4000-8000-000000000021 \
 && idlab seckey carol 0a000000-0000-4000-8000-000000000022 \
 && idlab seckey bg-1 0a000000-0000-4000-8000-000000000025 \
 && idlab seckey bg-2 0a000000-0000-4000-8000-000000000026 \
 && idlab otp ana ben \
 && install -d -m 755 /etc/shop \
 && : > /etc/shop/watched-accounts \
 && install -d -m 755 /var/log/shop \
 && install -d -m 755 /etc/netns/idp/shop/ca \
 && idlab bake \
 && systemctl enable signin-watch \
 && netlab seal /etc/netlab/topology
