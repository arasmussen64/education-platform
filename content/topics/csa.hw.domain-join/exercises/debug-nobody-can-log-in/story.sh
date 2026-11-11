#!/bin/bash
# The story so far, made once at the lab's first boot, after dc1 is up. This
# server was joined to the domain months ago, and members of linux-admins
# logged in every day. Then three things happened, one after another. Part
# of the scenery; reading it spoils the exercise.
set -euo pipefail
[ -e /var/lib/lab/story-done ] && exit 0
on_dc() { ip netns exec dc unshare --uts --mount --propagation private /usr/local/lib/lab/dc-enter "$@"; }
mkdir -p /var/lib/lab

# Wait for dc1's name server (it starts a moment after dc1 says it's ready).
for _ in $(seq 1 90); do
  dig +short +time=1 +tries=1 @10.0.9.10 _ldap._tcp.ad.shop.test SRV 2>/dev/null | grep -q dc1 && break
  sleep 1
done

# The working state: the domain's zones forwarded, joined, home directories,
# only the group permitted.
printf 'server=/ad.shop.test/10.0.9.10\nserver=/9.0.10.in-addr.arpa/10.0.9.10\n' > /etc/dnsmasq.d/ad.conf
systemctl restart dnsmasq
echo 'Shop-Admin-1' | realm join -U Administrator ad.shop.test
pam-auth-update --enable mkhomedir > /dev/null 2>&1
realm permit -g linux-admins@ad.shop.test
# The local side, from the hardening topic: SSH is for named groups only.
# kim, an operator, is in the local group ssh-users; ben, who runs the
# backups by cron, is in none of the groups and never logs in over SSH.
groupadd ssh-users
useradd -m -s /bin/bash -G ssh-users kim
echo 'kim:Kim-Local-1' | chpasswd
useradd -m -s /bin/bash ben
echo 'ben:Ben-Local-1' | chpasswd

# Fault 1: the forwarders were moved to an address where no name server
# answers.
sed -i 's/10\.0\.9\.10/10.0.9.11/' /etc/dnsmasq.d/ad.conf
systemctl restart dnsmasq
# Fault 2: the computer account's password was reset on dc1, so the keys in
# this machine's keytab no longer match it.
on_dc samba-tool user setpassword 'LAB$' --newpassword='Reset-By-Someone-77' > /dev/null 2>&1
# Fault 3: an SSH hardening change that lists only the local group.
printf '# Only these groups may log in over SSH.\nAllowGroups ssh-users\n' > /etc/ssh/sshd_config.d/60-access.conf
systemctl try-reload-or-restart ssh

sss_cache -E || true
systemctl restart sssd || true
touch /var/lib/lab/story-done
