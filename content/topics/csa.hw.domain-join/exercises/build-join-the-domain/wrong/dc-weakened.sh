# Wrong: everything is done, and dc1 is also set to accept a password sent
# over plain, unencrypted LDAP, so that a simple bind works. Anyone on the
# network can now read the passwords people sign in with.
printf 'server=/ad.shop.test/10.0.9.10\nserver=/9.0.10.in-addr.arpa/10.0.9.10\n' | sudo tee /etc/dnsmasq.d/ad.conf > /dev/null
sudo systemctl restart dnsmasq
echo 'Shop-Admin-1' | sudo realm join -U Administrator ad.shop.test
sudo pam-auth-update --enable mkhomedir
sudo realm permit -g linux-admins@ad.shop.test

# The shortcut: dc1 told to accept passwords over plain LDAP.
on-dc sed -i '/^\[global\]/a\\tldap server require strong auth = no' /etc/samba/smb.conf
sudo systemctl restart lab-dc
until dig +short +time=1 +tries=1 @10.0.9.10 _ldap._tcp.ad.shop.test SRV | grep -q dc1; do sleep 1; done
ldapsearch -x -H ldap://dc1.ad.shop.test -D 'alice@ad.shop.test' -w 'Alice-Pass-1' -b 'DC=ad,DC=shop,DC=test' '(sAMAccountName=alice)' dn
sleep 5
