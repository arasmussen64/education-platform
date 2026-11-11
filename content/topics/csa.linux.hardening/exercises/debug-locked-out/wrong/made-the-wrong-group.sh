# Wrong: the number and the key setting are fixed, but the group in
# AllowGroups is left as it was, and ben is put in a new group of that name
# to match. He gets in, but the rule the hardening was meant to set, only
# ssh-users, is not the rule the server has.
printf 'PasswordAuthentication no\nPermitRootLogin no\nAllowGroups admins\nMaxAuthTries 3\nPubkeyAuthentication yes\n' | sudo tee /etc/ssh/sshd_config.d/90-hardening.conf
sudo groupadd admins
sudo usermod -aG admins ben
sudo sshd -t
sudo systemctl restart ssh
