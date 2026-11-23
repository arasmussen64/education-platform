FROM lab-base-id
# The shop's sign-in, set up by someone else, with faults left in. The realm,
# the conditional-access policies and the watcher are all here; the learner
# mends what is wrong. The people, their keys and their app secrets are made
# here at build.
COPY topology /etc/netlab/topology
COPY machines/ /etc/netns/
COPY --chmod=755 bin/signin-watch /usr/local/bin/signin-watch
COPY --chmod=755 bin/ca-cases /usr/local/lib/lab-checks/ca-cases
COPY --chmod=755 bin/policies-enforced /usr/local/lib/lab-checks/policies-enforced
COPY units/signin-watch.service /etc/systemd/system/signin-watch.service
COPY phish-test.log /var/log/shop/phish-test.log
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
 && printf 'bg-1\nbg-2\n' > /etc/shop/watched-accounts \
 && idlab bake \
 && systemctl enable signin-watch \
 && netlab seal /etc/netlab/topology /var/log/shop/phish-test.log
