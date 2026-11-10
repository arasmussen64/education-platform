# Wrong: the drop-in was written to the learner's home instead of the
# sshd_config.d folder, so sshd never reads it and nothing changes.
mkdir -p ~/sshd_config.d
printf 'PasswordAuthentication no\nPermitRootLogin no\n' > ~/sshd_config.d/90-hardening.conf
sudo sshd -t
