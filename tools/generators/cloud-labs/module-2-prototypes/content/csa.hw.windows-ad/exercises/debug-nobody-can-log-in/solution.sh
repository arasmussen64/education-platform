# Three faults, found from three pieces of evidence.
#
# 1. Names. "kinit alice" says: Cannot find KDC for realm "AD.SHOP.TEST".
#    dig for the domain's SRV record through lab's resolver gives nothing,
#    and directly at dc1 (10.0.9.10) gives dc1. The site resolver's forwarder
#    for the zone points at 10.0.9.11, where nothing answers.
dig +short _ldap._tcp.ad.shop.test SRV
dig +short @10.0.9.10 _ldap._tcp.ad.shop.test SRV
cat /etc/dnsmasq.d/ad.conf
sudo sed -i 's/10\.0\.9\.11/10.0.9.10/' /etc/dnsmasq.d/ad.conf
sudo systemctl restart dnsmasq
dig +short _ldap._tcp.ad.shop.test SRV

# 2. The machine's own account. With names fixed, a user can get a ticket
#    (kinit alice works) but SSSD stays offline; its journal says
#    "Failed to initialize credentials using keytab ... Preauthentication
#    failed". The key in /etc/krb5.keytab no longer matches the computer
#    account's password on dc1, so the machine can't prove who it is. A user
#    can't repair that; the machine has to be joined again.
sudo kinit -k 'LAB$@AD.SHOP.TEST' || true
sudo realm leave
echo 'Shop-Admin-1' | sudo realm join -U Administrator ad.shop.test
#    Joining again writes a fresh SSSD config, which lets every domain
#    account in. Put the rule back.
sudo realm permit -g linux-admins@ad.shop.test

# 3. SSH. sshd's log says alice is "not allowed because none of user's
#    groups are listed in AllowGroups": a hardening change listed only the
#    local group. Add the domain group; keep the restriction.
printf '# Only these groups may log in over SSH.\nAllowGroups ssh-users linux-admins@ad.shop.test\n' | sudo tee /etc/ssh/sshd_config.d/60-access.conf > /dev/null
sudo sshd -t
sudo systemctl try-reload-or-restart ssh

realm list
id alice@ad.shop.test
