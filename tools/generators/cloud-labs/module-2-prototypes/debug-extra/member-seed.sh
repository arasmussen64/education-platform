#!/bin/bash
# The story so far, made at the lab's first boot. This server was joined to
# the domain months ago, and members of linux-admins logged in every day.
# Then three things happened, one after another. Part of the scenery; reading
# it spoils the exercise.
set -euo pipefail
[ -e /var/lib/lab/member-seeded ] && exit 0
on_dc() { ip netns exec dc unshare --uts --mount --propagation private /usr/local/lib/lab/dc-enter "$@"; }

# Wait for dc1's name server (it starts a moment after dc1 says it's ready).
for _ in $(seq 1 90); do
  dig +short +time=1 +tries=1 @10.0.9.10 _ldap._tcp.ad.shop.test SRV 2>/dev/null | grep -q dc1 && break
  sleep 1
done

# The working state: names forwarded, joined, home directories, the group.
printf 'server=/ad.shop.test/10.0.9.10\nserver=/9.0.10.in-addr.arpa/10.0.9.10\n' > /etc/dnsmasq.d/ad.conf
systemctl restart dnsmasq
echo 'Shop-Admin-1' | realm join -U Administrator ad.shop.test
pam-auth-update --enable mkhomedir > /dev/null 2>&1
realm permit -g linux-admins@ad.shop.test
# A local account that must stay locked out of SSH, and the local group
# whose members may use it.
groupadd ssh-users
usermod -aG ssh-users learner
useradd -m -s /bin/bash ben
echo 'ben:Ben-Local-1' | chpasswd

# Fault 1: the forwarder for the domain's zone points at an address where
# no name server answers.
sed -i 's/10\.0\.9\.10/10.0.9.11/' /etc/dnsmasq.d/ad.conf
systemctl restart dnsmasq
# Fault 2: the computer account's password was reset on dc1, so the key in
# this machine's keytab no longer matches it.
on_dc samba-tool user setpassword 'LAB$' --newpassword='Reset-By-Someone-77' > /dev/null 2>&1
# Fault 3: an SSH hardening change that lists only a local group.
printf '# Only these groups may log in over SSH.\nAllowGroups ssh-users\n' > /etc/ssh/sshd_config.d/60-access.conf

sss_cache -E || true
systemctl restart sssd || true
mkdir -p /var/lib/lab
touch /var/lib/lab/member-seeded
