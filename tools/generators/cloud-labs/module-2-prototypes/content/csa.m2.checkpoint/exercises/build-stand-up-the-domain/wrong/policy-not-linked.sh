# Wrong: the Group Policy object exists but is linked to nothing, so it applies to nobody.
# 1. The domain. Provisioning creates the directory database, the Kerberos
#    keys, the DNS zones and the SYSVOL share on dc1; it takes about half a
#    minute. Then start dc1's service and have it start at boot.
on-dc samba-tool domain provision --realm=AD.SHOP.TEST --domain=SHOP \
  --server-role=dc --dns-backend=SAMBA_INTERNAL --adminpass='Shop-Admin-1' \
  --option='dns forwarder = 10.0.9.1' > /dev/null 2>&1
sudo systemctl enable --now dc1
# dc1's name server comes up a moment after the service says it's ready.
until dig +short +time=1 +tries=1 @10.0.9.10 _ldap._tcp.ad.shop.test SRV | grep -q dc1; do sleep 1; done
dig +short @10.0.9.10 _kerberos._tcp.ad.shop.test SRV

# 2. The password rules first, so the people's passwords are held to them.
on-dc samba-tool domain passwordsettings set --min-pwd-length=14 --account-lockout-threshold=5

# 3. The people: a unit, two users in it, a group with one of them.
on-dc samba-tool ou create 'OU=Shop'
on-dc samba-tool user create dana 'Dana-Pass-12345' --userou='OU=Shop'
on-dc samba-tool user create erin 'Erin-Pass-12345' --userou='OU=Shop'
on-dc samba-tool group add linux-admins --groupou='OU=Shop'
on-dc samba-tool group addmembers linux-admins dana

# 4. A Group Policy object, linked to the unit. A link names the object by
#    its GUID, which gpo create prints.
gpo=$(on-dc samba-tool gpo create 'Server baseline' -U Administrator --password='Shop-Admin-1' 2>/dev/null | grep -o '{[0-9A-F-]*}')

# 5. lab finds the domain: forward its zone from the site's resolver to dc1.
printf 'server=/ad.shop.test/10.0.9.10\nserver=/9.0.10.in-addr.arpa/10.0.9.10\n' | sudo tee /etc/dnsmasq.d/ad.conf > /dev/null
sudo systemctl restart dnsmasq
realm discover ad.shop.test

# 6. Join, home directories, and only the group.
echo 'Shop-Admin-1' | sudo realm join -U Administrator ad.shop.test
sudo pam-auth-update --enable mkhomedir
sudo realm permit -g linux-admins@ad.shop.test
id dana@ad.shop.test
