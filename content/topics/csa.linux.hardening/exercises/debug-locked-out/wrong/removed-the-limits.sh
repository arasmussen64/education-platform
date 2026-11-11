# Wrong: the two lines that got in the way are deleted, not corrected. ben
# gets in, but nothing limits who may log in any more, and the try limit is
# back at the default of six.
printf 'PasswordAuthentication no\nPermitRootLogin no\nPubkeyAuthentication yes\n' | sudo tee /etc/ssh/sshd_config.d/90-hardening.conf
sudo sshd -t
sudo systemctl restart ssh
