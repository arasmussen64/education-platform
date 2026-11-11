# Wrong: who may log in is limited in SSH's settings (AllowGroups, the
# hardening topic's way) instead of in SSSD's own access rule. bob is
# refused over SSH, and let in by every other way into the machine: the
# console, su, a cron job, anything else that asks SSSD.
printf 'server=/ad.shop.test/10.0.9.10\nserver=/9.0.10.in-addr.arpa/10.0.9.10\n' | sudo tee /etc/dnsmasq.d/ad.conf > /dev/null
sudo systemctl restart dnsmasq
echo 'Shop-Admin-1' | sudo realm join -U Administrator ad.shop.test
sudo pam-auth-update --enable mkhomedir
printf '# Only the domain group may log in over SSH.\nAllowGroups linux-admins@ad.shop.test\n' | sudo tee /etc/ssh/sshd_config.d/60-access.conf > /dev/null
sudo sshd -t
sudo systemctl try-reload-or-restart ssh
