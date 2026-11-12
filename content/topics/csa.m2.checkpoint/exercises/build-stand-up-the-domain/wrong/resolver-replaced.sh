# Wrong: lab stops asking the site's resolver and asks dc1 directly, with
# /etc/resolv.conf rewritten by hand. Everything answers today, but the
# lab's network writes resolv.conf afresh at every boot, as a cloud
# network's DHCP does, so after the next reboot lab can't find the domain.
# 1. The domain. Provisioning creates the directory, the Kerberos keys and
#    the domain's DNS zone on dc1. Then start dc1's service, now and at boot.
on-dc samba-tool domain provision --quiet --realm=AD.SHOP.TEST --domain=SHOP \
  --server-role=dc --dns-backend=SAMBA_INTERNAL --adminpass='Shop-Admin-1' \
  --option='dns forwarder = 10.0.9.1'
sudo systemctl enable --now dc1
# dc1's name server and its directory (LDAP, port 389) answer a moment
# after its service says it's ready; on a busy machine, many moments.
until dig +short +time=1 +tries=1 @10.0.9.10 _ldap._tcp.ad.shop.test SRV | grep -q dc1 && nc -z -w 1 10.0.9.10 389; do sleep 1; done
dig +short @10.0.9.10 _kerberos._tcp.ad.shop.test SRV

# 2. dc1's address gets a name: a reverse zone for 10.0.9.x, and a PTR
#    record for .10 in it.
on-dc samba-tool dns zonecreate dc1 9.0.10.in-addr.arpa -U Administrator --password='Shop-Admin-1'
on-dc samba-tool dns add dc1 9.0.10.in-addr.arpa 10 PTR dc1.ad.shop.test -U Administrator --password='Shop-Admin-1'

# 3. The password rules, for the whole domain.
on-dc samba-tool domain passwordsettings set --min-pwd-length=14 --account-lockout-threshold=5

# 4. The people: a unit, two users in it, and a group with one of them.
on-dc samba-tool ou create 'OU=Shop'
on-dc samba-tool user create dana 'Dana-Pass-12345' --userou='OU=Shop'
on-dc samba-tool user create erin 'Erin-Pass-12345' --userou='OU=Shop'
on-dc samba-tool group add linux-admins --groupou='OU=Shop'
on-dc samba-tool group addmembers linux-admins dana

# 5. A Group Policy object, linked to the unit. A link names the object by
#    its GUID, the identifier in braces that gpo create prints.
guid=$(on-dc samba-tool gpo create 'Server baseline' -U Administrator --password='Shop-Admin-1' | grep -o '{.*}')
on-dc samba-tool gpo setlink 'OU=Shop,DC=ad,DC=shop,DC=test' "$guid" -U Administrator --password='Shop-Admin-1'

# 6. lab finds the domain: forward its zone, and the reverse zone, from the
#    site's resolver to dc1 (conditional forwarders), in a file the resolver
#    reads at every start.
sudo sh -c 'echo nameserver 10.0.9.10 > /etc/resolv.conf'
dig +short _ldap._tcp.ad.shop.test SRV
dig +short -x 10.0.9.10

# 7. Join (realm writes SSSD's settings and starts SSSD, now and at every
#    boot), a home directory made at each person's first login, and only
#    the group: SSSD's own access rule, which every way in asks.
realm discover ad.shop.test
echo 'Shop-Admin-1' | sudo realm join -U Administrator ad.shop.test
sudo pam-auth-update --enable mkhomedir
sudo realm permit -g linux-admins@ad.shop.test

# 8. Look.
realm list
id dana@ad.shop.test
