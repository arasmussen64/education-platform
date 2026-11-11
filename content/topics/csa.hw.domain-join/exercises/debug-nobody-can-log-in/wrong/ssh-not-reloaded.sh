# Wrong: the SSH group list is corrected in its file, and the running SSH
# server is never told to read it again, so it goes on refusing alice and
# carol with the old list until something restarts it.
sudo sed -i 's/10\.0\.9\.11/10.0.9.10/' /etc/dnsmasq.d/ad.conf
sudo systemctl restart dnsmasq
sudo realm leave
echo 'Shop-Admin-1' | sudo realm join -U Administrator ad.shop.test
sudo realm permit -g linux-admins@ad.shop.test
# The running server has to have read the old list for this to be the
# mistake it is: one login attempt starts it, as Monday's did.
sshpass -p 'Alice-Pass-1' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o PreferredAuthentications=password -o PubkeyAuthentication=no -o NumberOfPasswordPrompts=1 -o LogLevel=ERROR alice@ad.shop.test@localhost true || true
printf '# Only these groups may log in over SSH.\nAllowGroups ssh-users linux-admins@ad.shop.test\n' | sudo tee /etc/ssh/sshd_config.d/60-access.conf > /dev/null
sudo sshd -t
