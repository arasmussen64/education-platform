# Wrong: all three faults are fixed, and dc1 is also set to accept a
# password sent over plain, unencrypted LDAP, "to rule it out" while
# looking. Anyone on the network can now read the passwords people sign in
# with.
sudo sed -i 's/10\.0\.9\.11/10.0.9.10/' /etc/dnsmasq.d/ad.conf
sudo systemctl restart dnsmasq
on-dc sed -i '/^\[global\]/a\\tldap server require strong auth = no' /etc/samba/smb.conf
sudo systemctl restart lab-dc
until dig +short +time=1 +tries=1 @10.0.9.10 _ldap._tcp.ad.shop.test SRV | grep -q dc1; do sleep 1; done
sudo realm leave
echo 'Shop-Admin-1' | sudo realm join -U Administrator ad.shop.test
sudo realm permit -g linux-admins@ad.shop.test
printf '# Only these groups may log in over SSH.\nAllowGroups ssh-users linux-admins@ad.shop.test\n' | sudo tee /etc/ssh/sshd_config.d/60-access.conf > /dev/null
sudo systemctl try-reload-or-restart ssh
sleep 5
