# Wrong: the number and the key setting are fixed, but AllowGroups still
# names a group ben isn't in, so he's still locked out.
printf 'PasswordAuthentication no\nPermitRootLogin no\nAllowGroups admins\nMaxAuthTries 3\nPubkeyAuthentication yes\n' | sudo tee /etc/ssh/sshd_config.d/90-hardening.conf
sudo sshd -t
