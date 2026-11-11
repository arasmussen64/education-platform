# Three faults, found one after another, each from the evidence the last
# fix uncovered. The password lines use echo and a pipe (|) only so this
# file can run by itself: in the lab, type the password when asked.

# 1. Names. "kinit alice" says: Cannot find KDC for realm "AD.SHOP.TEST".
#    dig for the domain's SRV record through lab's resolver gives nothing,
#    and straight at dc1 (10.0.9.10) gives dc1. The site resolver's
#    forwarders for the domain's zones point at 10.0.9.11, where nothing
#    answers. Point them at dc1 again.
echo 'Alice-Pass-1' | kinit alice@AD.SHOP.TEST || true
dig +short _ldap._tcp.ad.shop.test SRV
dig +short @10.0.9.10 _ldap._tcp.ad.shop.test SRV
cat /etc/dnsmasq.d/ad.conf
sudo sed -i 's/10\.0\.9\.11/10.0.9.10/' /etc/dnsmasq.d/ad.conf
sudo systemctl restart dnsmasq
dig +short _ldap._tcp.ad.shop.test SRV
dig +short -x 10.0.9.10

# 2. The machine's own account. With names fixed, a person can get a ticket
#    (kinit alice works now) but SSSD stays offline: its log says "Failed to
#    initialize credentials using keytab ... Preauthentication failed". The
#    keys in /etc/krb5.keytab no longer match the computer account's
#    password on dc1, so the machine can't prove who it is, and without that
#    it can't look anyone up. Nothing a person does fixes that: the machine
#    has to be joined again.
echo 'Alice-Pass-1' | kinit alice@AD.SHOP.TEST
journalctl -u sssd --no-pager | grep -i keytab | tail -n 3
sudo kinit -k 'LAB$@AD.SHOP.TEST' || true
sudo realm leave
echo 'Shop-Admin-1' | sudo realm join -U Administrator ad.shop.test
#    Joining again writes a fresh SSSD configuration, which lets every
#    domain account in. Put the rule back.
sudo realm permit -g linux-admins@ad.shop.test

# 3. SSH. Now the domain answers, and alice is still refused: sshd's log
#    says she is "not allowed because none of user's groups are listed in
#    AllowGroups". A hardening change listed only the local group. Add the
#    domain group to the list; keep the restriction, and load it.
journalctl -u ssh --no-pager | grep -i 'not allowed' | tail -n 2
grep -r AllowGroups /etc/ssh/sshd_config /etc/ssh/sshd_config.d/
printf '# Only these groups may log in over SSH.\nAllowGroups ssh-users linux-admins@ad.shop.test\n' | sudo tee /etc/ssh/sshd_config.d/60-access.conf > /dev/null
sudo sshd -t
sudo systemctl try-reload-or-restart ssh

realm list
id alice@ad.shop.test
