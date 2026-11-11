# Wrong: the one member there is today is permitted by name instead of the
# group, so whoever joins desk-admins next month is refused.
# 1. The domain. Provisioning creates the directory, the Kerberos keys and
#    the domain's DNS zone on dc1. Then start dc1's service, now and at boot.
on-dc samba-tool domain provision --quiet --realm=AD.CLINIC.TEST --domain=CLINIC \
  --server-role=dc --dns-backend=SAMBA_INTERNAL --adminpass='Clinic-Admin-1' \
  --option='dns forwarder = 10.0.9.1'
sudo systemctl enable --now dc1
# dc1's name server answers a moment after its service says it's ready.
until dig +short +time=1 +tries=1 @10.0.9.10 _ldap._tcp.ad.clinic.test SRV | grep -q dc1; do sleep 1; done
dig +short @10.0.9.10 _kerberos._tcp.ad.clinic.test SRV

# 2. dc1's address gets a name: a reverse zone for 10.0.9.x, and a PTR
#    record for .10 in it.
on-dc samba-tool dns zonecreate dc1 9.0.10.in-addr.arpa -U Administrator --password='Clinic-Admin-1'
on-dc samba-tool dns add dc1 9.0.10.in-addr.arpa 10 PTR dc1.ad.clinic.test -U Administrator --password='Clinic-Admin-1'

# 3. The password rules, for the whole domain.
on-dc samba-tool domain passwordsettings set --min-pwd-length=12 --account-lockout-threshold=10

# 4. The people: a unit, two users in it, and a group with one of them.
on-dc samba-tool ou create 'OU=Front-Desk'
on-dc samba-tool user create noor 'Noor-Pass-1234567' --userou='OU=Front-Desk'
on-dc samba-tool user create omar 'Omar-Pass-1234567' --userou='OU=Front-Desk'
on-dc samba-tool group add desk-admins --groupou='OU=Front-Desk'
on-dc samba-tool group addmembers desk-admins noor

# 5. A Group Policy object, linked to the unit. A link names the object by
#    its GUID, the identifier in braces that gpo create prints.
guid=$(on-dc samba-tool gpo create 'Desk baseline' -U Administrator --password='Clinic-Admin-1' | grep -o '{.*}')
on-dc samba-tool gpo setlink 'OU=Front-Desk,DC=ad,DC=clinic,DC=test' "$guid" -U Administrator --password='Clinic-Admin-1'

# 6. lab finds the domain: forward its zone, and the reverse zone, from the
#    site's resolver to dc1 (conditional forwarders), in a file the resolver
#    reads at every start.
printf 'server=/ad.clinic.test/10.0.9.10\nserver=/9.0.10.in-addr.arpa/10.0.9.10\n' | sudo tee /etc/dnsmasq.d/ad.conf > /dev/null
sudo systemctl restart dnsmasq
dig +short _ldap._tcp.ad.clinic.test SRV
dig +short -x 10.0.9.10

# 7. Join (realm writes SSSD's settings and starts SSSD, now and at every
#    boot), a home directory made at each person's first login, and only
#    the group: SSSD's own access rule, which every way in asks.
realm discover ad.clinic.test
echo 'Clinic-Admin-1' | sudo realm join -U Administrator ad.clinic.test
sudo pam-auth-update --enable mkhomedir
sudo realm permit noor@ad.clinic.test

# 8. Look.
realm list
id noor@ad.clinic.test
